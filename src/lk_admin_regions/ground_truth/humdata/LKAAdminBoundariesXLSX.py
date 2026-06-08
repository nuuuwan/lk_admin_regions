import os

import pandas as pd
from utils import Log

log = Log("LKAAdminBoundariesXLSX")


class LKAAdminBoundariesXLSX:

    GROUND_TRUTH_PATH = os.path.join(
        "data_ground_truth", "humdata_cod_ab_lka", "lka_admin_boundaries.xlsx"
    )

    @classmethod
    def get_sheet_name_to_d_list(cls):
        dfs = pd.read_excel(
            LKAAdminBoundariesXLSX.GROUND_TRUTH_PATH, sheet_name=None
        )
        idx = {}
        for sheet_name, df in dfs.items():
            d_list = df.to_dict(orient="records")
            idx[sheet_name.lower().strip()] = d_list
        return idx

    @classmethod
    def get_ground_truth_geojson_path(cls, level):
        if level == 3:
            return os.path.join(
                "data_temp",
                "lka_admin3.kalmunai.geojson",
            )

        return os.path.join(
            "data_ground_truth",
            "humdata_cod_ab_lka",
            "lka_admin_boundaries",
            f"lka_admin{level}.geojson",
        )
