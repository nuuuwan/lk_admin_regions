import os
import shutil

from utils import File, JSONFile, Log

from lk_admin_regions.build_ents.BuildEnts import BuildEnts

log = Log("ModuleName")


class BuildGeo:
    DIR_DATA = BuildEnts.DIR_DATA
    DIR_DATA_GEO = os.path.join(DIR_DATA, "geo")
    MAX_FILE_SIZE_M = 25

    @classmethod
    def get_ent_geojson_path(cls, ent_type_name):
        return os.path.join(
            cls.DIR_DATA_GEO,
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
            new_geojson_path = cls.get_ent_geojson_path(ent_type_name)
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

            cls.geojson_to_multipolygon(ent_type_name, level, id_len)

    @classmethod
    def geojson_to_multipolygon(cls, ent_type_name, level, id_len):
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

            dir_data_geo_ents = os.path.join(
                cls.DIR_DATA_GEO, f"{ent_type_name}s"
            )
            os.makedirs(dir_data_geo_ents, exist_ok=True)
            output_path = os.path.join(dir_data_geo_ents, f"{ent_id}.json")
            json_file = JSONFile(output_path)
            json_file.write(flattened_coordinates)
            log.info(f"✅ Wrote {json_file}")
