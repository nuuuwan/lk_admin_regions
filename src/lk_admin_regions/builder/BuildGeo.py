import json
import os
import shutil

import topojson as tp
from utils import File, JSONFile, Log

from lk_admin_regions.ground_truth.humdata.LKAAdminBoundariesXLSX import \
    LKAAdminBoundariesXLSX

log = Log("BuildGeo")


class BuildGeo:
    DIR_DATA = "data"
    DIR_DATA_GEO = os.path.join(DIR_DATA, "geo")

    ENT_CONFIG = [
        ["province", 1],
        # ["district", 2],
        # ["dsd", 3],
        # ["gnd", 4],
    ]

    MAX_FILE_SIZE_M = 25

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
    def build_topojson(cls, ent_type_name, level):
        original_geojson_path = (
            LKAAdminBoundariesXLSX.get_ground_truth_geojson_path(level)
        )
        topojson_file = JSONFile(
            cls.get_ent_xjson_path("topojson", "original", ent_type_name)
        )

        original_geojson_file = JSONFile(original_geojson_path)
        geojson_data = original_geojson_file.read()
        topojson_data = tp.Topology(geojson_data).to_dict()
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
        simplified_geojson = tp.Topology(simplified_topojson).to_geojson()

        simplified_geojson_file = JSONFile(
            cls.get_ent_xjson_path("geojson", precision_label, ent_type_name)
        )
        simplified_geojson_file.write(json.loads(simplified_geojson))

        size_before = os.path.getsize(original_geojson_path)
        size_after = os.path.getsize(simplified_geojson_file.path)
        compression_p = size_after / size_before

        log.info(
            f"✅ Wrote {simplified_geojson_file}"
            + f" ({compression_p:.1%} of original geojson)"
        )

    @classmethod
    def build_simplified_geojson_and_topojson(
        cls,
        ent_type_name,
        level,
    ):
        topojson_file = cls.build_topojson(ent_type_name, level)
        for tolerance, precision_label in [
            [0.0001, "high"],
            [0.001, "medium"],
            [0.01, "low"],
            [0.1, "minimal"],
        ]:

            simplified_topojson = cls.build_simplified_topojson_for_size_spec(
                ent_type_name, tolerance, precision_label, topojson_file
            )

            cls.build_simplified_geojson_for_size_spec(
                simplified_topojson,
                LKAAdminBoundariesXLSX.get_ground_truth_geojson_path(level),
                precision_label,
                ent_type_name,
            )

    @classmethod
    def HACK_delete_large_files(cls):
        os.system("find data -type f -size +25M -delete")

    @classmethod
    def copy_original(cls, ent_type_name, level):

        geojson_path = LKAAdminBoundariesXLSX.get_ground_truth_geojson_path(
            level
        )
        os.makedirs(cls.DIR_DATA_GEO, exist_ok=True)
        new_geojson_path = cls.get_ent_xjson_path(
            "geojson", "original", ent_type_name
        )

        if os.path.getsize(geojson_path) <= cls.MAX_FILE_SIZE_M * 1_000_000:

            shutil.copyfile(geojson_path, new_geojson_path)
            log.info(f"✅ Wrote {File(new_geojson_path)}")
        else:
            log.warning(
                f"⚠️ Not writing {new_geojson_path}."
                + f" {File(geojson_path)} is too large."
            )

    @classmethod
    def build_all_for_ent(
        cls,
        ent_type_name,
        level,
    ):
        cls.copy_original(ent_type_name, level)
        cls.build_simplified_geojson_and_topojson(
            ent_type_name,
            level,
        )

    @classmethod
    def build_all(cls):
        for (
            ent_type_name,
            level,
        ) in BuildGeo.ENT_CONFIG:
            log.debug("-" * 64)
            log.debug(f"{level}. Building for {ent_type_name}...")
            log.debug("-" * 64)
            cls.build_all_for_ent(
                ent_type_name,
                level,
            )


if __name__ == "__main__":
    BuildGeo.build_all()
