import re
import json
import logging
from typing import Union, Dict, Any
from bs4 import BeautifulSoup
import pandas as pd

logger = logging.getLogger(__name__)

class TextPreprocessor:
    """
    Flexible text preprocessor for handling different input formats during inference.
    """
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text by removing extra whitespace, special characters, etc.
        
        Args:
            text (str): Raw text input
            
        Returns:
            str: Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove HTML tags if present
        text = BeautifulSoup(text, "html.parser").get_text()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_text_from_dict(data: Dict[str, Any]) -> str:
        """
        Extract text from a dictionary with various possible field names.
        
        Args:
            data (Dict[str, Any]): Dictionary containing text data
            
        Returns:
            str: Extracted and concatenated text
        """
        text_parts = []
        
        # Common field names for text content
        text_fields = ['text', 'body', 'content', 'article', 'story', 'description']
        title_fields = ['title', 'headline', 'subject']
        
        # Extract main text content
        for field in text_fields:
            if field in data and data[field]:
                text_parts.append(str(data[field]))
        
        # Extract title/headline if no main text found
        if not text_parts:
            for field in title_fields:
                if field in data and data[field]:
                    text_parts.append(str(data[field]))
        
        # If still no text found, try any field that looks like text
        if not text_parts:
            for key, value in data.items():
                if isinstance(value, str) and len(value) > 20:  # Likely text content
                    text_parts.append(value)
        
        return ' '.join(text_parts)
    
    @staticmethod
    def extract_text_from_json(json_str: str) -> str:
        """
        Extract text from a JSON string.
        
        Args:
            json_str (str): JSON string containing text data
            
        Returns:
            str: Extracted text
        """
        try:
            data = json.loads(json_str)
            if isinstance(data, dict):
                return TextPreprocessor.extract_text_from_dict(data)
            elif isinstance(data, list) and len(data) > 0:
                # Handle list of articles
                texts = []
                for item in data:
                    if isinstance(item, dict):
                        texts.append(TextPreprocessor.extract_text_from_dict(item))
                    elif isinstance(item, str):
                        texts.append(item)
                return ' '.join(texts)
            else:
                return str(data)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON format, treating as plain text")
            return json_str
    
    @staticmethod
    def extract_text_from_csv_row(row: Union[pd.Series, Dict]) -> str:
        """
        Extract text from a CSV row or dictionary with CSV-like structure.
        
        Args:
            row: Pandas Series or dictionary representing a CSV row
            
        Returns:
            str: Extracted text
        """
        if isinstance(row, pd.Series):
            row = row.to_dict()
        
        return TextPreprocessor.extract_text_from_dict(row)
    
    @staticmethod
    def preprocess_input(input_data: Union[str, Dict, Any]) -> str:
        """
        Main preprocessing function that handles various input formats.
        
        Args:
            input_data: Input data in various formats (string, dict, JSON string, etc.)
            
        Returns:
            str: Cleaned and extracted text ready for model inference
            
        Raises:
            ValueError: If input format is not supported or no text can be extracted
        """
        try:
            # Handle string input
            if isinstance(input_data, str):
                # Check if it's JSON
                if input_data.strip().startswith('{') or input_data.strip().startswith('['):
                    text = TextPreprocessor.extract_text_from_json(input_data)
                else:
                    text = input_data
                
                return TextPreprocessor.clean_text(text)
            
            # Handle dictionary input
            elif isinstance(input_data, dict):
                text = TextPreprocessor.extract_text_from_dict(input_data)
                return TextPreprocessor.clean_text(text)
            
            # Handle pandas Series (from CSV)
            elif hasattr(input_data, 'to_dict'):  # Pandas Series
                text = TextPreprocessor.extract_text_from_csv_row(input_data)
                return TextPreprocessor.clean_text(text)
            
            # Handle list input
            elif isinstance(input_data, list):
                texts = []
                for item in input_data:
                    if isinstance(item, str):
                        texts.append(item)
                    elif isinstance(item, dict):
                        texts.append(TextPreprocessor.extract_text_from_dict(item))
                    else:
                        texts.append(str(item))
                combined_text = ' '.join(texts)
                return TextPreprocessor.clean_text(combined_text)
            
            else:
                # Try to convert to string
                text = str(input_data)
                return TextPreprocessor.clean_text(text)
                
        except Exception as e:
            logger.error(f"Error preprocessing input: {str(e)}")
            raise ValueError(f"Failed to preprocess input: {str(e)}")
    
    @staticmethod
    def validate_input(input_data: Union[str, Dict, Any]) -> bool:
        """
        Validate if the input contains meaningful text content.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            bool: True if input contains valid text, False otherwise
        """
        try:
            processed_text = TextPreprocessor.preprocess_input(input_data)
            return len(processed_text.strip()) > 10  # Minimum meaningful length
        except:
            return False 