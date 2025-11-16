import os

import geopandas as gpd
from utils import Log, TSVFile

from lk_admin_regions.ground_truth.GNDListFinalXLSX import GNDListFinalXLSX

log = Log("SubnatAdminBounds")


class SubnatAdminBounds:
    PATH = os.path.join(
        "data_ground_truth",
        "subnational_administrative_boundaries",
        "lka_admbnda_adm4_slsd_20220816.shp",
    )
    DATA_PATH = os.path.join("data", "gnd-geo.tsv")

    @classmethod
    def to_list_of_dicts(cls):
        gdf = gpd.read_file(cls.PATH)
        return gdf.to_dict(orient="records")

    @classmethod
    def get_d_gnd_from_row(cls, d):
        gnd_id = d["ADM4_PCODE"].replace("LK", "LK-")
        gnd_name = d["ADM4_EN"]
        area_km = round(d["Shape_Area"] * 65_610 / 5.40777604693218, 3)
        return dict(gnd_id=gnd_id, gnd_name=gnd_name, area_km=area_km)

    @classmethod
    def build_gnd_table(cls):
        gnd_list = [cls.get_d_gnd_from_row(d) for d in cls.to_list_of_dicts()]

        area_km = sum(d["area_km"] for d in gnd_list)
        log.debug(f"{area_km=:,}")

        gnd_path = os.path.join("data", "gnd-geo.tsv")
        gnd_file = TSVFile(gnd_path)
        gnd_file.write(gnd_list)
        log.info(f"Wrote {len(gnd_list):,} rows to {gnd_file}")

    @classmethod
    def get_data_list(cls) -> list[dict]:
        return TSVFile(cls.DATA_PATH).read()

    @classmethod
    def get_idx(cls):
        return {d["gnd_id"]: d for d in cls.get_data_list()}

    @classmethod
    def compare_to_gnd_list_final(cls):
        idx_from_glf = GNDListFinalXLSX.get_idx()
        idx_from_sab = cls.get_idx()
        ids_from_glf = set(idx_from_glf.keys())
        ids_from_sab = set(idx_from_sab.keys())
        glf_minus_sab = ids_from_glf - ids_from_sab
        if glf_minus_sab:
            log.warning(
                f"⚠️ {len(glf_minus_sab)} GNDListFinal but not in SubnatAdminBounds"
            )
            for gnd_id in sorted(glf_minus_sab)[:10]:
                gnd_name = idx_from_glf[gnd_id]["gnd_name"]
                log.debug(f"  - {gnd_id} {gnd_name}")
        else:
            log.info("✅ All GND IDs in GNDListFinal are in SubnatAdminBounds")

        sab_minus_glf = ids_from_sab - ids_from_glf
        if sab_minus_glf:
            log.warning(
                f"⚠️ {len(sab_minus_glf)} In SubnatAdminBounds but not in GNDListFinal"
            )
            for gnd_id in sorted(sab_minus_glf)[:10]:
                gnd_name = idx_from_sab[gnd_id]["gnd_name"]
                log.debug(f"  - {gnd_id} {gnd_name}")
        else:
            log.info("✅ All GND IDs in SubnatAdminBounds are in GNDListFinal")


if __name__ == "__main__":
    SubnatAdminBounds.build_gnd_table()
    SubnatAdminBounds.compare_to_gnd_list_final()
