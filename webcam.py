import cv2
import torch
from ultralytics import YOLO

# Use Apple Silicon MPS GPU if available, otherwise CPU
_DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

# Load YOLO model once, on GPU
model = YOLO("yolo11n.pt")
model.to(_DEVICE)


def generate_frames():
    """
    OpenCV frame generator that captures live frames from the default webcam (0),
    runs YOLOv11 animal detection, annotates the frames, and streams them.
    """
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
            frame_bytes = buffer.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n'
                + frame_bytes +
                b'\r\n'
            )
    finally:
        camera.release()