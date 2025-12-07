import os

from rapidfuzz import fuzz
from utils import JSONFile, Log, TSVFile

from lk_admin_regions.ground_truth.dcs.GNDListFinalXLSX import GNDListFinalXLSX
from lk_admin_regions.ground_truth.humdata import LKAAdminBoundariesXLSX

log = Log("BuildEnts")

LIM_FUZZ_RATIO = 80
LIM_FUZZ_RATIO2 = 60


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

    @classmethod
    def get_id_field(cls, level):
        return f"adm{level}_pcode"

    @classmethod
    def get_id(cls, raw_d, level, id_len):
        if id_len == 0:
            return "LK"
        return f"LK-{int(raw_d[cls.get_id_field(level)][-id_len:])}"

    @classmethod
    def validate(cls, d_list):
        id_list = [d["id"] for d in d_list]
        unique_id_list = list(set(id_list))
        assert len(id_list) == len(unique_id_list)

        total_area = int(sum(d["area_sqkm"] for d in d_list))
        assert 65_983 <= total_area <= 66_040, total_area

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
        cls.validate(d_list)

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

    @staticmethod
    def fuzzy_match(a, b):
        # replace non alphanumeric characters with space
        a = "".join(c if c.isalnum() else "" for c in str(a))
        a = a.lower()
        b = "".join(c if c.isalnum() else "" for c in str(b))
        b = b.lower()
        return fuzz.ratio(a, b)

    @classmethod
    def merge_pds(cls):
        gnd_dcs_d_list = GNDListFinalXLSX.load_all()
        gnd_dcs_idx = {d["gnd_id"]: d for d in gnd_dcs_d_list}
        gnd_ent_list = JSONFile(
            os.path.join(cls.DIR_DATA_ENTS, "gnds.json")
        ).read()
        gnd_ent_idx = {d["id"]: d for d in gnd_ent_list}

        n_all = 0
        ent_minus_dcs_ent_list = []
        ent_and_dcs_ent_list = []
        for gnd_id, gnd_ent in gnd_ent_idx.items():
            gnd_dcs = gnd_dcs_idx.get(gnd_id)

            n_all += 1
            if gnd_dcs is not None and (
                cls.fuzzy_match(gnd_ent["name"], gnd_dcs["gnd_name"])
                >= LIM_FUZZ_RATIO2
                or str(gnd_ent["name"]) == "nan"
            ):
                ent_and_dcs_ent_list.append(gnd_ent | gnd_dcs)
            else:
                ent_minus_dcs_ent_list.append(gnd_ent)

        n_ent_minus_dcs = len(ent_minus_dcs_ent_list)
        log.info(f"{n_all=}")
        log.error(f"{n_ent_minus_dcs=}")

        dcs_minus_gnd_ent_list = []
        for gnd_id, gnd_dcs in gnd_dcs_idx.items():
            gnd_ent = gnd_ent_idx.get(gnd_id)
            if not (
                gnd_ent is not None
                and cls.fuzzy_match(gnd_ent["name"], gnd_dcs["gnd_name"])
                >= LIM_FUZZ_RATIO
            ):
                dcs_minus_gnd_ent_list.append(gnd_dcs)

        n_dcs_minus_ent = len(dcs_minus_gnd_ent_list)
        log.error(f"{n_dcs_minus_ent=}")

        ent_and_dcs_ent_list_name_match = []
        ent_minus_dcs_no_name_match = []
        for gnd_ent in ent_minus_dcs_ent_list:

            matches = []
            for gnd_dcs in dcs_minus_gnd_ent_list:
                if gnd_dcs["district_id"] == gnd_ent["id"][:5]:
                    fuzz_ratio = cls.fuzzy_match(
                        gnd_ent["name"], gnd_dcs["gnd_name"]
                    )
                    if fuzz_ratio >= LIM_FUZZ_RATIO:
                        matches.append((fuzz_ratio, gnd_ent))

            if matches:
                matches.sort(reverse=True, key=lambda x: x[0])
                _, best_match = matches[0]
                ent_and_dcs_ent_list_name_match.append(best_match | gnd_dcs)
            else:
                ent_minus_dcs_no_name_match.append(gnd_ent)

        n_name_match = len(ent_and_dcs_ent_list_name_match)
        log.info(f"{n_name_match=}")

        n_no_name_match = len(ent_minus_dcs_no_name_match)
        log.error(f"{n_no_name_match=}")

        # for gnd_ent in ent_minus_dcs_no_name_match:
        #     print(gnd_ent["id"], gnd_ent["name"])
