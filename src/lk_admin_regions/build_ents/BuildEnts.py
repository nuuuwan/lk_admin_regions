import os

from utils import JSONFile, Log, TSVFile

from lk_admin_regions.ground_truth.humdata import LKAAdminBoundariesXLSX

log = Log("BuildEnts")


class BuildEnts:
    DIR_DATA = "data"
    DIR_DATA_ENTS = os.path.join(DIR_DATA, "ents")

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
                "id": (
                    f"LK-{int(raw_d[f'adm{level}_pcode'][-id_len:])}"
                    if id_len > 0
                    else "LK"
                ),
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
            log.info(f"Wrote {n:,} ents to {file}")

    @classmethod
    def build_all(cls):
        sheet_name_to_d_list = (
            LKAAdminBoundariesXLSX.get_sheet_name_to_d_list()
        )
        for ent_type_name, sheet_name, func_raw_d_to_ent_d in [
            (
                "country",
                0,
                0,
            ),
            (
                "province",
                1,
                1,
            ),
            (
                "district",
                2,
                2,
            ),
            (
                "dsd",
                3,
                4,
            ),
            (
                "gnd",
                4,
                7,
            ),
        ]:
            cls.build_generic_ent(
                sheet_name_to_d_list,
                ent_type_name,
                sheet_name,
                func_raw_d_to_ent_d,
            )


if __name__ == "__main__":
    BuildEnts.build_all()
