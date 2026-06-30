import cv2
from ultralytics import YOLO

# Load YOLO model once
model = YOLO("yolo11n.pt")

# Open webcam
camera = cv2.VideoCapture(0)


def generate_frames():

    while True:

        success, frame = camera.read()

        if not success:
            break

        # Run YOLO
        results = model.predict(
            source=frame,
            conf=0.5,
            verbose=False
        )

        # Draw bounding boxes
        annotated_frame = results[0].plot()

        # Convert image to JPEG
        ret, buffer = cv2.imencode(".jpg", annotated_frame)

        frame = buffer.tobytes()

        # Send frame to browser
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + frame +
            b'\r\n'
        )