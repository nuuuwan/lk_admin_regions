import os

import geopandas as gpd
from utils import Log

from lk_admin_regions.builder.BuildEnts import BuildEnts
from lk_admin_regions.builder.BuildGeo import BuildGeo
from lk_admin_regions.builder.BuildNonAdminEnts import BuildNonAdminEnts
from lk_admin_regions.corrections.CombineDCSAndHumData import \
    CombineDCSAndHumData

log = Log("BuildNonAdminGeo")


class BuildNonAdminGeo:

    @classmethod
    def build_parent_original(
        cls,
        parent_type,
        gnd_to_parent,
        parent_code_field,
    ):
        hum_pcode_key = f"hum_adm4_pcode"
        gnd_geom_key = "adm4_pcode"

        gnds = CombineDCSAndHumData.get_data_list()

        # gnd_pcode -> parent_code, for mapping onto the geometries
        gnd_to_parent_code = {
            gnd[hum_pcode_key]: gnd_to_parent(gnd) for gnd in gnds
        }

        # Aggregate parent properties from constituent GND rows
        # (area summed, centroid area-weighted — matches
        # BuildEnts.build_parents)
        parents = BuildEnts.read(parent_type)
        parent_idx = {parent[parent_code_field]: parent for parent in parents}

        gnd_geoms = gpd.read_file(
            os.path.join(
                "data_ground_truth",
                "humdata_cod_ab_lka",
                "lka_admin_boundaries",
                "lka_admin4.geojson",
            )
        )

        gnd_geoms[parent_code_field] = gnd_geoms[gnd_geom_key].map(
            gnd_to_parent_code
        )

        n_missing = gnd_geoms[parent_code_field].isna().sum()
        if n_missing:
            log.warning(
                f"⚠️ {n_missing} GNDs have no {parent_code_field}; "
                "they will be excluded"
            )

        # Dissolve GND polygons into parents
        parents_geo = gnd_geoms.dissolve(by=parent_code_field)
        parents_geo = parents_geo.buffer(
            0
        )  # clean any slivers from the union
        parents_geo = gpd.GeoDataFrame(
            geometry=parents_geo
        ).reset_index()  # parent_code_field + geometry

        # Replace properties with custom fields, aligned to dissolve order
        prop_rows = [
            parent_idx[code] for code in parents_geo[parent_code_field]
        ]
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
        district_to_ed = BuildNonAdminEnts.get_distrct_to_ed()
        for parent_type, gnd_to_parent, parent_code_field in [
            ("pd", lambda gnd: gnd["dcs_pd_code"], "pd_code"),
            (
                "ed",
                lambda gnd: district_to_ed[gnd["dcs_district_id"]],
                "id",
            ),
            ("lg", lambda gnd: gnd["dcs_lg_id"], "id"),
        ]:
            original_geojson_path = cls.build_parent_original(
                parent_type, gnd_to_parent, parent_code_field
            )
            BuildGeo.build_simplified_geojson_and_topojson(
                parent_type,
                original_geojson_path,
            )
