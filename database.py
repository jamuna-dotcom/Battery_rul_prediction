import os
import logging
import mysql.connector
from mysql.connector import pooling, Error

logger = logging.getLogger(__name__)


class DatabaseConfig:
    _connection_pool = None

    @classmethod
    def initialize_pool(cls):
        """Initializes MySQL connection pool without crashing if offline."""
        try:
            cls._connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="battery_pool",
                pool_size=5,
                pool_reset_session=True,
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", 3306)),
                database=os.getenv("DB_NAME", "battery_rul_db"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "")
            )
            logger.info("MySQL Connection Pool initialized successfully.")
        except Error as err:
            cls._connection_pool = None
            logger.warning(f"Database connection failed ({err}). Operating in OFFLINE / NO-DB mode.")

    @classmethod
    def get_connection(cls):
        """Returns a connection if pool exists, else None."""
        if cls._connection_pool:
            try:
                return cls._connection_pool.get_connection()
            except Error as err:
                logger.warning(f"Failed to retrieve database connection: {err}")
                return None
        return None


def get_db():
    """Helper function for retrieving a database connection."""
    return DatabaseConfig.get_connection()