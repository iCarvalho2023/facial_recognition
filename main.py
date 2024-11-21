from flask import Flask, Blueprint
from controller.face_controller import show, store
import os

face_api = Blueprint('face_api', __name__, url_prefix='/face-api')


@face_api.route('/register_face', methods=['POST'])
def register_faces_function():
    return store()


@face_api.route('/identify_face', methods=['POST'])
def identify_faces_function():
    return show()


@face_api.route("/")
def home():
    return "Face API is running!"


# Main Flask app
app = Flask(__name__)

# Register the Blueprint with the main app
app.register_blueprint(face_api)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
