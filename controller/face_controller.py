from flask import request, jsonify
import cv2
import json
import numpy as np
import face_recognition
from repository.face_repository import FaceRepository
from utils.utils import encode_image, create_error_response, draw_face

face_repo = FaceRepository()


def show():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']
    image = face_recognition.load_image_file(file)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(image_rgb)
    if len(face_locations) != 1:
        return create_error_response("A single face must be detected", image_rgb)

    face_encoding = face_recognition.face_encodings(image_rgb, face_locations)[0]
    person_id = request.args.get("personId")

    known_encodings, known_names, known_person_ids = face_repo.get_all_faces(person_id)
    if not known_encodings:
        return create_error_response("No registered faces found", image_rgb)

    face_distances = face_recognition.face_distance(known_encodings, face_encoding)
    best_match_index = np.argmin(face_distances)

    if face_distances[best_match_index] > 0.6:
        name = "Visitante"
        person_id = None
    else:
        name = known_names[best_match_index]
        person_id = known_person_ids[best_match_index]

    draw_face(image_rgb, face_locations[0], name)
    return jsonify({
        "image": encode_image(image_rgb),
        "person": {"name": name, "person_id": person_id},
        "perentage": face_distances[best_match_index]
    })


def store():
    person_data = request.form.get("person_data")
    if not person_data:
        return jsonify({"error": "person_data is required"}), 400

    try:
        person_data = json.loads(person_data)
        person_id, name = person_data.get("person_id"), person_data.get("name")
        if not person_id or not name:
            return jsonify({"error": "Both person_id and name are required"}), 400
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400

    images = request.files.getlist("images")
    if not images:
        return jsonify({"error": "No images provided"}), 400

    known_encodings = face_repo.get_encodings_by_person_id(person_id)
    first_encoding = None

    for img_file in images:
        image = face_recognition.load_image_file(img_file)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(image_rgb)

        if len(encodings) != 1:
            return jsonify({"error": "Each image must contain exactly one face"}), 400

        face_encoding = encodings[0]
        if first_encoding is None:
            first_encoding = face_encoding
        elif not face_recognition.compare_faces([first_encoding], face_encoding)[0]:
            return jsonify({"error": "All images must be of the same person"}), 400

        if any(face_recognition.compare_faces(known_encodings, face_encoding)):
            return jsonify({"error": "Person does not match previously registered photos"}), 400

        img_str = encode_image(image_rgb)
        if not face_repo.insert_face(person_id, name, img_str, face_encoding):
            return jsonify({"error": "Database insertion failed"}), 500

    return jsonify({"message": "All faces registered successfully"}), 201


def index():
    person_id = request.args.get("personId")
    if not person_id:
        return jsonify({"error": "personId query parameter is required"}), 400

    faces = face_repo.get_faces_by_person_id(person_id)
    return (jsonify(faces), 200) if faces else (jsonify({"error": "No faces found"}), 404)
