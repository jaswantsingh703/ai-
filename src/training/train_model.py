import os
import logging
import torch
from src.utils.config import Config

# Check if transformers is available
try:
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("transformers module not available. Model training will be limited.")

class TrainModel:
    """
    Class for training and fine-tuning language models.
    """
    
    def __init__(self, model_name=None, dataset_name=None, save_path=None):
        """
        Initialize the model trainer.
        
        Args:
            model_name (str): Base model name
            dataset_name (str): Dataset name
            save_path (str): Path to save the trained model
        """
        self.model_name = model_name or "gpt2"
        self.dataset_name = dataset_name or "wikitext"
        self.save_path = save_path or os.path.join(Config.get("models_dir", "models"), "trained_model")
        
        # Create save directory if it doesn't exist
        os.makedirs(self.save_path, exist_ok=True)
        
        # Initialize model and tokenizer if transformers is available
        if TRANSFORMERS_AVAILABLE:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
                logging.info(f"Model and tokenizer initialized: {self.model_name}")
            except Exception as e:
                logging.error(f"Error initializing model and tokenizer: {e}")
                self.tokenizer = None
                self.model = None
        else:
            self.tokenizer = None
            self.model = None

    def load_data(self, dataset=None, split="train"):
        """
        Load dataset for training.
        
        Args:
            dataset: Dataset to use (if already loaded)
            split (str): Dataset split to use
            
        Returns:
            object: Loaded dataset or None if unavailable
        """
        # Use provided dataset if available
        if dataset is not None:
            return dataset
            
        # Otherwise, import and load dataset
        if TRANSFORMERS_AVAILABLE:
            try:
                from datasets import load_dataset
                logging.info(f"Loading dataset: {self.dataset_name} ({split})")
                dataset = load_dataset(self.dataset_name, split=split)
                return dataset
            except Exception as e:
                logging.error(f"Error loading dataset: {e}")
                return None
        else:
            logging.error("Cannot load dataset: transformers/datasets not available")
            return None

    def tokenize_function(self, examples):
        """
        Tokenize text examples for training.
        
        Args:
            examples (dict): Examples to tokenize
            
        Returns:
            dict: Tokenized examples
        """
        if not self.tokenizer:
            logging.error("Tokenizer not initialized")
            return examples
            
        try:
            return self.tokenizer(
                examples["text"],
                padding="max_length",
                truncation=True,
                max_length=512
            )
        except Exception as e:
            logging.error(f"Error tokenizing examples: {e}")
            return examples

    def train(self, dataset=None, epochs=3, batch_size=8, learning_rate=5e-5):
        """
        Train the language model.
        
        Args:
            dataset: Dataset for training
            epochs (int): Number of training epochs
            batch_size (int): Batch size for training
            learning_rate (float): Learning rate
            
        Returns:
            bool: Success status
        """
        if not TRANSFORMERS_AVAILABLE:
            logging.error("Cannot train model: transformers not available")
            return False
            
        if not self.model or not self.tokenizer:
            logging.error("Model or tokenizer not initialized")
            return False
            
        # Load dataset if not provided
        if dataset is None:
            dataset = self.load_data()
            if dataset is None:
                return False
                
        try:
            # Tokenize dataset
            logging.info("Tokenizing dataset")
            tokenized_dataset = dataset.map(
                self.tokenize_function,
                batched=True,
                remove_columns=["text"]
            )
            
            # Set up training arguments
            training_args = TrainingArguments(
                output_dir=self.save_path,
                evaluation_strategy="epoch",
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                num_train_epochs=epochs,
                learning_rate=learning_rate,
                weight_decay=0.01,
                save_steps=500,
                save_total_limit=2,
                logging_dir=os.path.join(self.save_path, "logs"),
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=tokenized_dataset,
            )
            
            # Start training
            logging.info(f"Starting model training for {epochs} epochs")
            trainer.train()
            
            # Save model
            self.save_model()
            
            return True
            
        except Exception as e:
            logging.error(f"Error during training: {e}")
            return False

    def save_model(self):
        """
        Save the trained model and tokenizer.
        
        Returns:
            bool: Success status
        """
        if not self.model or not self.tokenizer:
            logging.error("Model or tokenizer not initialized")
            return False
            
        try:
            logging.info(f"Saving model to {self.save_path}")
            
            # Save model and tokenizer
            self.model.save_pretrained(self.save_path)
            self.tokenizer.save_pretrained(self.save_path)
            
            return True
        except Exception as e:
            logging.error(f"Error saving model: {e}")
            return False

    def generate_text(self, prompt, max_length=100):
        """
        Generate text using the trained model.
        
        Args:
            prompt (str): Text prompt for generation
            max_length (int): Maximum length of generated text
            
        Returns:
            str: Generated text
        """
        if not self.model or not self.tokenizer:
            return "Model or tokenizer not initialized"
            
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            # Generate text
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.9
                )
                
            # Decode and return generated text
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
        except Exception as e:
            logging.error(f"Error generating text: {e}")
            return f"Error generating text: {str(e)}"