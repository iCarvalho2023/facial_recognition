from flask import jsonify
import cv2
import numpy as np
import mediapipe as mp
import base64
import re

mp_selfie_segmentation = mp.solutions.selfie_segmentation
BASE64_RE = re.compile(r'^[A-Za-z0-9+/=\r\n]+$')


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

        binary_mask = mask > 0.5

        total_pixels = binary_mask.size
        person_pixels = np.sum(binary_mask)
        background_pixels = total_pixels - person_pixels

        background_ratio = background_pixels / total_pixels

        if background_ratio < 0.1:
            return False
        else:
            return True


def normalize_photo(photo_mv):
    if photo_mv is None:
        return None

    raw = bytes(photo_mv)

    try:
        txt = raw.decode("utf-8").strip()
    except UnicodeDecodeError:
        txt = None

    if txt:
        if txt.startswith("data:"):
            try:
                header, b64data = txt.split(",", 1)
                return b64data.strip()
            except ValueError:
                pass

        if BASE64_RE.match(txt) and len(txt.replace("\n", "")) % 4 == 0:
            return txt.replace("\n", "")

    return base64.b64encode(raw).decode("ascii")
