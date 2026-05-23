import sys

import matplotlib.pyplot as plt
from gig import Ent, EntType


def draw(dsd_id):
    gnds = Ent.list_from_type(EntType.GND)
    gnds_for_dsd = [g for g in gnds if g.id[:7] == dsd_id]

    colors = plt.cm.tab20.colors

    plt.close()
    ax = plt.gca()
    for i, g in enumerate(gnds_for_dsd):
        geo = g.geo()
        geo.plot(ax=ax, color=colors[i % len(colors)])

    plt.show()


if __name__ == "__main__":
    draw(sys.argv[1])
