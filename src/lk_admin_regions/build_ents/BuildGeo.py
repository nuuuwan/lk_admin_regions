import json
import os
import shutil

import topojson as tp
from utils import File, JSONFile, Log

from lk_admin_regions.build_ents.BuildEnts import BuildEnts

log = Log("ModuleName")


class BuildGeo:
    DIR_DATA = BuildEnts.DIR_DATA
    DIR_DATA_GEO = os.path.join(DIR_DATA, "geo")

    MAX_FILE_SIZE_M = 25

    @classmethod
    def get_ent_xjson_path(cls, json_type, dir_name_simplified, ent_type_name):
        dir_geo = os.path.join(
            cls.DIR_DATA_GEO, json_type, dir_name_simplified
        )
        os.makedirs(dir_geo, exist_ok=True)
        return os.path.join(
            dir_geo,
            f"{ent_type_name}s.geojson",
        )

    @classmethod
    def get_ground_truth_geojson_path(cls, level):
        return os.path.join(
            "data_ground_truth",
            "humdata_cod_ab_lka",
            "lka_admin_boundaries",
            f"lka_admin{level}.geojson",
        )

    @classmethod
    def build_all(cls):
        for ent_type_name, level, id_len in BuildEnts.ENT_CONFIG:
            geojson_path = cls.get_ground_truth_geojson_path(level)
            os.makedirs(cls.DIR_DATA_GEO, exist_ok=True)
            new_geojson_path = cls.get_ent_xjson_path(
                "geojson", "original", ent_type_name
            )
            if not os.path.exists(new_geojson_path):
                if (
                    os.path.getsize(geojson_path)
                    <= cls.MAX_FILE_SIZE_M * 1_000_000
                ):

                    shutil.copyfile(geojson_path, new_geojson_path)
                    log.info(f"✅ Wrote {File(new_geojson_path)}")
                else:
                    log.warning(
                        f"⚠️ Not writing {new_geojson_path}."
                        + f" {File(geojson_path)} is too large."
                    )

            cls.build_multipolygon_json(ent_type_name, level, id_len)
            cls.build_small_geojson(ent_type_name, level)

    @classmethod
    def build_multipolygon_json(cls, ent_type_name, level, id_len):
        geojson_path = cls.get_ground_truth_geojson_path(level)
        geojson_data = JSONFile(geojson_path).read()

        for feature in geojson_data.get("features", []):
            ent_id = BuildEnts.get_id(
                feature.get("properties", {}), level, id_len
            )
            geometry = feature.get("geometry", {})
            coordinates = geometry.get("coordinates", [])

            flattened_coordinates = []
            if geometry.get("type") == "MultiPolygon":
                for polygon in coordinates:
                    for ring in polygon:
                        flattened_coordinates.append(
                            [[point[0], point[1]] for point in ring]
                        )
            elif geometry.get("type") == "Polygon":
                for ring in coordinates:
                    flattened_coordinates.append(
                        [[point[0], point[1]] for point in ring]
                    )

            dir_data_geo_json_ents = cls.get_ent_xjson_path(
                "json", "original", ent_type_name
            )
            os.makedirs(dir_data_geo_json_ents, exist_ok=True)

            json_file = JSONFile(
                os.path.join(dir_data_geo_json_ents, f"{ent_id}.json")
            )
            if not json_file.exists:
                json_file.write(flattened_coordinates)
                log.info(f"✅ Wrote {json_file}")

    @classmethod
    def build_small_geojson(cls, ent_type_name, level):
        for [tolerance, label] in [
            [0.0001, "small"],
            [0.001, "smaller"],
            [0.01, "smallest"],
            [0.1, "smallestest"],
        ]:

            original_geojson_path = cls.get_ground_truth_geojson_path(level)
            topojson_file = JSONFile(
                cls.get_ent_xjson_path("topojson", label, ent_type_name)
            )

            if not topojson_file.exists:
                original_geojson_file = JSONFile(original_geojson_path)
                geojson_data = original_geojson_file.read()
                topojson_data = tp.Topology(geojson_data).to_dict()
                topojson_file.write(topojson_data)
                p_compression = topojson_file.size / original_geojson_file.size
                log.info(
                    f"✅ Wrote {topojson_file}"
                    + f" ({p_compression:.1%} of geojson)"
                )

            topojson_data = topojson_file.read()
            simplified_topojson = (
                tp.Topology(topojson_data)
                .toposimplify(epsilon=tolerance)
                .to_dict()
            )

            simplified_geojson = tp.Topology(simplified_topojson).to_geojson()

            simplified_geojson_file = JSONFile(
                cls.get_ent_xjson_path("geojson", label, ent_type_name)
            )

            simplified_geojson_file.write(json.loads(simplified_geojson))

            size_before = os.path.getsize(original_geojson_path)
            size_after = os.path.getsize(simplified_geojson_file.path)
            compression_p = size_after / size_before

            log.info(
                f"✅ Wrote {simplified_geojson_file}"
                + f" ({compression_p:.1%} of original)"
            )
