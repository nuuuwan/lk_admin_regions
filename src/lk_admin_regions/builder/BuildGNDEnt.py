import os
from functools import cache

from fuzzywuzzy import fuzz
from utils import JSONFile, Log, TSVFile

from lk_admin_regions.corrections.CombineDCSAndHumData import (
    CombineDCSAndHumData,
)

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
    @cache
    def get_ed_ground_truth(cls):
        ed_ground_truth = TSVFile(
            os.path.join("data_ground_truth", "misc", "eds.tsv")
        ).read()
        return ed_ground_truth

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
    def build_denormalized_gnd(
        cls, d, district_to_ed, pd_code_to_data, ed_idx
    ):
        pd_data = pd_code_to_data[d["dcs_pd_code"]]

        ed_id = district_to_ed[d["dcs_district_id"]]
        ed_name = ed_idx[ed_id]["name"]

        if d["dcs_dsd_id"] == "LK-5221":
            d["hum_adm3_name"] = "Kalmunai North"

        if d["hum_adm4_name"] and str(d["hum_adm4_name"]) != "nan":
            gnd_name = d["hum_adm4_name"]
        else:
            gnd_name = d["dcs_gnd_name"]

        return dict(
            # gnd
            gnd_id=d["dcs_gnd_id"],
            gnd_name=gnd_name,
            gnd_num=d["dcs_gnd_num"],
            area_sqkm=d["hum_area_sqkm"],
            center_lat=d["hum_center_lat"],
            center_lng=d["hum_center_lon"],
            # country
            country_id="LK",
            country_name=d["hum_adm0_name"] or "Sri Lanka",
            # province
            province_id=d["dcs_province_id"],
            province_name=d["hum_adm1_name"] or d["dcs_province_name"],
            # district
            district_id=d["dcs_district_id"],
            district_name=d["hum_adm2_name"] or d["dcs_district_name"],
            # dsd
            dsd_id=d["dcs_dsd_id"],
            dsd_name=d["hum_adm3_name"] or d["dcs_dsd_name"],
            # ed
            ed_id=ed_id,
            ed_name=ed_name,
            # pd
            pd_id=pd_data["id"],
            pd_name=pd_data["name"],
            pd_code=d["dcs_pd_code"],
            # lg
            lg_id=d["dcs_lg_id"],
            lg_name=d["dcs_lg_name"],
            lg_code=d["dcs_lg_code"],
            lg_level=d["dcs_lg_level"],
            # geo
            hum_adm0_pcode=d["hum_adm0_pcode"],
            hum_adm1_pcode=d["hum_adm1_pcode"],
            hum_adm2_pcode=d["hum_adm2_pcode"],
            hum_adm3_pcode=d["hum_adm3_pcode"],
            hum_adm4_pcode=d["hum_adm4_pcode"],
        )

    @classmethod
    def build_denormalized_gnds(cls):
        raw_d_list = CombineDCSAndHumData().get_data_list()

        district_to_ed = cls.get_district_to_ed()
        pd_data_list = cls.get_pd_data_list()
        pd_code_to_data = {d["code"]: d for d in pd_data_list}
        ed_ground_truth = cls.get_ed_ground_truth()
        ed_idx = {d["id"]: d for d in ed_ground_truth}

        d_list = [
            cls.build_denormalized_gnd(
                d, district_to_ed, pd_code_to_data, ed_idx
            )
            for d in raw_d_list
        ]
        d_list.sort(key=lambda d: d["gnd_id"])
        cls.write_all_types(d_list, cls.DENORMALIZED_GNDS_PATH_BASE)

    @classmethod
    def build_gnd(cls, denormalized_gnd):
        gnd_id = denormalized_gnd["gnd_id"]
        # hack to fix Mullaitivu (LK-44) GNDs falling into
        # Vavuniya PD (EC-11B) instead of Mullaitivu PD (EC-11C)
        pd_id = denormalized_gnd["pd_id"]
        if gnd_id in [
            "LK-4418010",
            "LK-4418040",
            "LK-4418005",
            "LK-4418035",
            "LK-4418045",
        ]:
            pd_id = "EC-11C"

        # hack: All other GNDs in the Kegalle DSD (LK-9212) are in the Kegalle
        # PD (EC-22C)
        if gnd_id == "LK-9212305":  # Ganthuna Pallegama South
            pd_id = "EC-22C"

        return dict(
            # standard fields
            id=gnd_id,
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
            pd_id=pd_id,
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
    def build_parent_child_maps(cls):
        gnds = cls.read_denormalized_gnds()
        gnds.sort(key=lambda gnd: gnd["gnd_id"])

        region_to_gnds = {}
        region_to_region_type = {}
        for gnd in gnds:
            gnd_id = gnd["gnd_id"]
            for region_type in [
                "province",
                "district",
                "dsd",
                "ed",
                "pd",
                "lg",
            ]:
                region_id_key = f"{region_type}_id"
                region_id = gnd[region_id_key]
                region_to_region_type[region_id] = region_type
                if region_id not in region_to_gnds:
                    region_to_gnds[region_id] = set()
                region_to_gnds[region_id].add(gnd_id)

        region_ids = list(region_to_gnds.keys())
        region_ids.sort()
        parent_to_child_type_to_children = {}
        child_to_parent_type_to_parents = {}

        for region_id1 in region_ids:
            region_type1 = region_to_region_type[region_id1]
            gnds1 = region_to_gnds[region_id1]
            for region_id2 in region_ids:
                region_type2 = region_to_region_type[region_id2]
                gnds2 = region_to_gnds[region_id2]
                if region_id1 != region_id2 and gnds1.issubset(gnds2):
                    if region_id1 not in child_to_parent_type_to_parents:
                        child_to_parent_type_to_parents[region_id1] = {}
                    if (
                        region_type2
                        not in child_to_parent_type_to_parents[region_id1]
                    ):
                        child_to_parent_type_to_parents[region_id1][
                            region_type2
                        ] = []
                    child_to_parent_type_to_parents[region_id1][
                        region_type2
                    ].append(region_id2)

                    if region_id2 not in parent_to_child_type_to_children:
                        parent_to_child_type_to_children[region_id2] = {}
                    if (
                        region_type1
                        not in parent_to_child_type_to_children[region_id2]
                    ):
                        parent_to_child_type_to_children[region_id2][
                            region_type1
                        ] = []
                    parent_to_child_type_to_children[region_id2][
                        region_type1
                    ].append(region_id1)

        parent_to_child_type_to_children_json_file = JSONFile(
            os.path.join("data_temp", "parent_to_child_type_to_children.json")
        )
        parent_to_child_type_to_children_json_file.write(
            parent_to_child_type_to_children
        )
        log.info(f"Wrote {parent_to_child_type_to_children_json_file}")

        child_to_parent_type_to_parents_json_file = JSONFile(
            os.path.join("data_temp", "child_to_parent_type_to_parents.json")
        )
        child_to_parent_type_to_parents_json_file.write(
            child_to_parent_type_to_parents
        )
        log.info(f"Wrote {child_to_parent_type_to_parents_json_file}")

    @classmethod
    def get_child_to_parent_type_to_parents(cls):
        child_to_parent_type_to_parents_json_file = JSONFile(
            os.path.join("data_temp", "child_to_parent_type_to_parents.json")
        )
        return child_to_parent_type_to_parents_json_file.read()

    @classmethod
    def build(cls):
        cls.build_denormalized_gnds()
        cls.build_gnds()
        cls.build_parent_child_maps()
