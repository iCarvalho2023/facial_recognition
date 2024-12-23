import os
from dotenv import load_dotenv
import psycopg2
import firebase_admin
from firebase_admin import credentials

project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "default")

if project_id == 'serlares-pass':
    env_file = ".env."
    firebase_adm_sdk_path = "serlares-pass-prod-firebase-sdk.json"
    base_url = ''
elif project_id == 'serlares-pass-test':
    env_file = ".env.test"
    firebase_adm_sdk_path = "serlares-pass-test-firebase-sdk.json"
    base_url = ''
else:
    env_file = ".env.dev"
    firebase_adm_sdk_path = "serlares-pass-dev-firebase-sdk.json"
    base_url = 'face-api-51745000658.southamerica-east1.run.app'

print(f"Carregando variáveis de ambiente de: {env_file}:{project_id}")

load_dotenv(f"config/{env_file}")
cred = credentials.Certificate(f"config/{firebase_adm_sdk_path}")
firebase_admin.initialize_app(cred)

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
    db = None
    cred = None
