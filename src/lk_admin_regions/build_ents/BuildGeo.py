import os
import shutil

from shapely.geometry import mapping, shape
from utils import File, JSONFile, Log

from lk_admin_regions.build_ents.BuildEnts import BuildEnts

log = Log("ModuleName")


class BuildGeo:
    DIR_DATA = BuildEnts.DIR_DATA
    DIR_DATA_GEO = os.path.join(DIR_DATA, "geo")
    MAX_FILE_SIZE_M = 25

    @classmethod
    def get_ent_geojson_path(cls, dir_name_simplified, ent_type_name):
        dir_geo = os.path.join(cls.DIR_DATA_GEO, dir_name_simplified)
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
            new_geojson_path = cls.get_ent_geojson_path(
                "original", ent_type_name
            )
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

            # cls.build_multipolygon_json(ent_type_name, level, id_len)
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

            dir_data_geo_ents = os.path.join(
                cls.DIR_DATA_GEO, f"{ent_type_name}s"
            )

            json_file = JSONFile(
                os.path.join(dir_data_geo_ents, f"{ent_id}.json")
            )
            json_file.write(flattened_coordinates)
            log.info(f"✅ Wrote {json_file}")

    @classmethod
    def build_small_geojson(cls, ent_type_name, level, tolerance=0.001):

        for minus_log10_tolerance in [2, 3, 4]:
            tolerance = 10 ** (-minus_log10_tolerance)
            geojson_path = cls.get_ground_truth_geojson_path(level)
            geojson_data = JSONFile(geojson_path).read()

            simplified_features = []
            for feature in geojson_data.get("features", []):
                geometry = feature.get("geometry", {})
                shapely_geom = shape(geometry)
                simplified_geom = shapely_geom.simplify(
                    tolerance, preserve_topology=True
                )

                feature["geometry"] = mapping(simplified_geom)
                simplified_features.append(feature)

            simplified_geojson = {
                "type": "FeatureCollection",
                "features": simplified_features,
            }

            simplified_geojson_file = JSONFile(
                cls.get_ent_geojson_path(
                    f"simplified{minus_log10_tolerance}", ent_type_name
                )
            )
            simplified_geojson_file.write(simplified_geojson)

            size_before = os.path.getsize(geojson_path)
            size_after = os.path.getsize(simplified_geojson_file.path)
            compression_p = size_after / size_before

            if simplified_geojson_file.size > cls.MAX_FILE_SIZE_M * 1_000_000:
                log.warning(
                    f"⚠️  Not writing {simplified_geojson_file}."
                    + f" Size {simplified_geojson_file.size / 1_000_000:.1f}MB"
                    + " is too large even after simplification"
                    + f" with tolerance={tolerance}."
                )
                os.remove(simplified_geojson_file.path)
            else:
                log.info(
                    f"✅ Wrote {simplified_geojson_file}"
                    + f" ({compression_p:.1%} of original)"
                )
