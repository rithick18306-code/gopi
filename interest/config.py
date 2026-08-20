import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "mysql"),
    "database": os.getenv("DB_NAME", "gold_pledge_db"),
    "port": int(os.getenv("DB_PORT", "3306")),
}
