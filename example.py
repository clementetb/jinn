import numpy as np
import matplotlib.pyplot as plt

from genius_template_importer import import_template
from bidding import generate_bids
from helpers import is_pareto_efficient


if __name__ == "__main__":
    template1 = import_template("templates/Camera/camera_buyer_utility.xml")
    template2 = import_template("templates/Camera/camera_seller_utility.xml")

    bids = generate_bids(template1, template2, 0.05)

    points = bids[:, -2:]
    pareto_points = is_pareto_efficient(points, return_mask=True)

    px = points[:, 0]
    py = np.ma.masked_array(points[:, 1], mask=~pareto_points)

    pareto_points = np.ma.masked_array(points, mask=np.vstack(
        [~pareto_points, ~pareto_points]).transpose()).compressed().reshape(-1, 2)

    pareto_sorted = []
    for i in range(pareto_points.shape[0]):
        pareto_sorted.append((pareto_points[i, 0], pareto_points[i, 1]))

    pareto_sorted = sorted(pareto_sorted, key=lambda x: x[0])
    pareto_sorted = np.array(pareto_sorted)

    # drawing
    plt.plot(points[:, 0], points[:, 1], 'bo', ms=1)
    plt.plot(pareto_sorted[:, 0], pareto_sorted[:, 1], '-r^')
    plt.axis([-.1, 1.1, -.1, 1.1])
    plt.show()

    plt.savefig('example.png')
