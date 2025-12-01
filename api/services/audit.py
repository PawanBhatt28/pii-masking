import mysql.connector
from mysql.connector import pooling
from api.config import settings
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class AuditService:
    def __init__(self):
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="audit_pool",
                pool_size=5,
                host=settings.MYSQL_HOST,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DB
            )
            self._init_db()
        except Exception as e:
            logger.error(f"Error connecting to MySQL: {e}")
            self.pool = None

    def _get_connection(self):
        """Get connection with retry if pool was not initialized."""
        if self.pool:
            return self.pool.get_connection()
            
        # Try to reconnect
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="audit_pool",
                pool_size=5,
                host=settings.MYSQL_HOST,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DB
            )
            self._init_db()
            return self.pool.get_connection()
        except Exception as e:
            logger.error(f"Still unable to connect to MySQL: {e}")
            return None

    def _init_db(self):
        """Initialize audit table if not exists."""
        if not self.pool:
            return
            
        conn = self.pool.get_connection()
        cursor = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS audit_events (
            event_id VARCHAR(50) PRIMARY KEY,
            timestamp DATETIME(6) NOT NULL,
            operation VARCHAR(20) NOT NULL,
            session_id VARCHAR(50),
            user_id VARCHAR(50),
            user_role VARCHAR(50),
            ip_address VARCHAR(45),
            pii_types_accessed JSON,
            purpose VARCHAR(100),
            reason TEXT,
            success BOOLEAN,
            metadata JSON,
            created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
            INDEX idx_session (session_id),
            INDEX idx_user (user_id),
            INDEX idx_timestamp (timestamp)
        ) ENGINE=InnoDB;
        """
        
        try:
            cursor.execute(create_table_query)
            conn.commit()
        except Exception as e:
            logger.error(f"Error creating table: {e}")
        finally:
            cursor.close()
            conn.close()

    def log_event(self, 
                  operation: str,
                  session_id: str,
                  user_id: str,
                  user_role: str,
                  pii_types: List[str],
                  purpose: str = None,
                  reason: str = None,
                  success: bool = True,
                  metadata: Dict = None) -> str:
        """
        Log an audit event to MySQL.
        """
        # We don't get connection here to keep it fast, but we check if we can
        if not self.pool and not self._get_connection():
             logger.warning("Audit service not connected to DB")
             return "offline_audit_id"
            
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow()
        
        query = """
        INSERT INTO audit_events 
        (event_id, timestamp, operation, session_id, user_id, user_role, pii_types_accessed, purpose, reason, success, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            event_id,
            timestamp,
            operation,
            session_id,
            user_id,
            user_role,
            json.dumps(pii_types),
            purpose,
            reason,
            success,
            json.dumps(metadata) if metadata else None
        )
        
        conn = None
        try:
            conn = self._get_connection()
            if not conn:
                return "offline_audit_id"
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            return event_id
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            return "error_logging"
        finally:
            if conn:
                conn.close()

    def get_events(self, session_id: str = None, limit: int = 50) -> List[Dict]:
        """
        Retrieve audit events.
        """
        if not self.pool:
            return []
            
        query = "SELECT * FROM audit_events"
        params = []
        
        if session_id:
            query += " WHERE session_id = %s"
            params.append(session_id)
            
        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)
        
        conn = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Error fetching audit events: {e}")
            return []
        finally:
            if conn:
                conn.close()

audit_service = AuditService()
