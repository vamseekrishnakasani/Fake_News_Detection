import os
from dataclasses import dataclass, field

@dataclass
class ModelConfig:
    """
    Configuration for the model architecture and training hyperparameters.
    """
    model_name: str = 'roberta-base'  # Name of the HuggingFace model
    max_length: int = 512             # Max token length for input
    num_labels: int = 2               # Number of output labels (binary classification)
    batch_size: int = 8               # Batch size for training
    num_epochs: int = 3               # Number of training epochs
    learning_rate: float = 2e-5       # Learning rate
    warmup_steps: int = 500           # Warmup steps for scheduler
    weight_decay: float = 0.01        # Weight decay for optimizer

@dataclass
class TrainingConfig:
    """
    Configuration for training process and output directories.
    """
    output_dir: str = './fake_news_model'  # Directory to save trained model
    logging_dir: str = './logs'            # Directory for logs
    logging_steps: int = 100               # Steps between logging
    eval_steps: int = 500                  # Steps between evaluation
    save_steps: int = 500                  # Steps between checkpoints

@dataclass
class APIConfig:
    """
    Configuration for API server settings.
    """
    host: str = "0.0.0.0"                 # Host for API
    port: int = 8000                       # Port for API
    model_path: str = './fake_news_model'  # Path to trained model

@dataclass
class Config:
    """
    Main configuration class that aggregates all sub-configurations.
    Can be loaded from environment variables for flexibility.
    """
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    api: APIConfig = field(default_factory=APIConfig)

    @classmethod
    def from_env(cls):
        """
        Create config from environment variables, falling back to defaults.
        Returns:
            Config: An instance of the Config class with all settings.
        """
        return cls(
            model=ModelConfig(
                model_name=os.getenv('MODEL_NAME', 'roberta-base'),
                max_length=int(os.getenv('MAX_LENGTH', 512)),
                num_labels=int(os.getenv('NUM_LABELS', 2)),
                batch_size=int(os.getenv('BATCH_SIZE', 8)),
                num_epochs=int(os.getenv('NUM_EPOCHS', 3)),
                learning_rate=float(os.getenv('LEARNING_RATE', 2e-5)),
                warmup_steps=int(os.getenv('WARMUP_STEPS', 500)),
                weight_decay=float(os.getenv('WEIGHT_DECAY', 0.01))
            ),
            training=TrainingConfig(
                output_dir=os.getenv('OUTPUT_DIR', './fake_news_model'),
                logging_dir=os.getenv('LOGGING_DIR', './logs'),
                logging_steps=int(os.getenv('LOGGING_STEPS', 100)),
                eval_steps=int(os.getenv('EVAL_STEPS', 500)),
                save_steps=int(os.getenv('SAVE_STEPS', 500))
            ),
            api=APIConfig(
                host=os.getenv('API_HOST', "0.0.0.0"),
                port=int(os.getenv('API_PORT', 8000)),
                model_path=os.getenv('MODEL_PATH', './fake_news_model')
            )
        ) 