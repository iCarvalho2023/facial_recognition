from flask import Flask
from controller.face_controller import show, store

app = Flask(__name__)


@app.route('/identify_face', methods=['POST'])
def identify_faces_function():
    return show()


@app.route('/register_face', methods=['POST'])
def register_faces_function():
    return store()


if __name__ == "__main__":
    app.run(debug=True)
