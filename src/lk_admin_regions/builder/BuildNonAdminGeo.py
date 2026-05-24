import os

import geopandas as gpd
from utils import Log

from lk_admin_regions.builder.BuildEnts import BuildEnts
from lk_admin_regions.corrections.CombineDCSAndHumData import \
    CombineDCSAndHumData

log = Log("BuildNonAdminGeo")


class BuildNonAdminGeo:

    @staticmethod
    def _props_for(pd_code, pd_idx):
        return pd_idx[pd_code]

    @classmethod
    def build_pd(cls):
        gnds = CombineDCSAndHumData.get_data_list()

        # gnd_pcode -> pd_code, for mapping onto the geometries
        gnd_to_pd_code = {
            row["hum_adm4_pcode"]: row["dcs_pd_code"] for row in gnds
        }

        # Aggregate PD properties from constituent GND rows
        # (area summed, centroid area-weighted — matches BuildEnts.build_parents)
        pds = BuildEnts.read("pd")
        pd_idx = {pd["code"]: pd for pd in pds}

        gnd_geoms = gpd.read_file(
            os.path.join(
                "data_ground_truth",
                "humdata_cod_ab_lka",
                "lka_admin_boundaries",
                "lka_admin4.geojson",
            )
        )

        gnd_key = (
            "adm4_pcode"  # confirm this matches the GeoJSON's GND id property
        )
        gnd_geoms["pd_code"] = gnd_geoms[gnd_key].map(gnd_to_pd_code)

        n_missing = gnd_geoms["pd_code"].isna().sum()
        if n_missing:
            log.warning(
                f"⚠️ {n_missing} GNDs have no pd_code; they will be excluded"
            )

        # Dissolve GND polygons into PDs
        pds = gnd_geoms.dissolve(by="pd_code")
        pds = pds.buffer(0)  # clean any slivers from the union
        pds = gpd.GeoDataFrame(
            geometry=pds
        ).reset_index()  # 'pd_code' + geometry

        # Replace properties with custom fields, aligned to dissolve order
        prop_rows = [cls._props_for(code, pd_idx) for code in pds["pd_code"]]
        prop_df = gpd.pd.DataFrame(prop_rows)
        pds = gpd.GeoDataFrame(
            prop_df, geometry=pds.geometry.values, crs=pds.crs
        )

        out_path = os.path.join(
            "data", "geo", "geojson", "original", "pds.geojson"
        )
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        pds.to_file(out_path, driver="GeoJSON")
        log.info(f"✅ Wrote {len(pds)} PDs to {out_path}")

    @classmethod
    def build_all(cls):
        cls.build_pd()
