"""
Google Cloud Storage helper for secure file storage
"""
import os
import json
from datetime import datetime
from typing import Optional
from google.cloud import storage
from ai_core.config import settings
from ai_core.logger import logger


class CloudStorageManager:
    """Manages file storage in Google Cloud Storage"""
    
    def __init__(self):
        self.bucket_name = settings.GCP_BUCKET_NAME
        self.client = None
        self.bucket = None
        
        if settings.GCP_PROJECT_ID and settings.GCP_BUCKET_NAME:
            try:
                self.client = storage.Client(project=settings.GCP_PROJECT_ID)
                self.bucket = self.client.bucket(self.bucket_name)
                logger.info(f"Connected to GCS bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to initialize GCS: {e}")
    
    def upload_conversation(self, conversation_data: dict, conversation_id: str) -> bool:
        """Upload conversation to cloud storage"""
        try:
            if not self.bucket:
                # Fallback to local storage
                return self._save_local(conversation_data, conversation_id, "conversations")
            
            blob_name = f"conversations/{conversation_id}.json"
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(
                json.dumps(conversation_data, indent=2),
                content_type="application/json"
            )
            logger.info(f"Uploaded conversation {conversation_id} to GCS")
            return True
        except Exception as e:
            logger.error(f"Failed to upload conversation: {e}")
            return self._save_local(conversation_data, conversation_id, "conversations")
    
    def upload_flagged(self, question_data: dict, question_id: str) -> bool:
        """Upload flagged question to cloud storage"""
        try:
            if not self.bucket:
                return self._save_local(question_data, question_id, "flagged_questions")
            
            blob_name = f"flagged_questions/{question_id}.json"
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(
                json.dumps(question_data, indent=2),
                content_type="application/json"
            )
            logger.info(f"Uploaded flagged question {question_id} to GCS")
            return True
        except Exception as e:
            logger.error(f"Failed to upload flagged question: {e}")
            return self._save_local(question_data, question_id, "flagged_questions")
    
    def _save_local(self, data: dict, file_id: str, folder: str) -> bool:
        """Fallback to local file storage"""
        try:
            os.makedirs(folder, exist_ok=True)
            filepath = os.path.join(folder, f"{file_id}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {file_id} locally to {folder}")
            return True
        except Exception as e:
            logger.error(f"Failed to save locally: {e}")
            return False


# Singleton instance
cloud_storage = CloudStorageManager()
