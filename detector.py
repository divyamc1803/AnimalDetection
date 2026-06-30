import csv
from ultralytics import YOLO


def detect_animals(source="images"):

    # Load YOLO model
    model = YOLO("yolo11n.pt")

    # Run prediction
    results = model.predict(
        source=source,
        save=False,
        show=False,
        conf=0.5
    )

    # Dictionary to count animals
    animal_count = {}

    # Store detections
    detections = []

    # Summary variables
    total_images = 0
    total_animals = 0
    total_confidence = 0
    total_time = 0

    # Create CSV
    csv_file = open("results.csv", "w", newline="")
    writer = csv.writer(csv_file)

    writer.writerow([
        "Image",
        "Prediction",
        "Confidence",
        "Status",
        "Time(ms)",
        "Explanation"
    ])

    print("-" * 110)
    print(
        f"{'Image':<20}"
        f"{'Prediction':<15}"
        f"{'Confidence':<15}"
        f"{'Status':<15}"
        f"{'Time(ms)':<12}"
        "Explanation"
    )
    print("-" * 110)

    # Process every image
    for result in results:

        filename = result.path.split("/")[-1]

        total_images += 1

        time = result.speed["inference"]
        total_time += time

        # No detections
        if len(result.boxes) == 0:

            print(
                f"{filename:<20}"
                f"{'None':<15}"
                f"{'0%':<15}"
                f"{'None':<15}"
                f"{time:<12.1f}"
                f"No animal detected"
            )

            writer.writerow([
                filename,
                "None",
                "0%",
                "None",
                f"{time:.1f}",
                "No animal detected"
            ])

            continue

        # Detect every animal
        for box in result.boxes:

            cls = int(box.cls[0])
            name = result.names[cls]
            conf = float(box.conf[0]) * 100

            # Confidence Status
            if conf >= 95:
                status = "Excellent"
            elif conf >= 85:
                status = "Good"
            elif conf >= 70:
                status = "Moderate"
            else:
                status = "Low"

            # Count animals
            if name in animal_count:
                animal_count[name] += 1
            else:
                animal_count[name] = 1

            total_animals += 1
            total_confidence += conf

            # Save detections
            detections.append({
                "image": filename,
                "animal": name,
                "confidence": f"{conf:.2f}%",
                "status": status,
                "time": f"{time:.1f} ms"
            })

            print(
                f"{filename:<20}"
                f"{name:<15}"
                f"{conf:>6.2f}%{'':8}"
                f"{status:<15}"
                f"{time:<12.1f}"
                f"Detected {name}"
            )

            writer.writerow([
                filename,
                name,
                f"{conf:.2f}%",
                status,
                f"{time:.1f}",
                f"Detected {name}"
            ])

    # Print animal count
    print("\n")
    print("-" * 40)
    print(f"{'Animal':<20}{'Count'}")
    print("-" * 40)

    for animal, count in animal_count.items():
        print(f"{animal:<20}{count}")

    print("-" * 40)

    # Calculate averages
    average_confidence = (
        total_confidence / total_animals
        if total_animals else 0
    )

    average_time = (
        total_time / total_images
        if total_images else 0
    )

    # Print summary
    print("\n")
    print("=" * 55)
    print("PROJECT SUMMARY")
    print("=" * 55)
    print(f"Total Images Processed : {total_images}")
    print(f"Total Animals Detected : {total_animals}")
    print(f"Unique Animal Types    : {len(animal_count)}")
    print(f"Average Confidence     : {average_confidence:.2f}%")
    print(f"Average Inference Time : {average_time:.2f} ms")
    print("=" * 55)

    # Close CSV
    csv_file.close()

    print("\nCSV report saved successfully as 'results.csv'")

    # Summary dictionary
    summary = {
        "images": total_images,
        "animals": total_animals,
        "unique": len(animal_count),
        "confidence": f"{average_confidence:.2f}%",
        "time": f"{average_time:.2f} ms"
    }

    return {
        "detections": detections,
        "animal_count": animal_count,
        "summary": summary
    }


if __name__ == "__main__":
    detect_animals()