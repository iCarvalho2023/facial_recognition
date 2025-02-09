from conn import db as conn
import uuid
import binascii
import face_recognition
from flask import request, jsonify
import numpy as np
import cv2
import psycopg2.errors
import base64
import json


def show():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']
    image = face_recognition.load_image_file(file)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(image_rgb)

    if len(face_locations) == 0:
        cv2.putText(image_rgb, "No face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        return create_error_response("No faces detected", image_rgb)

    if len(face_locations) > 1:
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(image_rgb, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(image_rgb, "Multiple faces detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        return create_error_response("More than one face detected", image_rgb)

    face_encoding = face_recognition.face_encodings(image_rgb, face_locations)[0]

    if face_encoding.shape[0] != 128:
        (top, right, bottom, left) = face_locations[0]
        cv2.rectangle(image_rgb, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(image_rgb, "Face encoding dimensions incorrect", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 255), 2)
        return create_error_response("Face encoding dimensions incorrect", image_rgb)

    known_encodings, known_names, known_person_ids = load_face()

    matches = face_recognition.compare_faces(known_encodings, face_encoding)
    name = "Visitante"
    person_id = None

    if True in matches:
        match_index = matches.index(True)
        name = known_names[match_index]
        person_id = known_person_ids[match_index]

    (top, right, bottom, left) = face_locations[0]
    cv2.rectangle(image_rgb, (left, top), (right, bottom), (0, 255, 0), 2)
    cv2.putText(image_rgb, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode('.jpg', image_bgr)
    img_str = base64.b64encode(buffer).decode('utf-8')

    return jsonify({
        "image": img_str,
        "person": {
            "name": name,
            "person_id": person_id
        }
    })


def create_error_response(error_message, image_rgb):
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode('.jpg', image_bgr)
    img_str = base64.b64encode(buffer).decode('utf-8')

    return jsonify({
        "error": error_message,
        "image": img_str
    }), 400


def store():
    person_data = request.form.get("person_data")
    if person_data is None:
        return jsonify({"error": "person_data is required"}), 400

    try:
        person_data = json.loads(person_data)
        person_id = person_data.get("person_id")
        name = person_data.get("name")
        if not person_id or not name:
            return jsonify({"error": "Both person_id and name are required"}), 400
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in person_data"}), 400

    images = request.files.getlist("images")
    if not images:
        return jsonify({"error": "No images provided"}), 400

    for img_file in images:
        image = face_recognition.load_image_file(img_file)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode('.jpg', image_rgb)

        img_str = base64.b64encode(buffer).decode('utf-8')
        encodings = face_recognition.face_encodings(image_rgb)

        if len(encodings) == 0:
            return jsonify({"error": "No face detected"}), 400
        elif len(encodings) > 1:
            return jsonify({"error": "Multiple faces detected in one of the images"}), 400

        face_encoding = encodings[0]
        if face_encoding.shape[0] != 128:
            return jsonify({"error": "Invalid encoding size"}), 400

        response = insert_face(person_id, name, img_str, face_encoding)
        if response[1] != 200:
            return response

    return jsonify({"message": "All faces registered successfully"}), 201


def insert_face(person_id, name, img_str, encoding):
    try:
        cursor = conn.cursor()

        key = str(uuid.uuid4())
        encoding_base64 = binascii.hexlify(encoding.tobytes()).decode('utf-8')

        if encoding.shape[0] != 128:
            return jsonify({"error": "Invalid encoding size"}), 400

        cursor.execute(
            "INSERT INTO known_faces (key, person_id, name, encoding, photo) VALUES (%s, %s, %s, %s, %s)",
            (key, person_id, name, encoding_base64, img_str)
        )
        conn.commit()
        cursor.close()
        print(f"Successfully inserted face with key {key}")
        return jsonify({"message": "Face registered successfully"}), 200

    except psycopg2.Error as error:
        return jsonify({"error": "Error inserting face", "message": str(error)}), 500


def load_face():
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
            encoding = np.frombuffer(binascii.unhexlify(row_dict['encoding']), dtype=np.float64)
            if encoding.shape[0] == 128:
                known_faces.append(encoding)
                known_names.append(row_dict['name'])
                known_person_ids.append(row_dict['person_id'])
            else:
                print(f"Skipping encoding for {row_dict['name']}: Incorrect dimensions {encoding.shape}")
        except Exception as e:
            print(f"Error processing encoding for {row_dict['name']}: {e}")

    cursor.close()
    return known_faces, known_names, known_person_ids


def index():
    person_id = request.args.get('personId')
    if not person_id:
        return jsonify({"error": "personId query parameter is required"}), 400

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT key, person_id, name, photo FROM known_faces WHERE person_id = %s",
            (person_id,)
        )
        rows = cursor.fetchall()

        known_faces = []
        for row in rows:
            base64_bytes = base64.b64decode(row[3])
            encoding_base64_reencoded = base64.b64encode(base64_bytes).decode('utf-8')

            known_faces.append({
                "key": row[0],
                "person_id": row[1],
                "name": row[2],
                "photo": encoding_base64_reencoded
            })

        cursor.close()
        return jsonify(known_faces), 200

    except psycopg2.Error as error:
        return jsonify({"error": "Error retrieving faces", "message": str(error.pgerror)}), 500
