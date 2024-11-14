from collections import namedtuple
import cv2
import face_recognition
import numpy as np
from conn import dbConn
from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

# Define a namedtuple for the row
KnownFace = namedtuple('KnownFace', ['key', 'person_id', 'name', 'encoding'])


def load_known_faces():
    conn = dbConn
    cursor = conn.cursor()

    cursor.execute("SELECT key, person_id, name, encoding FROM known_faces")
    rows = cursor.fetchall()

    known_faces = []
    known_names = []
    known_person_ids = []

    for row in rows:
        row_dict = {
            'key': row[0],
            'person_id': row[1],
            'name': row[2],
            'encoding': row[3]
        }

        try:
            encoding = np.frombuffer(row_dict['encoding'], dtype=np.float64)
            known_faces.append(encoding)
            known_names.append(row_dict['name'])
            known_person_ids.append(row_dict['person_id'])
        except Exception as e:
            print(f"Error processing encoding for {row_dict['name']}: {e}")

    cursor.close()
    conn.close()

    return known_faces, known_names, known_person_ids


known_encodings, known_names, known_person_ids = load_known_faces()


@app.route('/identify_faces', methods=['POST'])
def identify_faces_function(_):

    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']
    image = face_recognition.load_image_file(file)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(image_rgb)
    face_encodings = face_recognition.face_encodings(image_rgb, face_locations)

    persons = []  # List to store recognized persons

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Visitante"
        person_id = ""

        if True in matches:
            match_index = matches.index(True)
            name = known_names[match_index]
            person_id = known_person_ids[match_index]  # Get person_id directly

        cv2.rectangle(image_rgb, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(image_rgb, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        persons.append({
            "name": name,
            "person_id": person_id
        })

    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode('.jpg', image_bgr)
    img_str = base64.b64encode(buffer).decode('utf-8')

    return jsonify(persons)
