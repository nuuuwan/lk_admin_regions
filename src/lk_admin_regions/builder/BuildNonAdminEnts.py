from utils import Log

from lk_admin_regions.builder.BuildEnts import BuildEnts

log = Log("BuildNonAdminEnts")


class BuildNonAdminEnts:
    MIN_MATCH_RATIO = 80

    @classmethod
    def build_pds(cls):
        pd_data_list = cls.get_pd_data_list()
        pd_data_list_idx = {d["code"]: d for d in pd_data_list}

        def expand_gnd(gnd):
            pd_code = gnd["pd_code"]
            pd_data = pd_data_list_idx[pd_code]
            return gnd | dict(
                pd_id=pd_data["id"],
                pd_name=pd_data["name"],
                pd_code=pd_code,
            )

        BuildEnts.build_parent("pd", expand_gnd, ["pd_code"])

    @classmethod
    def build_eds(cls):
        district_to_ed = cls.get_district_to_ed()
        ed_ground_truth = cls.get_ed_ground_truth()
        ed_ground_truth_idx = {d["id"]: d for d in ed_ground_truth}

        def expand_gnd(gnd):
            district_id = gnd["district_id"]
            ed_id = district_to_ed[district_id]
            ed_name = ed_ground_truth_idx[ed_id]["name"]
            return gnd | dict(
                ed_id=ed_id,
                ed_name=ed_name,
            )

        BuildEnts.build_parent("ed", expand_gnd)

    @classmethod
    def build_lgs(cls):

        def expand_gnd(gnd):
            return gnd | dict(
                lg_id=gnd["lg_id"],
                lg_name=gnd["lg_name"],
                lg_code=gnd["lg_code"],
                lg_level=gnd["lg_level"],
            )

        BuildEnts.build_parent("lg", expand_gnd, ["lg_code", "lg_level"])

    @classmethod
    def build_all(cls):
        cls.build_eds()
        cls.build_pds()
        cls.build_lgs()
