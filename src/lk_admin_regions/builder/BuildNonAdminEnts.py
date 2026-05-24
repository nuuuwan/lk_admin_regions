import os
from functools import cache

from fuzzywuzzy import fuzz
from utils import Log, TSVFile

from lk_admin_regions.builder.BuildEnts import BuildEnts
from lk_admin_regions.corrections.CombineDCSAndHumData import \
    CombineDCSAndHumData

log = Log("BuildNonAdminEnts")


class BuildNonAdminEnts:
    MIN_MATCH_RATIO = 80

    @classmethod
    @cache
    def get_distrct_to_ed(cls):
        district_and_ed = TSVFile(
            os.path.join("data_ground_truth", "misc", "district_and_ed.tsv")
        ).read()
        district_to_ed = {
            d["district_id"]: d["ed_id"] for d in district_and_ed
        }
        return district_to_ed

    @classmethod
    @cache
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
    def build_pds(cls):
        gnds = CombineDCSAndHumData.get_data_list()
        gnds.sort(
            key=lambda gnd: (
                f'{int(gnd["dcs_pd_code"][:3]):03d}',
                gnd["dcs_gnd_id"],
            )
        )

        district_to_ed = cls.get_distrct_to_ed()
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

        BuildEnts.write_all_types(d_list, os.path.join("data", "ents", "pds"))

    @classmethod
    def build_eds(cls):
        eds = TSVFile(
            os.path.join("data_ground_truth", "misc", "eds.tsv")
        ).read()
        BuildEnts.write_all_types(eds, os.path.join("data", "ents", "eds"))

    @classmethod
    def build_all(cls):
        cls.build_pds()
        cls.build_eds()
