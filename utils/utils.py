import base64

import cv2
from flask import jsonify


def create_error_response(error_message, image_rgb):
    return jsonify({"error": error_message, "image": encode_image(image_rgb)}), 400


def draw_face(image_rgb, face_location, name):
    top, right, bottom, left = face_location
    cv2.rectangle(image_rgb, (left, top), (right, bottom), (0, 255, 0), 2)
    cv2.putText(image_rgb, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


def encode_image(image_rgb):
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode('.jpg', image_bgr)
    return base64.b64encode(buffer).decode('utf-8')