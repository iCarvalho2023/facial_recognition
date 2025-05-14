import base64

import cv2
from flask import jsonify
import cv2
import numpy as np
import mediapipe as mp

mp_selfie_segmentation = mp.solutions.selfie_segmentation


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


def detect_fake_face(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as segment:
        results = segment.process(image_rgb)
        mask = results.segmentation_mask

        # Cria uma máscara binária: 1 = pessoa, 0 = fundo
        binary_mask = mask > 0.5

        # Conta pixels da pessoa e do fundo
        total_pixels = binary_mask.size
        person_pixels = np.sum(binary_mask)
        background_pixels = total_pixels - person_pixels

        # Calcula proporção do fundo
        background_ratio = background_pixels / total_pixels

        if background_ratio < 0.1:
            return False
        else:
            return True

