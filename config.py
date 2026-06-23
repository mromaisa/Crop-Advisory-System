#System and Database Configuration files stay here
import pyodbc

class Config:
    SECRET_KEY = 'super_secret_system_key_change_in_production'
    
    # Update these parameters with your SQL Server instance details
    DB_SERVER   = r'192.168.100.62'  # e.g., 'localhost\SQLEXPRESS' or an IP
    DB_DATABASE = 'Crop_Advisory'
    DB_USERNAME = 'romaisa'                     # Leave empty if using Windows Authentication
    DB_PASSWORD = 'Password123'     # Leave empty if using Windows Authentication
    DB_DRIVER   = '{ODBC Driver 18 for SQL Server}'

    @classmethod
    def get_db_connection(cls):
        """Builds an isolated connection string and returns a raw pyodbc connection."""
        if cls.DB_USERNAME and cls.DB_PASSWORD:
            # SQL Server Authentication
            conn_str = (
                f"DRIVER={cls.DB_DRIVER};"
                f"SERVER={cls.DB_SERVER};"
                f"DATABASE={cls.DB_DATABASE};"
                f"UID={cls.DB_USERNAME};"
                f"PWD={cls.DB_PASSWORD};"
                f"TrustServerCertificate=yes;"
            )
        else:
            # Trusted Connection (Windows Authentication)
            conn_str = (
                f"DRIVER={cls.DB_DRIVER};"
                f"SERVER={cls.DB_SERVER};"
                f"DATABASE={cls.DB_DATABASE};"
                f"Trusted_Connection=yes;"
            )
        return pyodbc.connect(conn_str)
