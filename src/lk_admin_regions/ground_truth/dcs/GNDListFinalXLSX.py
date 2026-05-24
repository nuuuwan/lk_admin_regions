import os

import pandas as pd
from utils import Log, TSVFile

log = Log("GNDListFinalXLSX")


class GNDListFinalXLSX:
    GROUND_TRUTH_PATH = os.path.join(
        "data_ground_truth", "dsc_gnd_list_final", "GNDList_Final.xlsx"
    )
    DATA_PATH = os.path.join("data_temp", "gnd-dcs.tsv")

    @classmethod
    def to_list_of_dicts(cls):
        df = pd.read_excel(cls.GROUND_TRUTH_PATH)
        return df.to_dict(orient="records")

    @classmethod
    def expand(cls, d: dict) -> dict:
        try:
            # gnd
            d["gnd_id"] = f"LK-{int(d['GND_UID'])}"
            d["gnd_name"] = d["GND_Name"]
            d["gnd_code"] = str(int(d["GND_ Code"]))
            d["gnd_num"] = d["GND_NUM"]
            # dsd
            d["dsd_id"] = d["gnd_id"][:7]
            # district
            d["district_id"] = d["gnd_id"][:5]
            # province
            d["province_id"] = d["gnd_id"][:4]
            # pd

            pd_code_raw = int(
                str(d["Polling Division_Code"]).split("/")[0].strip()
            )
            d["pd_code"] = f"{pd_code_raw:03d}"

            d["pd_name"] = d["Polling Division_Name"].split("/")[0].strip()
            # lg
            d["lg_code"] = d["LGD_Code"]
            d["lg_name"] = d["LGD_Name"]
            dcs_lg_code_raw = str(d["lg_code"]).replace("*", "")
            lg_code = f'{int(dcs_lg_code_raw.split("/")[0].strip()):03d}'
            lg_id = f"{d["district_id"]}-{lg_code}"
            d["lg_id"] = lg_id

        except Exception as e:
            log.error(f"Error processing: {d}: {e}")
            return None
        return d

    @classmethod
    def build_gnd_table(cls):
        raw_d_list = cls.to_list_of_dicts()
        d_list = [cls.expand(d) for d in raw_d_list[:-1]]
        d_list = [d for d in d_list if d]
        d_list.sort(key=lambda d: d["gnd_id"])

        gnd_file = TSVFile(cls.DATA_PATH)
        gnd_file.write(d_list)
        log.info(f"Wrote {len(d_list):,} rows to {gnd_file}")

    @classmethod
    def get_data_list(cls) -> list[dict]:
        return TSVFile(cls.DATA_PATH).read()

    @classmethod
    def get_idx(cls):
        return {d["GND_UID"]: d for d in cls.get_data_list()}
