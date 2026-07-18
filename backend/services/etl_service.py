"""
ETL Service - Extract, Transform, Load pipeline for retail sales data.

This is the data engineering core of the platform. It takes raw CSV uploads
(typically Superstore-style datasets), validates the schema, cleans messy
real-world data, and engineers features that power the analytics dashboards.

Design decisions:
- Median over mean for filling missing numerics: median is robust to outliers
  (e.g., a single $50k bulk order won't skew imputed values).
- Negative/zero sales rows are dropped: they usually represent returns or
  data entry errors and would distort revenue metrics.
- Column name standardization handles the most common variations seen when
  users export from Excel, Google Sheets, or different POS systems.
"""

import pandas as pd


class ETLService:
    """Static methods for each stage of the ETL pipeline."""

    # The columns the analytics layer expects to be present
    REQUIRED_COLUMNS = [
        "Order ID",
        "Order Date",
        "Customer Name",
        "Segment",
        "City",
        "State",
        "Region",
        "Category",
        "Sub-Category",
        "Product Name",
        "Sales",
        "Quantity",
        "Discount",
        "Profit",
    ]

    # Common column-name variations mapped to the canonical names above.
    # Keys are lowercase so we can do case-insensitive matching.
    COLUMN_MAP = {
        "order_id": "Order ID",
        "order id": "Order ID",
        "sales_amount": "Sales",
        "customer": "Customer Name",
        "sub_category": "Sub-Category",
        "product": "Product Name",
        "ship_date": "Ship Date",
        "ship_mode": "Ship Mode",
        "customer_id": "Customer ID",
    }

    @staticmethod
    def validate_columns(df: pd.DataFrame, required_columns: list[str] | None = None) -> list[str]:
        """
        Check that the DataFrame contains every required column.

        Returns a list of human-readable error strings (empty list = all good).
        """
        if required_columns is None:
            required_columns = ETLService.REQUIRED_COLUMNS

        errors = []
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        return errors

    @staticmethod
    def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names so uploads from different sources land on the
        same canonical schema.

        Steps:
        1. Strip leading/trailing whitespace from column names.
        2. Map common variations (case-insensitive) to canonical names.
        """
        # Strip whitespace
        df.columns = df.columns.str.strip()

        # Build a case-insensitive lookup: lowered name -> canonical name
        rename_map = {}
        for col in df.columns:
            lower = col.lower()
            if lower in ETLService.COLUMN_MAP:
                rename_map[col] = ETLService.COLUMN_MAP[lower]

        if rename_map:
            df = df.rename(columns=rename_map)

        return df

    @staticmethod
    def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """
        Clean raw data and return (cleaned_df, stats).

        Cleaning steps:
        1. Remove exact duplicate rows (common in multi-export scenarios).
        2. Fill missing numeric values with column median (robust to outliers).
        3. Fill missing categorical values with 'Unknown'.
        4. Drop rows where Order Date is missing (can't do time-series without it).
        5. Remove rows with Sales <= 0 (returns/errors distort revenue metrics).
        6. Parse date columns and coerce numeric columns to proper types.
        """
        original_rows = len(df)
        missing_values_filled = 0

        # --- Step 1: Remove duplicates ---
        df = df.drop_duplicates()
        duplicates_removed = original_rows - len(df)

        # --- Step 2 & 3: Fill missing values ---
        numeric_cols = ["Sales", "Quantity", "Discount", "Profit"]
        for col in numeric_cols:
            if col in df.columns:
                n_missing = df[col].isna().sum()
                if n_missing > 0:
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                    missing_values_filled += n_missing

        # Categorical columns: everything that isn't numeric or a date
        categorical_cols = [
            c for c in df.columns
            if c not in numeric_cols and c not in ["Order Date", "Ship Date"]
        ]
        for col in categorical_cols:
            n_missing = df[col].isna().sum()
            if n_missing > 0:
                df[col] = df[col].fillna("Unknown")
                missing_values_filled += n_missing

        # --- Step 4: Drop rows missing Order Date ---
        before_date_drop = len(df)
        df = df.dropna(subset=["Order Date"])
        invalid_rows_removed = before_date_drop - len(df)

        # --- Step 5: Parse dates ---
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
        if "Ship Date" in df.columns:
            df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")

        # Drop rows where Order Date couldn't be parsed
        pre_coerce = len(df)
        df = df.dropna(subset=["Order Date"])
        invalid_rows_removed += pre_coerce - len(df)

        # --- Step 6: Ensure numeric types ---
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # --- Step 7: Remove non-positive sales ---
        # Sales <= 0 typically means returns or data errors
        pre_sales = len(df)
        df = df[df["Sales"] > 0]
        invalid_rows_removed += pre_sales - len(df)

        stats = {
            "original_rows": original_rows,
            "duplicates_removed": duplicates_removed,
            "missing_values_filled": missing_values_filled,
            "invalid_rows_removed": invalid_rows_removed,
            "final_rows": len(df),
        }

        return df, stats

    @staticmethod
    def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create derived columns that the analytics dashboards rely on.

        - order_month / order_year / order_day_of_week: for time-series slicing.
        - profit_margin: key profitability KPI (%).
        - processing_days: fulfillment speed indicator.
        """
        df["order_month"] = df["Order Date"].dt.month
        df["order_year"] = df["Order Date"].dt.year
        # 0 = Monday, 6 = Sunday (ISO convention)
        df["order_day_of_week"] = df["Order Date"].dt.dayofweek

        # Profit margin as a percentage; guard against division by zero
        df["profit_margin"] = df.apply(
            lambda row: round(row["Profit"] / row["Sales"] * 100, 2) if row["Sales"] > 0 else 0,
            axis=1,
        )

        # Processing days = time from order to shipment
        if "Ship Date" in df.columns:
            df["processing_days"] = (df["Ship Date"] - df["Order Date"]).dt.days
        else:
            df["processing_days"] = None

        return df

    @staticmethod
    def process_upload(file_path: str) -> dict:
        """
        End-to-end ETL pipeline for a CSV upload.

        Reads the file, standardizes columns, validates schema, cleans data,
        and engineers features. Returns a result dict with the cleaned DataFrame
        (or None if validation failed) and processing statistics.
        """
        # Read CSV - try utf-8 first, fall back to latin-1 for Excel exports
        try:
            df = pd.read_csv(file_path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin-1")

        # Standardize column names before validation
        df = ETLService.standardize_columns(df)

        # Validate that all required columns are present
        errors = ETLService.validate_columns(df)
        if errors:
            return {
                "cleaned_df": None,
                "original_rows": len(df),
                "cleaned_rows": 0,
                "validation_errors": errors,
                "stats": {},
            }

        # Clean the data
        df, stats = ETLService.clean_data(df)

        # Add derived features
        df = ETLService.engineer_features(df)

        return {
            "cleaned_df": df,
            "original_rows": stats["original_rows"],
            "cleaned_rows": len(df),
            "validation_errors": [],
            "stats": stats,
        }
