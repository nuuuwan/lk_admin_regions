"""
One-off script to replace the single "Kalmunai" DSD in lka_admin3.geojson with
two separate DSDs sourced from the Department of Census and Statistics (DCS):

  LK-5221.json  →  Kalmunai North  (adm3_pcode: LK5221)
  LK-5224.json  →  Kalmunai        (adm3_pcode: LK5224)

The existing "Kalmunai" feature (adm3_pcode: LK5221) is removed and both new
features are inserted at the same position.
"""

import json
import os

DIR_REPO = os.path.dirname(os.path.dirname(__file__))
PATH_GEOJSON = os.path.join(
    DIR_REPO,
    "data_ground_truth",
    "humdata_cod_ab_lka",
    "lka_admin_boundaries.geojson",
    "lka_admin3.geojson",
)
PATH_DCS_5221 = os.path.join(
    DIR_REPO, "data_ground_truth", "dcs_old_kalmunai", "LK-5221.json"
)
PATH_DCS_5224 = os.path.join(
    DIR_REPO, "data_ground_truth", "dcs_old_kalmunai", "LK-5224.json"
)
PATH_OUT = os.path.join(
    DIR_REPO,
    "data_temp",
    "lka_admin3.kalmunai.geojson",
)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def make_feature(base_props, pcode, name, coordinates):
    """Build a GeoJSON Feature from an existing feature's properties."""
    props = dict(base_props)
    props["adm3_name"] = name
    props["adm3_pcode"] = pcode
    # Clear Sinhala/Tamil/other name fields – unknown for new entries
    props["adm3_name1"] = None
    props["adm3_name2"] = None
    props["adm3_name3"] = None
    # Area and centroid are not recalculated here
    props["area_sqkm"] = None
    props["center_lat"] = None
    props["center_lon"] = None
    return {
        "type": "Feature",
        "properties": props,
        "geometry": {
            "type": "Polygon",
            "coordinates": coordinates,
        },
    }


def main():
    geojson = load_json(PATH_GEOJSON)
    coords_5221 = load_json(PATH_DCS_5221)  # list of rings for Kalmunai North
    coords_5224 = load_json(PATH_DCS_5224)  # list of rings for Kalmunai

    new_features = []
    replaced = False

    for feat in geojson["features"]:
        if feat["properties"].get("adm3_name") == "Kalmunai":
            if replaced:
                # Skip any duplicate Kalmunai features
                continue
            base_props = feat["properties"]
            new_features.append(
                make_feature(
                    base_props, "LK5221", "Kalmunai North", coords_5221
                )
            )
            new_features.append(
                make_feature(base_props, "LK5224", "Kalmunai", coords_5224)
            )
            replaced = True
        else:
            new_features.append(feat)

    if not replaced:
        raise ValueError(
            "No feature with adm3_name='Kalmunai' found in GeoJSON."
        )

    original_count = len(geojson["features"])
    geojson["features"] = new_features

    with open(PATH_OUT, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"Done. Feature count: {len(new_features)} (was {original_count})")
    print(f"Written to: {PATH_OUT}")


if __name__ == "__main__":
    main()
