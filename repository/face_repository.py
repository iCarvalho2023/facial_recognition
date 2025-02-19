import uuid
import binascii
import numpy as np
import psycopg2

from conn import db as conn


class FaceRepository:
    def __init__(self):
        self.conn = conn

    def get_all_faces(self, person_id=None):
        """Fetch all faces or filter by person_id."""
        cursor = self.conn.cursor()
        if person_id:
            cursor.execute("SELECT person_id, name, encoding FROM known_faces WHERE person_id = %s", (person_id,))
        else:
            cursor.execute("SELECT person_id, name, encoding FROM known_faces")

        rows = cursor.fetchall()
        cursor.close()

        known_faces = []
        known_names = []
        known_person_ids = []

        for row in rows:
            try:
                encoding = np.frombuffer(binascii.unhexlify(row[2]), dtype=np.float64)
                if encoding.shape[0] == 128:
                    known_faces.append(encoding)
                    known_names.append(row[1])
                    known_person_ids.append(row[0])
            except Exception as e:
                print(f"Error processing encoding for {row[1]}: {e}")

        return known_faces, known_names, known_person_ids

    def insert_face(self, person_id, name, img_str, encoding):
        """Insert a new face into the database."""
        try:
            cursor = self.conn.cursor()
            key = str(uuid.uuid4())
            encoding_base64 = binascii.hexlify(encoding.tobytes()).decode('utf-8')

            cursor.execute(
                "INSERT INTO known_faces (key, person_id, name, encoding, photo) VALUES (%s, %s, %s, %s, %s)",
                (key, person_id, name, encoding_base64, img_str)
            )
            self.conn.commit()
            cursor.close()
            print(f"Successfully inserted face with key {key}")
            return True
        except psycopg2.Error as error:
            print(f"Error inserting face: {error}")
            return False

    def get_faces_by_person_id(self, person_id):
        """Fetch stored faces for a person."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT key, person_id, name, photo FROM known_faces WHERE person_id = %s",
            (person_id,)
        )
        rows = cursor.fetchall()
        cursor.close()

        return [
            {
                "key": row[0],
                "person_id": row[1],
                "name": row[2],
                "photo": row[3]
            } for row in rows
        ]

    def get_encodings_by_person_id(self, person_id):
        """Fetch face encodings for a specific person."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT encoding FROM known_faces WHERE person_id = %s", (person_id,))
        rows = cursor.fetchall()
        cursor.close()
        return [np.frombuffer(binascii.unhexlify(row[0]), dtype=np.float64) for row in rows]
