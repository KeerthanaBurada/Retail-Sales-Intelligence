"""Generates actionable business insights from sales analytics data.

Combines outputs from AnalyticsService to identify patterns, opportunities,
and risks across geography, product, customer, and trend dimensions.
"""

from services.analytics_service import AnalyticsService


class InsightsService:

    @staticmethod
    def generate_insights(db, dataset_id=None) -> list[dict]:
        """Analyze sales data and return a list of categorized business insights.

        Each insight includes a category, title, description, key metric,
        and a concrete recommendation.
        """
        insights = []

        # --- 1. Regional performance insights ---
        regions = AnalyticsService.get_revenue_by_region(db, dataset_id)
        if regions:
            best = max(regions, key=lambda r: r['revenue'])
            worst = min(regions, key=lambda r: r['revenue'])

            insights.append({
                'category': 'geography',
                'title': 'Regional Champion',
                'description': (
                    f"The {best['region']} region leads with "
                    f"${best['revenue']:,.0f} in revenue."
                ),
                'metric': f"${best['revenue']:,.0f} revenue",
                'recommendation': (
                    'Maintain market position with continued investment '
                    'and expansion.'
                ),
            })

            insights.append({
                'category': 'geography',
                'title': 'Regional Growth Opportunity',
                'description': (
                    f"The {worst['region']} region contributes only "
                    f"${worst['revenue']:,.0f} in revenue. Consider targeted "
                    f"marketing campaigns or partner with local retailers to "
                    f"boost regional presence."
                ),
                'metric': f"${worst['revenue']:,.0f} revenue",
                'recommendation': (
                    'Consider targeted marketing campaigns or partner with '
                    'local retailers to boost regional presence.'
                ),
            })

        # --- 2. Category performance insights ---
        categories = AnalyticsService.get_category_performance(db, dataset_id)
        if categories:
            best_cat = max(categories, key=lambda c: c['revenue'])
            worst_cat = min(categories, key=lambda c: c['revenue'])

            insights.append({
                'category': 'product',
                'title': 'Star Category',
                'description': (
                    f"{best_cat['category']} leads all categories with "
                    f"${best_cat['revenue']:,.0f} in revenue and a "
                    f"{best_cat['profit_margin']:.1f}% profit margin."
                ),
                'metric': f"${best_cat['revenue']:,.0f} revenue",
                'recommendation': (
                    'Expand product range and increase marketing budget '
                    'for this high-performing category.'
                ),
            })

            insights.append({
                'category': 'product',
                'title': 'Underperforming Category',
                'description': (
                    f"{worst_cat['category']} generated only "
                    f"${worst_cat['revenue']:,.0f} in revenue."
                ),
                'metric': f"${worst_cat['revenue']:,.0f} revenue",
                'recommendation': (
                    'Review product assortment, pricing strategy, and '
                    'consider promotional campaigns to boost performance.'
                ),
            })

        # --- 3. Revenue trend insight (needs at least 6 data points) ---
        trend = AnalyticsService.get_sales_trend(db, dataset_id)
        if len(trend) >= 6:
            recent_3 = sum(t['revenue'] for t in trend[-3:])
            prev_3 = sum(t['revenue'] for t in trend[-6:-3])

            if prev_3 > 0:
                growth = (recent_3 - prev_3) / prev_3 * 100
            else:
                growth = 0.0

            if growth > 0:
                desc = (
                    f"Revenue grew {growth:.1f}% over the last quarter "
                    f"compared to the previous quarter."
                )
                rec = 'Capitalize on growth momentum with strategic investments.'
            else:
                desc = (
                    f"Revenue declined {abs(growth):.1f}% over the last quarter."
                )
                rec = (
                    'Investigate declining categories and regions. '
                    'Consider promotional offers.'
                )

            insights.append({
                'category': 'trend',
                'title': 'Revenue Trend',
                'description': desc,
                'metric': f'{growth:+.1f}% growth',
                'recommendation': rec,
            })

        # --- 4. Top revenue product ---
        top_products = AnalyticsService.get_top_products(db, dataset_id, limit=1)
        if top_products:
            product = top_products[0]
            insights.append({
                'category': 'product',
                'title': 'Top Revenue Product',
                'description': (
                    f"\"{product['product_name']}\" is the highest-revenue "
                    f"product with ${product['revenue']:,.0f} in sales."
                ),
                'metric': f"${product['revenue']:,.0f}",
                'recommendation': (
                    'Ensure adequate inventory and consider bundling '
                    'with complementary products.'
                ),
            })

        # --- 5. Margin alert for categories with thin margins ---
        if categories:
            lowest_margin_cat = min(categories, key=lambda c: c['profit_margin'])
            if lowest_margin_cat['profit_margin'] < 15:
                insights.append({
                    'category': 'pricing',
                    'title': 'Margin Alert',
                    'description': (
                        f"{lowest_margin_cat['category']} has a thin profit "
                        f"margin of {lowest_margin_cat['profit_margin']:.1f}%."
                    ),
                    'metric': f"{lowest_margin_cat['profit_margin']:.1f}% margin",
                    'recommendation': (
                        'Review discount policies and negotiate better '
                        'supplier pricing for this category.'
                    ),
                })

        # --- 6. High-value customer segment ---
        segments = AnalyticsService.get_customer_segments(db, dataset_id)
        if segments:
            best_seg = max(segments, key=lambda s: s['avg_order_value'])
            insights.append({
                'category': 'customer',
                'title': 'High-Value Customer Segment',
                'description': (
                    f"The {best_seg['segment']} segment has the highest "
                    f"average order value of ${best_seg['avg_order_value']:,.0f}."
                ),
                'metric': f"${best_seg['avg_order_value']:,.0f} avg order",
                'recommendation': (
                    'Develop loyalty programs and premium offerings '
                    'tailored to this segment.'
                ),
            })

        # --- 7. Seasonal pattern by quarter ---
        monthly = AnalyticsService.get_monthly_revenue(db, dataset_id)
        if monthly:
            quarterly_revenue = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
            for entry in monthly:
                # period format is "YYYY-MM"
                month = int(entry['period'].split('-')[1])
                quarter = (month - 1) // 3 + 1
                quarterly_revenue[quarter] += entry['revenue']

            best_q = max(quarterly_revenue, key=quarterly_revenue.get)
            best_q_rev = quarterly_revenue[best_q]

            insights.append({
                'category': 'trend',
                'title': 'Seasonal Pattern',
                'description': (
                    f"Q{best_q} is the strongest quarter with "
                    f"${best_q_rev:,.0f} in total revenue."
                ),
                'metric': f"Q{best_q}: ${best_q_rev:,.0f}",
                'recommendation': (
                    f"Prepare inventory and marketing campaigns ahead of "
                    f"Q{best_q} to maximize seasonal demand."
                ),
            })

        return insights
