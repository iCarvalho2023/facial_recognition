import cv2
import face_recognition


def identify_faces(image_path, known_encodings, known_names):
    # Load the input image and convert it to RGB
    image = face_recognition.load_image_file(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Find face locations and encodings in the input image
    face_locations = face_recognition.face_locations(image_rgb)
    face_encodings = face_recognition.face_encodings(image_rgb, face_locations)

    # Iterate over each detected face
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare with each known face
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"

        # Check if there's a match
        if True in matches:
            match_index = matches.index(True)
            name = known_names[match_index]

        # Draw the rectangle and name on the image
        cv2.rectangle(image_rgb, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(image_rgb, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the image with identification
    cv2.imshow("Face Identification", image_rgb)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def add_person(image_path, name, known_encodings, known_names):
    # Load the image and get the face encoding
    image = face_recognition.load_image_file(image_path)
    face_encoding = face_recognition.face_encodings(image)[0]

    # Add encoding and name to the known lists
    known_encodings.append(face_encoding)
    known_names.append(name)


# Example usage
known_encodings = [
    face_recognition.face_encodings(face_recognition.load_image_file("pessoa2.jpg"))[0],
    face_recognition.face_encodings(face_recognition.load_image_file("pessoa1.jpeg"))[0]
]
known_names = ["Mateus", "Isaias"]

# Add a new person
add_person("jones.jpg", "Jones Manuel", known_encodings, known_names)

# Identify faces in a test image
identify_faces("imagem_teste.jpeg", known_encodings, known_names)
identify_faces("imagem_teste2.jpeg", known_encodings, known_names)
identify_faces("novo_jones.jpg", known_encodings, known_names)
identify_faces("todos.jpg", known_encodings, known_names)
