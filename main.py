import os
from firebase_admin import auth
from flask import Flask, Blueprint, request, jsonify, g
from flask_cors import CORS
from flasgger import Swagger, swag_from

import conn
from controller.face_controller import show, store

face_api = Blueprint('face_api', __name__, url_prefix='/face-api')


@face_api.before_request
def authenticate():
    if request.endpoint == 'face_api.home':
        return

    authorization = request.headers.get('Authorization')

    if not authorization or not authorization.startswith('Bearer '):
        return jsonify({"message": "Unauthorized"}), 403

    id_token = authorization.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        g.user = decoded_token
    except Exception as e:
        print(f"Erro ao verificar token Firebase: {e}")
        return jsonify({"message": "Unauthorized"}), 403


@face_api.route('/register_face', methods=['POST'])
@swag_from('swagger/register_face.yml')
def register_faces_function():
    return store()


@face_api.route('/identify_face', methods=['POST'])
@swag_from('swagger/identify_face.yml')
def identify_faces_function():
    return show()


@face_api.route("/")
def home():
    return "Face API is running!"


app = Flask(__name__)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Face API",
        "description": "API para registro e identificação de faces.",
        "version": "1.0.0"
    },
    "host": conn.base_url,
    "basePath": "/face-api",
    "schemes": [
        "https"
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "\
        JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

CORS(app, resources={r"/face-api/*": {"origins": "http://localhost:8080"}}, supports_credentials=True)
app.register_blueprint(face_api)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
