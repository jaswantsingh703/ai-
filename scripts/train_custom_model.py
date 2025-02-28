#!/usr/bin/env python3
"""
Custom model training script for Jarvis AI.
Trains a language model on user data for improved personalization.
"""

import os
import sys
import argparse
import logging
import torch
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.training.dataset_loader import DatasetLoader
from src.training.train_model import TrainModel
from src.utils.config import Config
from src.utils.helper_functions import setup_logging

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Train a custom model for Jarvis AI")
    
    parser.add_argument(
        "--model",
        type=str,
        choices=["gpt2", "gpt2-medium", "distilgpt2", "bert-base-uncased"],
        default="gpt2",
        help="Base model to fine-tune"
    )
    
    parser.add_argument(
        "--data_dir",
        type=str,
        default="data/training_data",
        help="Directory containing training data files"
    )
    
    parser.add_argument(
        "--output_dir",
        type=str,
        default="models/custom_trained",
        help="Directory to save the trained model"
    )
    
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs"
    )
    
    parser.add_argument(
        "--batch_size",
        type=int,
        default=4,
        help="Training batch size"
    )
    
    parser.add_argument(
        "--learning_rate",
        type=float,
        default=5e-5,
        help="Learning rate"
    )
    
    parser.add_argument(
        "--max_length",
        type=int,
        default=128,
        help="Maximum token length for inputs"
    )
    
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="Hugging Face dataset name (optional)"
    )
    
    parser.add_argument(
        "--log_file",
        type=str,
        default="logs/training.log",
        help="Log file path"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

def prepare_data(args, dataset_loader):
    """Prepare the training dataset."""
    if args.dataset:
        # Load from Hugging Face
        logging.info(f"Loading dataset from Hugging Face: {args.dataset}")
        dataset = dataset_loader.load_huggingface_dataset(args.dataset)
        if dataset is None:
            logging.error(f"Failed to load dataset: {args.dataset}")
            return None
    else:
        # Look for data files
        if not os.path.exists(args.data_dir):
            logging.error(f"Data directory not found: {args.data_dir}")
            return None
            
        # Try to load CSV dataset
        csv_files = [f for f in os.listdir(args.data_dir) if f.endswith('.csv')]
        if csv_files:
            logging.info(f"Loading CSV dataset: {csv_files[0]}")
            dataset = dataset_loader.load_csv_dataset(os.path.join(args.data_dir, csv_files[0]))
        else:
            logging.error("No CSV files found in data directory")
            return None
    
    # Preprocess the dataset
    dataset = dataset_loader.preprocess_dataset(dataset)
    logging.info(f"Dataset prepared with {len(dataset)} examples")
    
    return dataset

def train_model(args, dataset):
    """Train the model on the prepared dataset."""
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Create a timestamp for the model
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_save_path = os.path.join(args.output_dir, f"{args.model}_{timestamp}")
    
    # Initialize the model trainer
    logging.info(f"Initializing trainer with model: {args.model}")
    trainer = TrainModel(
        model_name=args.model,
        save_path=model_save_path
    )
    
    # Check if model was initialized successfully
    if trainer.model is None or trainer.tokenizer is None:
        logging.error("Failed to initialize model or tokenizer")
        return False
    
    # Train the model
    logging.info(f"Starting training for {args.epochs} epochs")
    success = trainer.train(
        dataset=dataset,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate
    )
    
    if success:
        logging.info(f"Training completed successfully. Model saved to {model_save_path}")
        
        # Update config to point to the new model
        Config.set("custom_model_path", model_save_path)
        Config.set("custom_model_type", args.model)
        
        # Generate a sample from the trained model
        sample_prompt = "The AI assistant can help with"
        sample_output = trainer.generate_text(sample_prompt, max_length=100)
        
        logging.info(f"Sample generation:\nPrompt: {sample_prompt}\nOutput: {sample_output}")
        return True
    else:
        logging.error("Training failed")
        return False

def main():
    """Main function to run the training process."""
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.log_file)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Log hardware info
    logging.info(f"PyTorch version: {torch.__version__}")
    logging.info(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logging.info(f"CUDA device: {torch.cuda.get_device_name(0)}")
    
    # Initialize dataset loader
    logging.info("Initializing dataset loader")
    dataset_loader = DatasetLoader(data_dir=args.data_dir)
    
    # Prepare data
    logging.info("Preparing training data")
    dataset = prepare_data(args, dataset_loader)
    if dataset is None:
        logging.error("Failed to prepare dataset. Exiting.")
        return 1
    
    # Train model
    logging.info("Starting model training")
    success = train_model(args, dataset)
    
    if success:
        logging.info("Training process completed successfully")
        return 0
    else:
        logging.error("Training process failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())