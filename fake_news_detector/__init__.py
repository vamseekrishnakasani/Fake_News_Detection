from .utils.config import Config
from .models.dataset import FakeNewsDataset, DataLoader
from .models.trainer import ModelTrainer
from .api.app import FakeNewsAPI, run_api

__version__ = '0.1.0' 