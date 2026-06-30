from ultralytics import YOLO

# Load the model
model = YOLO("yolo11n.pt")  # or your best.pt

# Test on one image
results = model("image.jpg", save=True)

print("Detection completed successfully!")