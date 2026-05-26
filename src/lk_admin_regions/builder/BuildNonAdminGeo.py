import os

import geopandas as gpd
from utils import Log

from lk_admin_regions.builder.BuildEnts import BuildEnts
from lk_admin_regions.builder.BuildGeo import BuildGeo
from lk_admin_regions.builder.BuildGNDEnt import BuildGNDEnt

log = Log("BuildNonAdminGeo")


class BuildNonAdminGeo:

    @classmethod
    def build_parent_original(
        cls,
        parent_type,
        child_level,
    ):
        log.debug("-" * 64)
        log.debug(f"Building for {parent_type}...")
        log.debug("-" * 64)
        gnds = BuildGNDEnt.read_denormalized_gnds()

        parent_id_key = f"{parent_type}_id"
        child_id_key = f"hum_adm{child_level}_pcode"
        child_to_parent_code = {
            gnd[child_id_key]: gnd[parent_id_key] for gnd in gnds
        }

        parents = BuildEnts.read(parent_type)
        parent_idx = {parent["id"]: parent for parent in parents}

        child_geoms = gpd.read_file(
            os.path.join(
                "data_ground_truth",
                "humdata_cod_ab_lka",
                "lka_admin_boundaries",
                f"lka_admin{child_level}.geojson",
            )
        )

        child_geoms[parent_id_key] = child_geoms[
            f"adm{child_level}_pcode"
        ].map(child_to_parent_code)

        n_missing = child_geoms[parent_id_key].isna().sum()
        if n_missing:
            log.warning(
                f"⚠️ {n_missing} children have no {parent_id_key}; "
                "they will be excluded"
            )

        # Dissolve GND polygons into parents
        parents_geo = child_geoms.dissolve(by=parent_id_key)
        parents_geo = parents_geo.buffer(
            0
        )  # clean any slivers from the union
        parents_geo = gpd.GeoDataFrame(
            geometry=parents_geo
        ).reset_index()  # parent_id_key + geometry

        # Replace properties with custom fields, aligned to dissolve order
        prop_rows = [parent_idx[code] for code in parents_geo[parent_id_key]]
        prop_df = gpd.pd.DataFrame(prop_rows)
        parents_geo = gpd.GeoDataFrame(
            prop_df, geometry=parents_geo.geometry.values, crs=parents_geo.crs
        )

        original_geojson_path = os.path.join(
            "data", "geo", "geojson", "original", f"{parent_type}s.geojson"
        )
        os.makedirs(os.path.dirname(original_geojson_path), exist_ok=True)
        parents_geo.to_file(original_geojson_path, driver="GeoJSON")
        log.info(
            f"✅ Wrote {len(parents_geo)} {parent_type}s "
            f"to {original_geojson_path}"
        )

        return original_geojson_path

    @classmethod
    def build_all(cls):
        for parent_type, child_level in [
            ["country", 0],
            ["ed", 2],
            ["pd", 4],
            ["lg", 4],
        ]:
            original_geojson_path = cls.build_parent_original(
                parent_type,
                child_level,
            )
            BuildGeo.build_raw_json_geojson_and_topojson(
                parent_type,
                original_geojson_path,
            )
            BuildGeo.cleanup_big_files()
            break
