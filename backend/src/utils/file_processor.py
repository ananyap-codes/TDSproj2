"""
File processor for handling various data file formats
"""

import os
import pandas as pd
import json
from typing import Optional, Union, Any
from PIL import Image
import io

class FileProcessor:
    def __init__(self):
        self.supported_extensions = {
            '.csv': self._process_csv,
            '.xlsx': self._process_excel,
            '.xls': self._process_excel,
            '.json': self._process_json,
            '.txt': self._process_text,
            '.tsv': self._process_tsv,
            '.png': self._process_image,
            '.jpg': self._process_image,
            '.jpeg': self._process_image
        }

    def process_file(self, filepath: str) -> Optional[Any]:
        """
        Process a file based on its extension
        Returns processed data or None if unsupported
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        # Get file extension
        _, ext = os.path.splitext(filepath.lower())

        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {ext}")

        # Process the file
        processor = self.supported_extensions[ext]
        return processor(filepath)

    def _process_csv(self, filepath: str) -> pd.DataFrame:
        """Process CSV files"""
        try:
            # Try different separators and encodings
            separators = [',', ';', '\t']
            encodings = ['utf-8', 'latin-1', 'cp1252']

            for encoding in encodings:
                for sep in separators:
                    try:
                        df = pd.read_csv(filepath, sep=sep, encoding=encoding)
                        if df.shape[1] > 1:  # Valid if more than 1 column
                            return df
                    except:
                        continue

            # Fallback
            return pd.read_csv(filepath)

        except Exception as e:
            raise ValueError(f"Failed to process CSV file: {str(e)}")

    def _process_excel(self, filepath: str) -> pd.DataFrame:
        """Process Excel files"""
        try:
            # Try to read the first sheet
            df = pd.read_excel(filepath, engine='openpyxl' if filepath.endswith('.xlsx') else None)
            return df
        except Exception as e:
            raise ValueError(f"Failed to process Excel file: {str(e)}")

    def _process_json(self, filepath: str) -> Union[pd.DataFrame, dict]:
        """Process JSON files"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Try to convert to DataFrame if it's a list of dictionaries
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                return pd.DataFrame(data)
            else:
                return data

        except Exception as e:
            raise ValueError(f"Failed to process JSON file: {str(e)}")

    def _process_text(self, filepath: str) -> str:
        """Process text files"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            # Try different encodings
            encodings = ['latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        return f.read()
                except:
                    continue
            raise ValueError(f"Failed to process text file: {str(e)}")

    def _process_tsv(self, filepath: str) -> pd.DataFrame:
        """Process TSV (Tab-separated values) files"""
        try:
            return pd.read_csv(filepath, sep='\t')
        except Exception as e:
            raise ValueError(f"Failed to process TSV file: {str(e)}")

    def _process_image(self, filepath: str) -> dict:
        """Process image files"""
        try:
            with Image.open(filepath) as img:
                # Get image info
                image_info = {
                    'filename': os.path.basename(filepath),
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height
                }

                # Convert to base64 for API response
                img_buffer = io.BytesIO()
                img.save(img_buffer, format=img.format if img.format else 'PNG')
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                image_info['base64_data'] = f"data:image/{img.format.lower() if img.format else 'png'};base64,{img_base64}"

                return image_info

        except Exception as e:
            raise ValueError(f"Failed to process image file: {str(e)}")

    def get_file_info(self, filepath: str) -> dict:
        """Get basic information about a file"""
        if not os.path.exists(filepath):
            return {"error": "File not found"}

        stat = os.stat(filepath)
        _, ext = os.path.splitext(filepath)

        return {
            "filename": os.path.basename(filepath),
            "extension": ext,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "supported": ext.lower() in self.supported_extensions
        }
