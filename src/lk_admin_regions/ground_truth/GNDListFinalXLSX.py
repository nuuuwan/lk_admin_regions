import os

import pandas as pd
from utils import Log, TSVFile

log = Log("GNDListFinalXLSX")

"""
{'Serial Number': 1, 'GND_UID': 1103005.0, 'Province_Code': 1.0, 'Province_Name': 'Western', 'District_Code': 11.0, 'District_Name': 'Colombo', 'DSD_ Code': 3.0, 'DSD_Name': 'Colombo', 'GND_ Code': 5.0, 'GND_Name': 'Sammanthranapura', 'GND_NUM': ' ', 'LGD_Code': 11, 'LGD_Name': 'Colombo MC', 'Polling Division_Code': 1, 'Polling Division_Name': 'Clombo North'}
"""


class GNDListFinalXLSX:
    PATH = os.path.join(
        "data_ground_truth", "gnd_list_final", "GNDList_Final.xlsx"
    )

    @classmethod
    def to_list_of_dicts(cls):

        df = pd.read_excel(cls.PATH)
        return df.to_dict(orient="records")

    @classmethod
    def get_d_gnd_from_row(cls, d):
        if str(d["GND_UID"]) in ["", "nan"]:
            return None
        gnd_uid = f"{int(d["GND_UID"])}"
        assert len(gnd_uid) == 7, gnd_uid
        gnd_id = f"LK-{gnd_uid}"

        gnd_code = f"{int(d["GND_ Code"])}"
        gnd_num = str(d["GND_NUM"]).strip()

        dsd_code = f"{int(d['DSD_ Code']):02d}"
        assert len(dsd_code) == 2, dsd_code
        district_code = f"{int(d['District_Code'])}"
        assert len(district_code) == 2, district_code
        province_code = f"{int(d['Province_Code'])}"
        assert len(province_code) == 1, province_code

        lg_code_str = str(d["LGD_Code"])
        if "/" in lg_code_str:
            lg_code_str = lg_code_str.split("/")[-1]  # HACK!
        if "*" in lg_code_str:
            lg_code_str = lg_code_str.replace("*", "")  # HACK!
        lg_code = f"{int(lg_code_str):03d}"
        assert len(lg_code) == 3, lg_code

        pd_code_str = str(d["Polling Division_Code"])
        if "/" in pd_code_str:
            pd_code_str = pd_code_str.split("/")[-1]  # HACK!
        pd_code = f"{int(pd_code_str):03d}"
        assert len(pd_code) == 3, pd_code

        pd_name = d["Polling Division_Name"].strip()
        lg_name = d["LGD_Name"].strip()
        pd_name = d["Polling Division_Name"].strip()

        gnd_name = d["GND_Name"].strip()
        dsd_name = d["DSD_Name"].strip()
        district_name = d["District_Name"].strip()
        province_name = d["Province_Name"].strip()

        # derived
        province_id = f"LK-{province_code}"
        assert province_id == gnd_id[:4], f"{province_id} != {gnd_id[:4]}"
        district_id = f"LK-{district_code}"
        assert district_id == gnd_id[:5], f"{district_id} != {gnd_id[:5]}"
        dsd_id = f"{district_id}{dsd_code}"
        assert dsd_id == gnd_id[:7], f"{dsd_id} != {gnd_id[:7]}"

        return dict(
            # gnd
            gnd_id=gnd_id,
            gnd_name=gnd_name,
            gnd_code=gnd_code,
            gnd_num=gnd_num,
            # dsd
            dsd_id=dsd_id,
            dsd_name=dsd_name,
            dsd_code=dsd_code,
            # district
            district_id=district_id,
            district_name=district_name,
            district_code=district_code,
            # province
            province_id=province_id,
            province_name=province_name,
            province_code=province_code,
            # lg
            lg_name=lg_name,
            lg_code=lg_code,
            # pd
            pd_name=pd_name,
            pd_code=pd_code,
        )

    @classmethod
    def build_gnd_table(cls):
        gnd_list = [cls.get_d_gnd_from_row(d) for d in cls.to_list_of_dicts()]
        gnd_list = [d for d in gnd_list if d is not None]
        gnd_path = os.path.join("data", "gnd.tsv")
        gnd_file = TSVFile(gnd_path)
        gnd_file.write(gnd_list)
        log.info(f"Wrote {len(gnd_list):,} rows to {gnd_file}")


if __name__ == "__main__":
    GNDListFinalXLSX.build_gnd_table()
