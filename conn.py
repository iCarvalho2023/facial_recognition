import os
from dotenv import load_dotenv
import psycopg2
import firebase_admin
from firebase_admin import credentials

project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "default")

if project_id == 'serlares-pass':
    env_file = ".env."
elif project_id == 'serlares-pass-test':
    env_file = ".env.test"
else:
    env_file = ".env.dev"

load_dotenv(f"config/{env_file}")

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_database = os.getenv("DB_DATABASE")
firebase_adm_sdk_path = os.getenv("FIREBASE_ADM_SDK_PATH")
base_url = os.getenv("API_BASE_URL")

print(f"Carregando variáveis de ambiente de: {env_file}:{project_id}, url: {base_url}")

cred = credentials.Certificate(f"config/{firebase_adm_sdk_path}")
firebase_admin.initialize_app(cred)

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
    db = None
    cred = None
