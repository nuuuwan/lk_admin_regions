import json
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


if __name__ == "__main__":
    idx = {}
    for (
        sheet_name,
        d_list,
    ) in LKAAdminBoundariesXLSX.get_sheet_name_to_d_list().items():
        first_d = d_list[0]
        first_d_stred = {k: str(v) for k, v in first_d.items()}
        idx[sheet_name] = first_d_stred

    log.debug(json.dumps(idx, indent=2))
