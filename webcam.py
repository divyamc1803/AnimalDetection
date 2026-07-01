import cv2
from ultralytics import YOLO

# Load YOLO model once
model = YOLO("yolo11n.pt")


def generate_frames():

    camera = cv2.VideoCapture(0)

    try:

        while True:

            success, frame = camera.read()

            if not success:
                break

            results = model.predict(
                source=frame,
                conf=0.5,
                verbose=False
            )

            annotated_frame = results[0].plot()

            ret, buffer = cv2.imencode(".jpg", annotated_frame)

            frame = buffer.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n'
                + frame +
                b'\r\n'
            )

    finally:

        camera.release()