import os
from functools import cache

from utils import JSONFile, Log, TSVFile

from lk_admin_regions.corrections.CombineDCSAndHumData import \
    CombineDCSAndHumData

log = Log("BuildEnts")

LIM_FUZZ_RATIO = 80
LIM_FUZZ_RATIO2 = 60


class BuildEnts:
    DIR_DATA = "data"
    DIR_DATA_ENTS = os.path.join(DIR_DATA, "ents")
    RAW_DATA_PATH = os.path.join("data_temp", "combined_gnd.tsv")
    DENORMALIZED_GNDS_PATH_BASE = os.path.join(
        "data_temp", "denormalized_gnds"
    )

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
    def build_denormalized_gnd(cls, raw_d):
        # Admin Regions
        country_id = "LK"
        province_id = raw_d["dcs_province_id"]
        district_id = raw_d["dcs_district_id"]
        dsd_id = raw_d["dcs_dsd_id"]
        gnd_id = raw_d["dcs_gnd_id"]

        gnd_num = raw_d["dcs_gnd_num"]

        country_name = raw_d["hum_adm0_name"] or "Sri Lanka"
        province_name = raw_d["hum_adm1_name"] or raw_d["dcs_province_name"]
        district_name = raw_d["hum_adm2_name"] or raw_d["dcs_district_name"]
        dsd_name = raw_d["hum_adm3_name"] or raw_d["dcs_dsd_name"]
        gnd_name = raw_d["hum_adm4_name"] or raw_d["dcs_gnd_name"]

        # Other Regions
        lg_code = raw_d["dcs_lg_code"]
        pd_code = raw_d["dcs_pd_code"]

        # Geo
        area_sqkm = raw_d["hum_area_sqkm"]
        center_lat = raw_d["hum_center_lat"]
        center_lng = raw_d["hum_center_lon"]

        return dict(
            # gnd
            gnd_id=gnd_id,
            gnd_name=gnd_name,
            gnd_num=gnd_num,
            area_sqkm=area_sqkm,
            center_lat=center_lat,
            center_lng=center_lng,
            # dsd
            dsd_id=dsd_id,
            dsd_name=dsd_name,
            # district
            district_id=district_id,
            district_name=district_name,
            # province
            province_id=province_id,
            province_name=province_name,
            # country
            country_id=country_id,
            country_name=country_name,
            # lg
            lg_code=lg_code,
            # pd
            pd_code=pd_code,
        )

    @classmethod
    def build_denormalized_gnds(cls):
        raw_d_list = CombineDCSAndHumData().get_data_list()
        d_list = [cls.build_denormalized_gnd(d) for d in raw_d_list]
        d_list.sort(key=lambda d: d["gnd_id"])
        cls.write_all_types(d_list, cls.DENORMALIZED_GNDS_PATH_BASE)

    @classmethod
    def build_gnd(cls, denormalized_gnd):
        return dict(
            id=denormalized_gnd["gnd_id"],
            name=denormalized_gnd["gnd_name"],
            num=denormalized_gnd["gnd_num"],
            area_sqkm=round(float(denormalized_gnd["area_sqkm"]), 2),
            center_lat=round(float(denormalized_gnd["center_lat"]), 6),
            center_lng=round(float(denormalized_gnd["center_lng"]), 6),
            lg_code=denormalized_gnd["lg_code"],
            pd_code=denormalized_gnd["pd_code"],
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
    def build_parents(cls):
        denormalized_gnds = cls.read_denormalized_gnds()
        for parent_label in ["dsd", "district", "province", "country"]:
            id_key = f"{parent_label}_id"
            name_key = f"{parent_label}_name"

            gnds_by_parent = {}
            for gnd in denormalized_gnds:
                parent_id = gnd[id_key]
                if parent_id not in gnds_by_parent:
                    gnds_by_parent[parent_id] = []
                gnds_by_parent[parent_id].append(gnd)

            parents = []
            for parent_id, gnds_for_parent in gnds_by_parent.items():
                parent_name = gnds_for_parent[0][name_key]

                w_area_sqkm = 0
                w_center_lat = 0
                w_center_lng = 0
                for gnd in gnds_for_parent:
                    area_sqkm = float(gnd["area_sqkm"])
                    w_area_sqkm += area_sqkm
                    w_center_lat += area_sqkm * float(gnd["center_lat"])
                    w_center_lng += area_sqkm * float(gnd["center_lng"])

                center_lat = w_center_lat / w_area_sqkm if w_area_sqkm else 0
                center_lng = w_center_lng / w_area_sqkm if w_area_sqkm else 0

                parent_d = dict(
                    id=parent_id,
                    name=parent_name,
                    area_sqkm=round(w_area_sqkm, 2),
                    center_lat=round(center_lat, 6),
                    center_lng=round(center_lng, 6),
                )
                parents.append(parent_d)

            parents.sort(key=lambda d: d["id"])
            cls.write_all_types(
                parents,
                os.path.join(cls.DIR_DATA_ENTS, f"{parent_label}s"),
            )

    @classmethod
    def build_all(cls):
        cls.build_denormalized_gnds()
        cls.build_gnds()
        cls.build_parents()

    @classmethod
    @cache
    def read(cls, ent_type_name):
        file_path = os.path.join(cls.DIR_DATA_ENTS, f"{ent_type_name}s.tsv")
        return TSVFile(file_path).read()


if __name__ == "__main__":
    BuildEnts.build_all()
