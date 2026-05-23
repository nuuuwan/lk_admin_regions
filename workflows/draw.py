import json
import os
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
import topojson
from gig import Ent, EntType


def draw1(dsd_id):
    gnds = Ent.list_from_type(EntType.GND)
    gnds_for_dsd = [g for g in gnds if g.id[:7] == dsd_id]

    colors = plt.cm.tab20.colors

    plt.close()
    ax = plt.gca()
    for i, g in enumerate(gnds_for_dsd):
        geo = g.geo()
        geo.plot(ax=ax, color=colors[i % len(colors)])

    os.makedirs("images", exist_ok=True)
    plt.savefig(os.path.join("images", f"{dsd_id}.draw1.png"))
    print(f"Saved {dsd_id}.draw1.png")
    plt.close()


def draw2(dsd_id):
    topo_path = os.path.join(
        "data", "geo", "topojson", "original", "gnds.topojson"
    )
    with open(topo_path) as f:
        topo_data = json.load(f)
    topo = topojson.Topology(topo_data)
    gdf = topo.to_gdf()
    gdf_dsd = gdf[gdf["adm3_pcode"] == dsd_id.replace("-", "")]

    colors = plt.cm.tab20.colors

    plt.close()
    ax = plt.gca()
    for i, (_, row) in enumerate(gdf_dsd.iterrows()):
        gpd.GeoSeries([row.geometry]).plot(
            ax=ax, color=colors[i % len(colors)]
        )

    os.makedirs("images", exist_ok=True)
    plt.savefig(os.path.join("images", f"{dsd_id}.draw2.png"))
    print(f"Saved {dsd_id}.draw2.png")
    plt.close()


def draw(dsd_id):
    draw1(dsd_id)
    draw2(dsd_id)


if __name__ == "__main__":
    draw(sys.argv[1])
