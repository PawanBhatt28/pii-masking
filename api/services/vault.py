import redis
import json
from cryptography.fernet import Fernet
from api.config import settings
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class VaultService:
    """
    Secure storage for PII tokens using Redis and Fernet encryption.
    """
    
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        self.default_ttl = 86400  # 24 hours

    def encrypt(self, data: str) -> str:
        """Encrypt string data."""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def store_token(self, session_id: str, token: str, pii_data: Dict[str, Any], ttl: int = None) -> bool:
        """
        Store PII data associated with a token in Redis.
        Structure: session:{session_id}:{token} -> encrypted_json
        """
        try:
            key = f"session:{session_id}:{token}"
            
            # Encrypt the sensitive value inside the data
            # We store the whole metadata object, but ensure sensitive value is encrypted
            # Actually, let's encrypt the whole JSON blob for simplicity and security
            
            json_data = json.dumps(pii_data)
            encrypted_blob = self.encrypt(json_data)
            
            expiration = ttl if ttl is not None else self.default_ttl
            
            self.redis.setex(key, expiration, encrypted_blob)
            return True
        except Exception as e:
            logger.error(f"Error storing token: {e}")
            return False

    def get_token(self, session_id: str, token: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve and decrypt PII data for a token.
        """
        try:
            key = f"session:{session_id}:{token}"
            encrypted_blob = self.redis.get(key)
            
            if not encrypted_blob:
                return None
                
            decrypted_json = self.decrypt(encrypted_blob)
            return json.loads(decrypted_json)
        except Exception as e:
            logger.error(f"Error retrieving token: {e}")
            return None

    def get_all_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve all stored PII tokens (Debug/Admin only).
        """
        try:
            keys = self.redis.keys("session:*:*")
            entries = []
            
            # Limit keys to avoid performance hit
            for key in keys[:limit]:
                try:
                    encrypted_blob = self.redis.get(key)
                    if encrypted_blob:
                        decrypted_json = self.decrypt(encrypted_blob)
                        data = json.loads(decrypted_json)
                        entries.append({
                            "key": key,
                            "data": data,
                            "ttl": self.redis.ttl(key)
                        })
                except Exception as e:
                    logger.warning(f"Failed to decrypt key {key}: {e}")
                    entries.append({"key": key, "error": "Decryption failed"})
            
            return entries
        except Exception as e:
            logger.error(f"Error listing entries: {e}")
            return []

vault_service = VaultService()
