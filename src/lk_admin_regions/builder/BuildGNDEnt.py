import os
from functools import cache

from fuzzywuzzy import fuzz
from utils import JSONFile, Log, TSVFile

from lk_admin_regions.corrections.CombineDCSAndHumData import \
    CombineDCSAndHumData

log = Log("BuildGNDEnt")

LIM_FUZZ_RATIO = 80
LIM_FUZZ_RATIO2 = 60


class BuildGNDEnt:
    DIR_DATA = "data"
    DIR_DATA_ENTS = os.path.join(DIR_DATA, "ents")
    RAW_DATA_PATH = os.path.join("data_temp", "combined_gnd.tsv")
    DENORMALIZED_GNDS_PATH_BASE = os.path.join(
        "data_temp", "denormalized_gnds"
    )
    MIN_MATCH_RATIO = 80

    @classmethod
    def get_ed_to_pd(cls):
        pds = TSVFile(
            os.path.join("data_ground_truth", "misc", "pds.tsv")
        ).read()
        ed_to_pds = {}
        for pd in pds:
            pd_id = pd["id"]
            assert len(pd_id) == 6 and pd_id.startswith("EC-")
            ed_id = pd_id[:5]
            if ed_id not in ed_to_pds:
                ed_to_pds[ed_id] = []
            ed_to_pds[ed_id].append(pd)
        return ed_to_pds

    @classmethod
    def get_pd_data_list(cls):
        gnds = CombineDCSAndHumData.get_data_list()
        gnds.sort(
            key=lambda gnd: (
                f'{int(gnd["dcs_pd_code"][:3]):03d}',
                gnd["dcs_gnd_id"],
            )
        )

        district_to_ed = cls.get_district_to_ed()
        ed_to_pd = cls.get_ed_to_pd()
        ed_to_pd_code_to_name_dcs = {}
        for gnd in gnds:
            gnd_id = gnd["dcs_gnd_id"]
            district_id = gnd["dcs_district_id"]
            ed_id = district_to_ed[district_id]

            pd_code = gnd["dcs_pd_code"]
            if len(pd_code) > 3:
                log.warning(
                    f"'[{gnd_id}] Multiple codes: {pd_code}."
                    + f" Using only first: {pd_code[:3]}."
                )
            pd_code = f'{int(gnd["dcs_pd_code"][:3]):03d}'

            if ed_id not in ed_to_pd_code_to_name_dcs:
                ed_to_pd_code_to_name_dcs[ed_id] = {}
            if pd_code not in ed_to_pd_code_to_name_dcs[ed_id]:
                dcs_pd_name = gnd["dcs_pd_name"].split("/")[0].strip()
                ed_to_pd_code_to_name_dcs[ed_id][pd_code] = dcs_pd_name

        d_list = []
        for ed_id, pd_code_to_name_dcs in ed_to_pd_code_to_name_dcs.items():
            pds_for_ed = ed_to_pd[ed_id]
            for pd, (pd_code, pd_name_from_dcs) in zip(
                pds_for_ed, pd_code_to_name_dcs.items()
            ):
                d = dict(
                    id=pd["id"],
                    name=pd["name"],
                    code=pd_code,
                    name_from_dcs=pd_name_from_dcs,
                )
                d_list.append(d)

        # HACK
        d_list[90]["name_from_dcs"] = "Vavuniya"
        d_list[90]["code"] = "092"
        d_list[91]["name_from_dcs"] = "Mullaitivu"
        d_list[91]["code"] = "091"

        d_list.sort(key=lambda d: d["id"])
        n_match = 0
        # validate names
        for d in d_list:
            name = d["name"]
            name_from_dcs = d["name_from_dcs"]
            match_ratio = fuzz.ratio(name, name_from_dcs)
            if match_ratio < cls.MIN_MATCH_RATIO:
                log.warning(
                    f"{d['id']} ({name}) vs. '{d['code']} ({name_from_dcs})'"
                    + f" (match ratio: {match_ratio})"
                )
            else:
                n_match += 1
        log.info(f"{n_match}/{len(d_list)} PD Name match")

        d_list = [
            dict(
                id=d["id"],
                name=d["name"],
                code=d["code"],
            )
            for d in d_list
        ]

        return d_list

    @classmethod
    def get_district_to_ed(cls):
        district_and_ed = TSVFile(
            os.path.join("data_ground_truth", "misc", "district_and_ed.tsv")
        ).read()
        district_to_ed = {
            d["district_id"]: d["ed_id"] for d in district_and_ed
        }
        return district_to_ed

    @staticmethod
    def write_all_types(d_list, file_path_base):
        log.info(f"Writing {len(d_list)} ents to {file_path_base}.[json|tsv]")
        json_file = JSONFile(f"{file_path_base}.json")
        json_file.write(d_list)
        log.info(f"\tWrote {json_file}")
        tsv_file = TSVFile(f"{file_path_base}.tsv")
        tsv_file.write(d_list)
        log.info(f"\tWrote {tsv_file}")

    @classmethod
    def build_denormalized_gnd(cls, raw_d, district_to_ed, pd_code_to_data):
        pd_data = pd_code_to_data[raw_d["dcs_pd_code"]]
        return dict(
            # gnd
            gnd_id=raw_d["dcs_gnd_id"],
            gnd_name=raw_d["hum_adm4_name"] or raw_d["dcs_gnd_name"],
            gnd_num=raw_d["dcs_gnd_num"],
            area_sqkm=raw_d["hum_area_sqkm"],
            center_lat=raw_d["hum_center_lat"],
            center_lng=raw_d["hum_center_lon"],
            # country
            country_id="LK",
            country_name=raw_d["hum_adm0_name"] or "Sri Lanka",
            # province
            province_id=raw_d["dcs_province_id"],
            province_name=raw_d["hum_adm1_name"]
            or raw_d["dcs_province_name"],
            # district
            district_id=raw_d["dcs_district_id"],
            district_name=raw_d["hum_adm2_name"]
            or raw_d["dcs_district_name"],
            # dsd
            dsd_id=raw_d["dcs_dsd_id"],
            dsd_name=raw_d["hum_adm3_name"] or raw_d["dcs_dsd_name"],
            # ed
            ed_id=district_to_ed[raw_d["dcs_district_id"]],
            # pd
            pd_id=pd_data["id"],
            pd_name=pd_data["name"],
            pd_code=raw_d["dcs_pd_code"],
            # lg
            lg_id=raw_d["dcs_lg_id"],
            lg_name=raw_d["dcs_lg_name"],
            lg_code=raw_d["dcs_lg_code"],
            lg_level=raw_d["dcs_lg_level"],
        )

    @classmethod
    def build_denormalized_gnds(cls):
        raw_d_list = CombineDCSAndHumData().get_data_list()

        district_to_ed = cls.get_district_to_ed()
        pd_data_list = cls.get_pd_data_list()
        pd_code_to_data = {d["code"]: d for d in pd_data_list}

        d_list = [
            cls.build_denormalized_gnd(d, district_to_ed, pd_code_to_data)
            for d in raw_d_list
        ]
        d_list.sort(key=lambda d: d["gnd_id"])
        cls.write_all_types(d_list, cls.DENORMALIZED_GNDS_PATH_BASE)

    @classmethod
    def build_gnd(cls, denormalized_gnd):
        return dict(
            # standard fields
            id=denormalized_gnd["gnd_id"],
            name=denormalized_gnd["gnd_name"],
            area_sqkm=round(float(denormalized_gnd["area_sqkm"]), 2),
            center_lat=round(float(denormalized_gnd["center_lat"]), 6),
            center_lng=round(float(denormalized_gnd["center_lng"]), 6),
            # additional vars
            num=denormalized_gnd["gnd_num"],
            # parents
            country_id="LK",
            province_id=denormalized_gnd["province_id"],
            district_id=denormalized_gnd["district_id"],
            dsd_id=denormalized_gnd["dsd_id"],
            ed_id=denormalized_gnd["ed_id"],
            pd_id=denormalized_gnd["pd_id"],
            lg_id=denormalized_gnd["lg_id"],
        )

    @classmethod
    @cache
    def read_denormalized_gnds(cls):
        return TSVFile(cls.DENORMALIZED_GNDS_PATH_BASE + ".tsv").read()

    @classmethod
    def build_gnds(cls):
        denormalized_gnds = cls.read_denormalized_gnds()
        gnds = [cls.build_gnd(d) for d in denormalized_gnds]
        cls.write_all_types(gnds, os.path.join(cls.DIR_DATA_ENTS, "gnds"))

    @classmethod
    def build(cls):
        cls.build_denormalized_gnds()
        cls.build_gnds()
