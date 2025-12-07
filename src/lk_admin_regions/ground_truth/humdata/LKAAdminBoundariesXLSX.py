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
        # LK23
        # "LK2303": "LK2303",  # Kothmale East - UNCHANGED
        "LK2321": "LK2304",  # Kothmale West
        # "LK2306": "LK2306",  # Hanguranketha - UNCHANGED
        "LK2318": "LK2307",  # Mathurata
        "LK2309": "LK2310",  # Niladandahinna # ORDER MATTERS
        "LK2324": "LK2309",  # Walapane # ORDER MATTERS
        # "LK2312": "LK2312",  # Nuwara-Eliya - UNCHANGED
        "LK2327": "LK2313",  # Thalawakelle
        # "LK2315": "LK2315",  # Ambagamuwa Korale - UNCHANGED
        "LK2330": "LK2316",  # Norwood
        # LK31
        # "LK3136": "LK3136",  # Hikkaduwa - UNCHANGED
        "LK3163": "LK3137",  # Rathgama
        "LK3160": "LK3138",  # Madampagama
        # "LK3127": "LK3127",  # Baddegama - UNCHANGED
        "LK3157": "LK3128",  # Wanduramba
        # LK91
        # "LK9118": "LK9118",  # Balangoda - UNCHANGED
        "LK9154": "LK9119",  # Kaltota
    }

    @classmethod
    def correct_v(cls, v):
        for wrong, right in cls.ID_CORRECTION_MAP.items():
            if wrong in str(v):
                v = str(v).replace(wrong, right)
        return v

    @classmethod
    def correct_d(cls, d):
        return {k: cls.correct_v(v) for k, v in d.items()}

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
            idx[sheet_name.lower().strip()] = cls.correct_d_list(d_list)
        return idx
