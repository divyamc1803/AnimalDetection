import matplotlib
matplotlib.use("Agg")      # Use a non-GUI backend

import matplotlib.pyplot as plt
import numpy as np


def generate_bar_graph(animal_count):

    if not animal_count:
        return None

    animals = np.array(list(animal_count.keys()))
    counts = np.array(list(animal_count.values()))

    plt.figure(figsize=(8, 5))

    plt.bar(
        animals,
        counts
    )

    plt.title("Animal Detection Summary")
    plt.xlabel("Detected Classes")
    plt.ylabel("Count")

    plt.tight_layout()

    import os

    os.makedirs("static/graphs", exist_ok=True)

    filename = "static/graphs/animal_detection_graph.png"

    plt.savefig(filename)

    plt.close()

    return "/static/graphs/animal_detection_graph.png"