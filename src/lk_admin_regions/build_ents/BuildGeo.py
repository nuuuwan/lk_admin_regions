import os
import shutil

from utils import File, Log

from lk_admin_regions.build_ents.BuildEnts import BuildEnts

log = Log("ModuleName")


class BuildGeo:
    DIR_DATA = BuildEnts.DIR_DATA
    DIR_DATA_GEO = os.path.join(DIR_DATA, "geo")

    @classmethod
    def build_all(cls):
        for ent_type_name, level in [
            ("country", 0),
            ("province", 1),
            ("district", 2),
            ("dsd", 3),
        ]:
            geojson_path = os.path.join(
                "data_ground_truth",
                "humdata_cod_ab_lka",
                "lka_admin_boundaries",
                f"lka_admin{level}.geojson",
            )

            os.makedirs(cls.DIR_DATA_GEO, exist_ok=True)
            new_geojson_path = os.path.join(
                cls.DIR_DATA_GEO,
                f"{ent_type_name}s.geojson",
            )

            shutil.copyfile(geojson_path, new_geojson_path)
            log.info(f"Wrote {File(new_geojson_path)}")
