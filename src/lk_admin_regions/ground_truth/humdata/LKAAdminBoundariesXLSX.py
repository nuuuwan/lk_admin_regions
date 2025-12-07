import json
import os

import pandas as pd
from utils import Log

log = Log("LKAAdminBoundariesXLSX")


class LKAAdminBoundariesXLSX:

    GROUND_TRUTH_PATH = os.path.join(
        "data_ground_truth", "humdata_cod_ab_lka", "lka_admin_boundaries.xlsx"
    )

    # IDs assigned to newly created DSDs and GNDs (see README.recent-history.md)
    # in humdata is inconsistent with how http://moha.gov.lk
    # and others define them.
    # This map is used to correct those IDs.
    ID_CORRECTION_MAP = {
        # LK-23
        # "LK-2303": "LK-2303",  # Kothmale East - UNCHANGED
        "LK-2321": "LK-2304",  # Kothmale West
        # "LK-2306": "LK-2306",  # Hanguranketha - UNCHANGED
        "LK-2318": "LK-2307",  # Mathurata
        
        "LK-2309": "LK-2310",  # Niladandahinna # ORDER MATTERS
        "LK-2324": "LK-2309",  # Walapane # ORDER MATTERS
        
        # "LK-2312": "LK-2312",  # Nuwara-Eliya - UNCHANGED
        "LK-2327": "LK-2313",  # Thalawakelle
        # "LK-2315": "LK-2315",  # Ambagamuwa Korale - UNCHANGED
        "LK-2330": "LK-2316",  # Norwood
        # LK-31
        # "LK-3136": "LK-3136",  # Hikkaduwa - UNCHANGED
        "LK-3163": "LK-3137",  # Rathgama
        "LK-3160": "LK-3138",  # Madampagama
        # "LK-3127": "LK-3127",  # Baddegama - UNCHANGED
        "LK-3157": "LK-3128",  # Wanduramba
        # LK-91
        # "LK-9118": "LK-9118",  # Balangoda - UNCHANGED
        "LK-9154": "LK-9119",  # Kaltota
    }


    @classmethod
    def correct_v(cls, v):
        for wrong, right in cls.ID_CORRECTION_MAP.items():
            if wrong in v:
                v = v.replace(wrong, right)
        return v

    @classmethod
    def correct_d(cls, d):
        return {k: cls.correct_v(v) for k, v in d.items()}]

    @classmethod 
    def correct_d_list(cls, d_list):
        return [cls.correct_d(d) for d in d_list]
            

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
