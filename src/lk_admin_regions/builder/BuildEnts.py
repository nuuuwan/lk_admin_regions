import os

from utils import JSONFile, Log, TSVFile

log = Log("BuildEnts")

LIM_FUZZ_RATIO = 80
LIM_FUZZ_RATIO2 = 60


class BuildEnts:
    DIR_DATA = "data"
    DIR_DATA_ENTS = os.path.join(DIR_DATA, "ents")
    RAW_DATA_PATH = os.path.join("data_temp", "combined_gnd.tsv")
    DENORMALIZED_GNDS_PATH = os.path.join(
        "data_temp", "denormalized_gnds.tsv"
    )

    @classmethod
    def build_denormalized_gnd(cls, raw_d):
        # Admin Regions
        country_id = "LK"
        province_id = raw_d["dcs_province_id"]
        district_id = raw_d["dcs_district_id"]
        dsd_id = raw_d["dcs_dsd_id"]

        gnd_code = int(raw_d["dcs_gnd_code"])
        gnd_id = f"{dsd_id}{gnd_code:03d}"
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
        raw_d_list = TSVFile(cls.RAW_DATA_PATH).read()
        d_list = [cls.build_denormalized_gnd(d) for d in raw_d_list]
        d_list.sort(key=lambda d: d["gnd_id"])
        tsv_file = TSVFile(BuildEnts.DENORMALIZED_GNDS_PATH)
        tsv_file.write(d_list)
        log.info(f"Wrote {tsv_file}")

    @classmethod
    def build_gnd(cls, denormalized_gnd):
        return dict(
            gnd_id=denormalized_gnd["gnd_id"],
            name=denormalized_gnd["gnd_name"],
            num=denormalized_gnd["gnd_num"],
            area_sqkm=denormalized_gnd["area_sqkm"],
            center_lat=denormalized_gnd["center_lat"],
            center_lng=denormalized_gnd["center_lng"],
        )

    @classmethod
    def build_gnds(cls):
        denormalized_gnds = TSVFile(cls.DENORMALIZED_GNDS_PATH).read()
        gnds = [cls.build_gnd(d) for d in denormalized_gnds]
        json_file = JSONFile(os.path.join(cls.DIR_DATA_ENTS, "gnds.json"))
        json_file.write(gnds)
        log.info(f"Wrote {json_file}")
        tsv_file = TSVFile(os.path.join(cls.DIR_DATA_ENTS, "gnds.tsv"))
        tsv_file.write(gnds)
        log.info(f"Wrote {tsv_file}")

    @classmethod
    def build(cls):
        cls.build_denormalized_gnds()
        cls.build_gnds()


if __name__ == "__main__":
    BuildEnts.build()
