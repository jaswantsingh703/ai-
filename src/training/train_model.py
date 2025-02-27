import torch
import transformers
import logging
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

class TrainModel:
    """
    Class for training AI models using Transformers and PyTorch.
    """
    
    def __init__(self, model_name="gpt2", dataset_name="wikitext", save_path="trained_model"):
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.save_path = save_path
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        logging.info("Model and tokenizer initialized.")

    def load_data(self, split="train"):
        """
        Loads dataset for training.
        :param split: Dataset split (train, test, validation)
        """
        logging.info(f"Loading dataset: {self.dataset_name} ({split})")
        dataset = load_dataset(self.dataset_name, split=split)
        return dataset

    def tokenize_function(self, examples):
        """
        Tokenizes input dataset examples.
        """
        return self.tokenizer(examples["text"], padding="max_length", truncation=True)

    def train(self, epochs=3, batch_size=8):
        """
        Trains the AI model.
        :param epochs: Number of training epochs.
        :param batch_size: Batch size for training.
        """
        dataset = self.load_data()
        tokenized_datasets = dataset.map(self.tokenize_function, batched=True)

        training_args = TrainingArguments(
            output_dir=self.save_path,
            evaluation_strategy="epoch",
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            num_train_epochs=epochs,
            save_steps=500,
            save_total_limit=2,
            logging_dir="logs",
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_datasets,
        )

        logging.info("Starting model training...")
        trainer.train()
        logging.info("Training completed. Model saved.")

    def save_model(self):
        """
        Saves the trained model and tokenizer.
        """
        self.model.save_pretrained(self.save_path)
        self.tokenizer.save_pretrained(self.save_path)
        logging.info(f"Model saved to {self.save_path}")

# Example Usage
if __name__ == "__main__":
    trainer = TrainModel()
    trainer.train(epochs=3, batch_size=8)
    trainer.save_model()
