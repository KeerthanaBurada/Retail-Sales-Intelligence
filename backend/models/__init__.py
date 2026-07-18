# Import all models so Base.metadata.create_all can discover them
from models.user import User
from models.dataset import Dataset, SalesRecord
from models.forecast import ForecastResult, SavedReport
