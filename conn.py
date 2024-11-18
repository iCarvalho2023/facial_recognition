import os
from dotenv import load_dotenv
import psycopg2


env_file = ".env.dev"
load_dotenv(env_file)

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_database = os.getenv("DB_DATABASE")

try:
    db = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_username,
        password=db_password,
        dbname=db_database,
    )
    print("Conexão com o banco de dados bem-sucedida!")
except Exception as e:
    print("Erro ao conectar ao banco de dados:", e)