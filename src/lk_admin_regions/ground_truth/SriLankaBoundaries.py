import os

import geopandas as gpd
from rapidfuzz import fuzz
from utils import Log, TSVFile

from lk_admin_regions.ground_truth.GNDListFinalXLSX import GNDListFinalXLSX

log = Log("SriLankaBoundaries")


class SriLankaBoundaries:
    PATH = os.path.join(
        "data_ground_truth",
        "sri_lanka_boundaries",
        "_local.gnd.geojson",
    )
    DATA_PATH = os.path.join("data", "gnd-geo2.tsv")

    @classmethod
    def to_list_of_dicts(cls):
        gdf = gpd.read_file(cls.PATH)
        print(gdf.columns)
        print(gdf.iloc[99].to_dict())
        return gdf.to_dict(orient="records")

    @classmethod
    def get_d_gnd_from_row(cls, d):
        gnd_id = f"LK-{int(d['admin_code'])}"
        if len(gnd_id) != 10:
            return None
        gnd_name = d["gnd_name"]
        area_km = round(d["st_area(shape)"] * 65_610 / 5.40777604693218, 3)
        return dict(
            gnd_id=gnd_id,
            gnd_name=gnd_name,
            area_km=area_km,
            gnd_no_census=d["gnd_no_census"],
        )

    @classmethod
    def build_gnd_table(cls):
        gnd_list = [cls.get_d_gnd_from_row(d) for d in cls.to_list_of_dicts()]
        gnd_list = [d for d in gnd_list if d is not None]

        area_km = sum(d["area_km"] for d in gnd_list)
        log.debug(f"{area_km=:,}")

        gnd_file = TSVFile(cls.DATA_PATH)
        gnd_file.write(gnd_list)
        log.info(f"Wrote {len(gnd_list):,} rows to {gnd_file}")

    @classmethod
    def get_data_list(cls) -> list[dict]:
        return TSVFile(cls.DATA_PATH).read()

    @classmethod
    def get_idx(cls):
        return {d["gnd_id"]: d for d in cls.get_data_list()}

    @staticmethod
    def append_gnd_id2(d_idx: dict[dict]) -> dict[dict]:
        d_idx2 = {}
        for d in d_idx.values():
            gnd_id = d["gnd_id"]
            gnd_id2 = gnd_id
            d["gnd_id2"] = gnd_id2
            d_idx2[gnd_id2] = d
        return d_idx2

    @staticmethod
    def get_district_id(gnd_id: str) -> str:
        return gnd_id[:5]

    @classmethod
    def get_gnd_code(cls, gnd_id):
        return gnd_id[-3:]

    @classmethod
    def is_rough_match(cls, gnd1, gnd2):
        gnd_id1 = gnd1["gnd_id"]
        gnd_id2 = gnd2["gnd_id"]
        return (
            cls.get_district_id(gnd_id1) == cls.get_district_id(gnd_id2)
            # and cls.get_gnd_code(gnd_id1) == cls.get_gnd_code(gnd_id2)
            and fuzz.ratio(gnd1["gnd_name"], gnd2["gnd_name"]) >= 80
        )

    @classmethod
    def compare_to_gnd_list_final(cls):
        idx_from_glf = SriLankaBoundaries.append_gnd_id2(
            GNDListFinalXLSX.get_idx()
        )
        idx_from_slb = SriLankaBoundaries.append_gnd_id2(
            SriLankaBoundaries.get_idx()
        )
        ids_from_glf = set(idx_from_glf.keys())
        ids_from_slb = set(idx_from_slb.keys())
        glf_minus_slb = ids_from_glf - ids_from_slb
        if glf_minus_slb:
            log.warning(
                f"⚠️ {
                    len(glf_minus_slb)} GLF but not in SLB"
            )
            for gnd_id in sorted(glf_minus_slb):
                gnd_name = idx_from_glf[gnd_id]["gnd_name"]
                log.debug(f"- (GLF-SLB) {gnd_id} {gnd_name}")
        else:
            log.info("✅ All GND IDs in GLF are in SLB")
        log.debug("-" * 40)

        slb_minus_glf = ids_from_slb - ids_from_glf
        if slb_minus_glf:
            log.warning(
                f"⚠️ {
                    len(slb_minus_glf)} In SLB but not in GLF"
            )
            for gnd_id in sorted(slb_minus_glf):
                gnd_name = idx_from_slb[gnd_id]["gnd_name"]
                log.debug(f"- (SLB-GLF) {gnd_id} {gnd_name}")
        else:
            log.info("✅ All GND IDs in SLB are in GLF")
        log.debug("-" * 40)

        n_match = 0
        n_no_match = 0
        for gnd_id_slb in sorted(slb_minus_glf):
            gnd_slb = idx_from_slb[gnd_id_slb]
            has_match = False
            for gnd_id_glf in sorted(glf_minus_slb):
                gnd_glf = idx_from_glf[gnd_id_glf]
                if cls.is_rough_match(gnd_slb, gnd_glf):
                    # log.info(
                    #     f"{n_match:03d}. "
                    #     f"{gnd_id_slb} {gnd_slb['gnd_name']} <> "
                    #     f"{gnd_id_glf} {gnd_glf['gnd_name']}"
                    # )
                    has_match = True
            if has_match:
                n_match += 1
            else:
                n_no_match += 1
                log.debug(
                    f"{n_no_match:03d}. ❌ {gnd_id_slb} {gnd_slb['gnd_name']}"
                )


if __name__ == "__main__":
    SriLankaBoundaries.build_gnd_table()
    SriLankaBoundaries.compare_to_gnd_list_final()
