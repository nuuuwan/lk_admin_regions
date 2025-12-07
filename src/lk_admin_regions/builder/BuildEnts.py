import os

from utils import JSONFile, Log, TSVFile

from lk_admin_regions.ground_truth.humdata import LKAAdminBoundariesXLSX

log = Log("BuildEnts")


class BuildEnts:
    DIR_DATA = "data"
    DIR_DATA_ENTS = os.path.join(DIR_DATA, "ents")

    ENT_CONFIG = [
        ("country", 0, 0),
        ("province", 1, 1),
        ("district", 2, 2),
        ("dsd", 3, 4),
        ("gnd", 4, 7),
    ]

    # IDs assigned to newly created DSDs and GNDs (see README.recent-history.md)
    # in humdata is inconsistent with how http://moha.gov.lk
    # and others define them.
    # This map is used to correct those IDs.
    ID_CORRECTION_MAP = {
        # LK-23
        # "LK-2303": "LK-2303",  # Kothmale East - UNCHANGED
        "LK-2321": "LK-2304",  # Kothmale West
        # "LK-2306": "LK-2306",  # Hanguranketha - UNCHANGED
        "LK-2318": "LK-2307",  # Mathurata
        "LK-2324": "LK-2309",  # Walapane
        "LK-2309": "LK-2310",  # Niladandahinna
        # "LK-2312": "LK-2312",  # Nuwara-Eliya - UNCHANGED
        "LK-2327": "LK-2313",  # Thalawakelle
        "LK-2315": "LK-2315",  # Ambagamuwa Korale - UNCHANGED
        "LK-2330": "LK-2316",  # Norwood
        # LK-31
        # "LK-3136": "LK-3136",  # Hikkaduwa - UNCHANGED
        "LK-3163": "LK-3137",  # Rathgama
        "LK-3160": "LK-3138",  # Madampagama
        # "LK-3127": "LK-3127",  # Baddegama - UNCHANGED
        "LK-3157": "LK-3128",  # Wanduramba
        # LK-91
        # "LK-9118": "LK-9118",  # Balangoda - UNCHANGED
        "LK-9154": "LK-9119",  # Kaltota
    }

    @classmethod
    def get_id_field(cls, level):
        return f"adm{level}_pcode"

    @classmethod
    def get_id(cls, raw_d, level, id_len):
        if id_len == 0:
            return "LK"
        return f"LK-{int(raw_d[cls.get_id_field(level)][-id_len:])}"

    @classmethod
    def build_generic_ent(
        cls,
        sheet_name_to_d_list,
        ent_type_name,
        level,
        id_len,
    ):

        def func_raw_d_to_ent_d(raw_d):
            return {
                "id": cls.get_id(raw_d, level, id_len),
                "name": raw_d[f"adm{level}_name"],
                "name_si": raw_d[f"adm{level}_name1"],
                "name_ta": raw_d[f"adm{level}_name2"],
                "area_sqkm": float(raw_d["area_sqkm"]),
                "center_lat": float(raw_d["center_lat"]),
                "center_lon": float(raw_d["center_lon"]),
            }

        sheet_name = f"lka_admin{level}"
        raw_d_list = sheet_name_to_d_list[sheet_name]

        d_list = [func_raw_d_to_ent_d(raw_d) for raw_d in raw_d_list]
        d_list.sort(key=lambda d: d["id"])

        os.makedirs(cls.DIR_DATA_ENTS, exist_ok=True)

        n = len(d_list)
        for ext, ChidFile in (("tsv", TSVFile), ("json", JSONFile)):
            file = ChidFile(
                os.path.join(cls.DIR_DATA_ENTS, f"{ent_type_name}s.{ext}")
            )
            file.write(d_list)
            log.info(f"✅ Wrote {n:,} ents to {file}")

    @classmethod
    def build_all(cls):
        sheet_name_to_d_list = (
            LKAAdminBoundariesXLSX.get_sheet_name_to_d_list()
        )
        for ent_type_name, sheet_name, func_raw_d_to_ent_d in cls.ENT_CONFIG:
            cls.build_generic_ent(
                sheet_name_to_d_list,
                ent_type_name,
                sheet_name,
                func_raw_d_to_ent_d,
            )


if __name__ == "__main__":
    BuildEnts.build_all()
