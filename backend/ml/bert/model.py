import torch
from torch import nn
from transformers import BertTokenizer, BertForSequenceClassification, BertConfig
from transformers import AdamW, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import re

class PHIDetectionModel:
    def __init__(self, model_path=None, pretrained_model="bert-base-uncased"):
        """
        Initialize the BERT model for PHI detection
        
        Args:
            model_path (str): Path to load a fine-tuned model
            pretrained_model (str): Pretrained model to use if no fine-tuned model is provided
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self.pretrained_model = pretrained_model
        self.tokenizer = None
        self.model = None
        self.phi_categories = [
            'NAME', 'AGE', 'DATE', 'PHONE', 'EMAIL', 'ID', 'ADDRESS', 'PROFESSION',
            'LOCATION', 'HOSPITAL', 'DOCTOR', 'MEDICALRECORD', 'URL', 'HEALTHPLAN'
        ]
        
        # Load model if path is provided
        if model_path and os.path.exists(model_path):
            self._load_model(model_path)
        else:
            self._initialize_model()
    
    def _initialize_model(self):
        """
        Initialize the BERT model and tokenizer
        """
        # Load tokenizer
        self.tokenizer = BertTokenizer.from_pretrained(self.pretrained_model)
        
        # Load model configuration
        config = BertConfig.from_pretrained(
            self.pretrained_model,
            num_labels=2,  # Binary classification: PHI or not PHI
            output_attentions=False,
            output_hidden_states=False,
        )
        
        # Load model
        self.model = BertForSequenceClassification.from_pretrained(
            self.pretrained_model,
            config=config
        )
        
        # Move model to device
        self.model.to(self.device)
    
    def _load_model(self, model_path):
        """
        Load a fine-tuned model and tokenizer
        
        Args:
            model_path (str): Path to the fine-tuned model
        """
        # Load tokenizer
        tokenizer_path = os.path.join(os.path.dirname(model_path), 'tokenizer')
        if os.path.exists(tokenizer_path):
            self.tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
        else:
            self.tokenizer = BertTokenizer.from_pretrained(self.pretrained_model)
        
        # Load model
        self.model = BertForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
    
    def train(self, texts, labels, epochs=4, batch_size=16, learning_rate=2e-5, save_path=None):
        """
        Fine-tune the BERT model for PHI detection
        
        Args:
            texts (list): List of text samples
            labels (list): List of labels (1 for PHI, 0 for non-PHI)
            epochs (int): Number of training epochs
            batch_size (int): Batch size for training
            learning_rate (float): Learning rate for optimizer
            save_path (str): Path to save the fine-tuned model
            
        Returns:
            dict: Training metrics
        """
        # Split data into train and validation sets
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        
        # Tokenize data
        train_encodings = self.tokenizer(train_texts, truncation=True, padding=True, max_length=128)
        val_encodings = self.tokenizer(val_texts, truncation=True, padding=True, max_length=128)
        
        # Create PyTorch datasets
        train_dataset = PHIDataset(train_encodings, train_labels)
        val_dataset = PHIDataset(val_encodings, val_labels)
        
        # Create data loaders
        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size)
        
        # Prepare optimizer and scheduler
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=0,
            num_training_steps=total_steps
        )
        
        # Training loop
        self.model.train()
        for epoch in range(epochs):
            print(f"Epoch {epoch + 1}/{epochs}")
            epoch_loss = 0
            
            for batch in train_loader:
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # Forward pass
                self.model.zero_grad()
                outputs = self.model(input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                epoch_loss += loss.item()
                
                # Backward pass
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
            
            # Print epoch loss
            avg_epoch_loss = epoch_loss / len(train_loader)
            print(f"Training loss: {avg_epoch_loss:.4f}")
            
            # Evaluate on validation set
            val_metrics = self.evaluate(val_texts, val_labels, batch_size)
            print(f"Validation accuracy: {val_metrics['accuracy']:.4f}")
            print(f"Validation ROC AUC: {val_metrics['roc_auc']:.4f}")
        
        # Save the model if a path is provided
        if save_path:
            self._save_model(save_path)
        
        # Final evaluation
        final_metrics = self.evaluate(val_texts, val_labels, batch_size)
        return final_metrics
    
    def evaluate(self, texts, labels, batch_size=16):
        """
        Evaluate the model on a dataset
        
        Args:
            texts (list): List of text samples
            labels (list): List of labels (1 for PHI, 0 for non-PHI)
            batch_size (int): Batch size for evaluation
            
        Returns:
            dict: Evaluation metrics
        """
        # Tokenize data
        encodings = self.tokenizer(texts, truncation=True, padding=True, max_length=128)
        
        # Create dataset and data loader
        dataset = PHIDataset(encodings, labels)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size)
        
        # Evaluation loop
        self.model.eval()
        predictions = []
        true_labels = []
        probs = []
        
        with torch.no_grad():
            for batch in loader:
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                batch_labels = batch['labels'].to(self.device)
                
                # Forward pass
                outputs = self.model(input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                
                # Get predictions and probabilities
                batch_preds = torch.argmax(logits, dim=1).cpu().numpy()
                batch_probs = torch.softmax(logits, dim=1).cpu().numpy()[:, 1]  # Probability of PHI class
                
                # Append to lists
                predictions.extend(batch_preds)
                true_labels.extend(batch_labels.cpu().numpy())
                probs.extend(batch_probs)
        
        # Calculate metrics
        accuracy = (np.array(predictions) == np.array(true_labels)).mean()
        report = classification_report(true_labels, predictions, output_dict=True)
        cm = confusion_matrix(true_labels, predictions)
        roc_auc = roc_auc_score(true_labels, probs)
        
        # Return metrics
        return {
            'accuracy': accuracy,
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'roc_auc': roc_auc
        }
    
    def predict(self, text):
        """
        Predict if a text contains PHI
        
        Args:
            text (str): Input text
            
        Returns:
            tuple: (is_phi, probability, highlighted_text)
        """
        # Tokenize text
        encoding = self.tokenizer(text, truncation=True, padding=True, max_length=128, return_tensors='pt')
        
        # Move to device
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        # Forward pass
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            
            # Get prediction and probability
            pred = torch.argmax(logits, dim=1).item()
            prob = torch.softmax(logits, dim=1)[0, 1].item()  # Probability of PHI class
        
        # Highlight potential PHI in text
        highlighted_text = self._highlight_phi(text)
        
        return pred == 1, prob, highlighted_text
    
    def _highlight_phi(self, text):
        """
        Highlight potential PHI in text using regex patterns
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Text with highlighted PHI and categories found
        """
        # Define regex patterns for different PHI categories
        patterns = {
            'NAME': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Simple name pattern
            'AGE': r'\b\d{1,3} years? old\b|\bage\s*:\s*\d{1,3}\b',
            'DATE': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
            'PHONE': r'\b\(\d{3}\)\s*\d{3}[-.]\d{4}\b|\b\d{3}[-.]\d{3}[-.]\d{4}\b',
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ID': r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',  # SSN-like pattern
            'ADDRESS': r'\b\d+\s+[A-Za-z]+\s+[A-Za-z]+\b',  # Simple address pattern
            'MEDICALRECORD': r'\bMR[N]?\s*#?\s*\d+\b|\bmedical record\s*#?\s*\d+\b'
        }
        
        # Find all matches
        findings = {}
        for category, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start, end = match.span()
                if category not in findings:
                    findings[category] = []
                findings[category].append({
                    'text': match.group(),
                    'start': start,
                    'end': end
                })
        
        return {
            'original_text': text,
            'findings': findings,
            'categories_found': list(findings.keys())
        }
    
    def _save_model(self, save_path):
        """
        Save the fine-tuned model and tokenizer
        
        Args:
            save_path (str): Path to save the model
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save model
        self.model.save_pretrained(save_path)
        
        # Save tokenizer
        tokenizer_path = os.path.join(os.path.dirname(save_path), 'tokenizer')
        self.tokenizer.save_pretrained(tokenizer_path)
        
        # Save metadata
        metadata_path = os.path.join(os.path.dirname(save_path), 'model_metadata.json')
        metadata = {
            'model_type': 'BERT',
            'pretrained_model': self.pretrained_model,
            'phi_categories': self.phi_categories,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

# Dataset class for BERT
class PHIDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# Example usage for generating synthetic data and training
def generate_synthetic_data(n_samples=1000):
    """
    Generate synthetic data for demonstration
    
    Args:
        n_samples (int): Number of samples to generate
        
    Returns:
        tuple: (texts, labels)
    """
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Sample non-PHI texts
    non_phi_texts = [
        "The patient's condition is stable and improving.",
        "Medication was administered as prescribed.",
        "Lab results show normal levels of glucose.",
        "Patient reports feeling better after treatment.",
        "Follow-up appointment scheduled for next month.",
        "No adverse reactions to the medication observed.",
        "Vital signs are within normal range.",
        "Patient was advised to rest and stay hydrated.",
        "The procedure was completed successfully without complications.",
        "Recommended physical therapy twice a week."
    ]
    
    # Sample PHI texts (with sensitive information)
    phi_texts = [
        "John Smith's blood pressure is 120/80.",
        "Please contact the patient at (555) 123-4567.",
        "Dr. Johnson prescribed medication for Mary Williams.",
        "Patient's date of birth is 05/12/1975.",
        "Send the results to patient@example.com.",
        "Patient lives at 123 Main Street, Anytown.",
        "Social security number is 123-45-6789.",
        "Medical record #12345 shows history of allergies.",
        "Jane Doe, 45 years old, was admitted on January 15, 2023.",
        "Please forward this to Dr. Sarah Brown at Memorial Hospital."
    ]
    
    # Generate synthetic data
    texts = []
    labels = []
    
    # Add non-PHI samples
    for _ in range(int(n_samples * 0.6)):  # 60% non-PHI
        text = np.random.choice(non_phi_texts)
        # Add some random medical terms
        if np.random.random() < 0.5:
            medical_terms = ["blood pressure", "heart rate", "temperature", "oxygen saturation", 
                            "medication", "treatment", "diagnosis", "prognosis", "symptoms"]
            text += f" {np.random.choice(medical_terms)} was noted."
        texts.append(text)
        labels.append(0)  # Non-PHI
    
    # Add PHI samples
    for _ in range(int(n_samples * 0.4)):  # 40% PHI
        text = np.random.choice(phi_texts)
        texts.append(text)
        labels.append(1)  # PHI
    
    # Shuffle the data
    indices = np.arange(len(texts))
    np.random.shuffle(indices)
    texts = [texts[i] for i in indices]
    labels = [labels[i] for i in indices]
    
    return texts, labels

def main():
    """
    Main function to demonstrate the PHI detection model
    """
    # Generate synthetic data
    print("Generating synthetic data...")
    texts, labels = generate_synthetic_data(n_samples=500)  # Smaller dataset for demonstration
    
    # Initialize the model
    print("Initializing BERT model...")
    model = PHIDetectionModel()
    
    # Train the model (with fewer epochs for demonstration)
    print("Training the model...")
    metrics = model.train(
        texts, 
        labels, 
        epochs=2,  # Fewer epochs for demonstration
        batch_size=8,
        save_path='models/phi_detection_model'
    )
    
    # Print evaluation metrics
    print("\nModel Evaluation:")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"ROC AUC: {metrics['roc_auc']:.4f}")
    
    # Example predictions
    print("\nTesting with example texts...")
    
    test_texts = [
        "The patient's condition is stable.",  # Non-PHI
        "John Doe's blood test results came back positive."  # Contains PHI (name)
    ]
    
    for text in test_texts:
        is_phi, probability, highlighted = model.predict(text)
        print(f"\nText: {text}")
        print(f"Contains PHI: {is_phi}")
        print(f"Probability: {probability:.4f}")
        print(f"Categories found: {highlighted['categories_found']}")

if __name__ == "__main__":
    main()