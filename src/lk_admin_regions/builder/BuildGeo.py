import json
import os

import matplotlib.pyplot as plt
import topojson as tp
from utils import File, JSONFile, Log

from lk_admin_regions.corrections.CombineDCSAndHumData import \
    CombineDCSAndHumData
from lk_admin_regions.ground_truth.humdata.LKAAdminBoundariesXLSX import \
    LKAAdminBoundariesXLSX

log = Log("BuildGeo")


class BuildGeo:
    DIR_DATA = "data"
    DIR_DATA_GEO = os.path.join(DIR_DATA, "geo")
    GEO_PRECISION_DECIMAL_PLACES = 6

    MAX_FILE_SIZE_M = 25

    @staticmethod
    def round_geojson(geojson_data, ndigits):
        def round_coords(obj):
            if isinstance(obj, list):
                return [round_coords(x) for x in obj]
            if isinstance(obj, float):
                return round(obj, ndigits)
            return obj

        def round_geometry(geom):
            if not geom:
                return geom
            if geom.get("type") == "GeometryCollection":
                geom["geometries"] = [
                    round_geometry(g) for g in geom.get("geometries", [])
                ]
            elif "coordinates" in geom:
                geom["coordinates"] = round_coords(geom["coordinates"])
            return geom

        obj_type = geojson_data.get("type")
        if obj_type == "FeatureCollection":
            for feature in geojson_data.get("features", []):
                feature["geometry"] = round_geometry(feature.get("geometry"))
        elif obj_type == "Feature":
            geojson_data["geometry"] = round_geometry(
                geojson_data.get("geometry")
            )
        else:
            # bare geometry (Point, Polygon, GeometryCollection, etc.)
            round_geometry(geojson_data)

        return geojson_data

    @staticmethod
    def round_topojson(topojson_data, ndigits):
        def round_coords(obj):
            if isinstance(obj, list):
                return [round_coords(x) for x in obj]
            if isinstance(obj, float):
                return round(obj, ndigits)
            return obj

        # If quantized, arcs are integers with a transform; rounding floats
        # is a no-op and precision is already controlled by quantization.
        if "transform" not in topojson_data:
            if "arcs" in topojson_data:
                topojson_data["arcs"] = round_coords(topojson_data["arcs"])

        return topojson_data

    @classmethod
    def get_ent_xjson_path(
        cls, json_type, dir_name_simplified, ent_type_name
    ):
        dir_geo = os.path.join(
            cls.DIR_DATA_GEO, json_type, dir_name_simplified
        )
        os.makedirs(dir_geo, exist_ok=True)
        return os.path.join(
            dir_geo,
            f"{ent_type_name}s.{json_type}",
        )

    @classmethod
    def build_topojson(cls, ent_type_name, original_geojson_path):

        original_geojson_file = JSONFile(original_geojson_path)
        topojson_file = JSONFile(
            cls.get_ent_xjson_path("topojson", "original", ent_type_name)
        )

        original_geojson_file = JSONFile(original_geojson_path)
        geojson_data = original_geojson_file.read()
        topojson_data = tp.Topology(geojson_data).to_dict()
        topojson_data = cls.round_topojson(
            topojson_data, cls.GEO_PRECISION_DECIMAL_PLACES
        )
        topojson_file.write(topojson_data)
        p_compression = topojson_file.size / original_geojson_file.size
        log.info(
            f"✅ Wrote {topojson_file}" + f" ({p_compression:.1%} of geojson)"
        )
        return topojson_file

    @classmethod
    def build_simplified_topojson_for_size_spec(
        cls, ent_type_name, tolerance, precision_label, topojson_file
    ):

        topojson_data = topojson_file.read()
        simplified_topojson = (
            tp.Topology(topojson_data)
            .toposimplify(epsilon=tolerance)
            .to_dict()
        )

        simplified_topojson_file = JSONFile(
            cls.get_ent_xjson_path("topojson", precision_label, ent_type_name)
        )
        simplified_topojson = cls.round_topojson(
            simplified_topojson, cls.GEO_PRECISION_DECIMAL_PLACES
        )
        simplified_topojson_file.write(simplified_topojson)
        p_compression = simplified_topojson_file.size / topojson_file.size
        log.info(
            f"✅ Wrote {simplified_topojson_file}"
            + f" ({p_compression:.1%} of original topojson)"
        )
        return simplified_topojson

    @classmethod
    def build_simplified_geojson_for_size_spec(
        cls,
        simplified_topojson,
        original_geojson_path,
        precision_label,
        ent_type_name,
    ):
        simplified_geojson = json.loads(
            tp.Topology(simplified_topojson).to_geojson()
        )
        simplified_geojson = cls.round_geojson(
            simplified_geojson, cls.GEO_PRECISION_DECIMAL_PLACES
        )

        simplified_geojson_file = JSONFile(
            cls.get_ent_xjson_path("geojson", precision_label, ent_type_name)
        )
        simplified_geojson_file.write(simplified_geojson)

        size_before = os.path.getsize(original_geojson_path)
        size_after = os.path.getsize(simplified_geojson_file.path)
        compression_p = size_after / size_before

        log.info(
            f"✅ Wrote {simplified_geojson_file}"
            + f" ({compression_p:.1%} of original geojson)"
        )

        cls.build_image(
            ent_type_name,
            precision_label,
            compression_p,
            simplified_geojson_file.path,
        )

    @classmethod
    def build_raw_json(cls, ent_type_name, original_geojson_path):
        geojson_data = JSONFile(original_geojson_path).read()

        dir_raw = os.path.join(
            cls.DIR_DATA_GEO, "json", "original", f"{ent_type_name}s.json"
        )
        os.makedirs(dir_raw, exist_ok=True)

        n_written = 0
        for feature in geojson_data["features"]:
            properties = feature["properties"]
            ent_id = properties.get("id") or properties.get("hum_id")
            geometry = feature["geometry"]
            geom_type = geometry["type"]

            # Normalize to MultiPolygon structure: [polygon][ring][coord pair]
            if geom_type == "Polygon":
                multipolygon = geometry["coordinates"]
            elif geom_type == "MultiPolygon":
                multipolygon = geometry["coordinates"][0]
            else:
                log.warning(
                    f"Skipping unsupported geometry type"
                    f" {geom_type} for {ent_id}"
                )
                continue

            raw_path = os.path.join(dir_raw, f"{ent_id}.json")
            JSONFile(raw_path).write(multipolygon)
            n_written += 1

        log.info(f"✅ Wrote {n_written} raw JSON files to {dir_raw}")

    @classmethod
    def build_image(
        cls, ent_type_name, prevision_level, compression_p, geojson_path
    ):

        geojson_data = JSONFile(geojson_path).read()

        dir_images = os.path.join(cls.DIR_DATA_GEO, "images", prevision_level)
        os.makedirs(dir_images, exist_ok=True)
        image_path = os.path.join(dir_images, f"{ent_type_name}.png")

        fig, ax = plt.subplots(figsize=(10, 12))

        features = geojson_data["features"]
        cmap = plt.get_cmap("tab20")
        n = len(features)

        for i, feature in enumerate(features):
            geometry = feature["geometry"]
            geom_type = geometry["type"]
            color = cmap(i % cmap.N)

            if geom_type == "Polygon":
                polygons = [geometry["coordinates"]]
            elif geom_type == "MultiPolygon":
                polygons = geometry["coordinates"]
            else:
                log.warning(f"Skipping unsupported geometry type {geom_type}")
                continue

            for polygon in polygons:
                for ring in polygon:
                    # GeoJSON stores [lng, lat]; x=lng, y=lat
                    xs = [pt[0] for pt in ring]
                    ys = [pt[1] for pt in ring]
                    ax.fill(
                        xs,
                        ys,
                        facecolor=color,
                        edgecolor="black",
                        linewidth=0.3,
                        alpha=0.7,
                    )

        ax.set_aspect("equal")
        ax.set_title(
            f"{ent_type_name} ({n} regions) - {prevision_level}"
            + f" ({compression_p:.1%} of original geojson)"
        )
        ax.axis("off")

        fig.savefig(image_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        log.info(f"✅ Wrote {File(image_path)}")

    @classmethod
    def build_raw_json_geojson_and_topojson(
        cls,
        ent_type_name,
        original_geojson_path,
    ):

        cls.build_image(ent_type_name, "original", 1, original_geojson_path)
        cls.build_raw_json(ent_type_name, original_geojson_path)

        topojson_file = cls.build_topojson(
            ent_type_name, original_geojson_path
        )
        for tolerance, precision_label in [
            [0.00001, "e5_large"],
            [0.0001, "e4_medium"],
            [0.001, "e3_small"],
            [0.01, "e2_tiny"],
        ]:

            simplified_topojson = cls.build_simplified_topojson_for_size_spec(
                ent_type_name, tolerance, precision_label, topojson_file
            )

            cls.build_simplified_geojson_for_size_spec(
                simplified_topojson,
                original_geojson_path,
                precision_label,
                ent_type_name,
            )

    @classmethod
    def remap_properties(cls, ent_type_name, geojson_data):
        hum_to_dcs_map = CombineDCSAndHumData.get_hum_id_to_dcs_id_map(
            ent_type_name
        )
        if ent_type_name == "province":
            hum_id_key = "adm1_pcode"
        elif ent_type_name == "district":
            hum_id_key = "adm2_pcode"
        elif ent_type_name == "dsd":
            hum_id_key = "adm3_pcode"
        elif ent_type_name == "gnd":
            hum_id_key = "adm4_pcode"
        else:
            raise ValueError(f"Unknown ent_type_name: {ent_type_name}")

        new_features = []
        ent_data_list = JSONFile(
            os.path.join("data", "ents", f"{ent_type_name}s.json")
        ).read()
        ent_data_idx = {ent["id"]: ent for ent in ent_data_list}
        n_missing_dcs_id = 0
        for feature in geojson_data["features"]:
            properties = feature["properties"]
            hum_id = properties[hum_id_key]
            dcs_id = hum_to_dcs_map.get(hum_id)
            if dcs_id:
                data = ent_data_idx[dcs_id]
            else:
                data = dict(hum_id=hum_id)
                log.warning(f"Missing DCS ID for HUM ID: {hum_id}")
                n_missing_dcs_id += 1

            new_properties = data
            new_feature = dict(
                properties=new_properties, geometry=feature["geometry"]
            )
            new_features.append(new_feature)

        if n_missing_dcs_id > 0:
            log.error(f"{n_missing_dcs_id} features are missing DCS IDs.")

        geojson_data["features"] = new_features
        return geojson_data

    @classmethod
    def copy_original(cls, ent_type_name, level):
        geojson_path = LKAAdminBoundariesXLSX.get_ground_truth_geojson_path(
            level
        )
        os.makedirs(cls.DIR_DATA_GEO, exist_ok=True)
        new_geojson_path = cls.get_ent_xjson_path(
            "geojson", "original", ent_type_name
        )

        geojson_data = JSONFile(geojson_path).read()
        geojson_data = cls.remap_properties(
            ent_type_name, geojson_data
        )  # remap here
        geojson_data = cls.round_geojson(
            geojson_data, cls.GEO_PRECISION_DECIMAL_PLACES
        )  # round here

        JSONFile(new_geojson_path).write(
            geojson_data
        )  # write instead of copy
        log.info(f"✅ Wrote {File(new_geojson_path)}")

        return new_geojson_path

    @classmethod
    def build_all_for_ent(
        cls,
        ent_type_name,
        level,
    ):
        log.debug("-" * 64)
        log.debug(f"{level}. Building for {ent_type_name}...")
        log.debug("-" * 64)

        original_geojson_path = cls.copy_original(ent_type_name, level)
        cls.build_raw_json_geojson_and_topojson(
            ent_type_name,
            original_geojson_path,
        )

    @classmethod
    def cleanup_big_files(cls):
        os.system("find data -type f -size +20M -delete")

    @classmethod
    def build_all(cls):
        for (
            ent_type_name,
            level,
        ) in [
            ["province", 1],
            ["district", 2],
            ["dsd", 3],
            ["gnd", 4],
        ]:
            cls.build_all_for_ent(
                ent_type_name,
                level,
            )
            cls.cleanup_big_files()
