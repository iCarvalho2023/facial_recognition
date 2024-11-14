import face_recognition
import binascii

# Load the image
image = face_recognition.load_image_file("pessoa1.jpeg")
encoding = face_recognition.face_encodings(image)[0]  # Assuming the first face in the image

# Convert the encoding to a hexadecimal string (binascii)
encoding_hex = binascii.hexlify(encoding.tobytes()).decode('utf-8')  # Convert the encoding to hex

print(encoding_hex)