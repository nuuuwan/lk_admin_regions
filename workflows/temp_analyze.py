from fuzzywuzzy import fuzz

from lk_admin_regions import GNDListFinalXLSX, LKAAdminBoundariesXLSX

ID_CORRECTION_MAP = {
    "LK-2321": "LK-2302",  # Kothmale West
    "LK-2318": "LK-2307",  # Mathurata
    "LK-2309": "LK-2310",  # Niladandahinna
    "LK-2324": "LK-2309",  # Walapane
    "LK-2327": "LK-2313",  # Thalawakelle
    "LK-2330": "LK-2314",  # Norwood
    #
    "LK-3163": "LK-3137",  # Rathgama
    "LK-3160": "LK-3135",  # Madampagama
    "LK-3157": "LK-3128",  # Wanduramba
    #
    "LK-5115": "LK-5112",  # Eravur Pattu
    "LK-5139": "LK-5115",  # Eravur Town
    #
    "LK-5221": "LK-5224",  # Kalmunai
    #
    "LK-9154": "LK-9119",  # Kaltota
}


def correct(d_list, dcs_region_key, hum_region_key):

    corrected_d_list = []
    for d in d_list:
        region_id = "LK-" + d[hum_region_key][2:]
        for before, after in ID_CORRECTION_MAP.items():
            if before in region_id:
                region_id = region_id.replace(before, after)
        d[dcs_region_key] = region_id
        corrected_d_list.append(d)
    return corrected_d_list


def compare(dcs_region_label, hum_admin_level):
    print("-" * 32)
    print("LEVEL ", hum_admin_level)
    print("-" * 32)

    dcs_region_id_key = f"{dcs_region_label}_id"
    dcs_region_name_key = f"{dcs_region_label}_name"
    hum_sheet_name = f"lka_admin{hum_admin_level}"
    hum_region_id_key = f"adm{hum_admin_level}_pcode"
    hum_region_name_key = f"adm{hum_admin_level}_name"
    data_dcs = GNDListFinalXLSX.get_data_list()
    data_hum = LKAAdminBoundariesXLSX.get_sheet_name_to_d_list()

    region_id_to_name_dcs = {
        d[dcs_region_id_key]: d[dcs_region_name_key] for d in data_dcs
    }

    data_hum_corrected = correct(
        data_hum[hum_sheet_name], dcs_region_id_key, hum_region_id_key
    )
    if len(data_hum_corrected) != len(data_hum[hum_sheet_name]):
        print(
            "❌ HUM DUPLICATE IDS",
            len(data_hum_corrected),
            len(data_hum[hum_sheet_name]),
        )
    region_id_to_name_hum = {
        d[dcs_region_id_key]: d[hum_region_name_key]
        for d in data_hum_corrected
    }

    print(len(region_id_to_name_dcs), next(iter(region_id_to_name_dcs.keys())))
    print(len(region_id_to_name_hum), next(iter(region_id_to_name_hum.keys())))

    dcs_region_ids = set(region_id_to_name_dcs.keys())
    hum_region_ids = set(region_id_to_name_hum.keys())

    dcs_minus_hum = set(dcs_region_ids - hum_region_ids)
    hum_minus_dcs = set(hum_region_ids - dcs_region_ids)

    print("len(dcs_minus_hum)=", len(dcs_minus_hum))
    if dcs_minus_hum:
        for region_id in dcs_minus_hum:
            print(
                "\t- ",
                region_id,
                region_id_to_name_dcs[region_id],
            )

    print("len(hum_minus_dcs)=", len(hum_minus_dcs))
    if hum_minus_dcs:
        for region_id in hum_minus_dcs:
            print(
                "\t- ",
                region_id,
                region_id_to_name_hum[region_id],
            )

    if dcs_minus_hum == set() and hum_minus_dcs == set():
        print("✅ IDs MATCH")

        n_mismatch = 0
        for region_id in dcs_region_ids:
            dcs_name = region_id_to_name_dcs[region_id]
            hum_name = region_id_to_name_hum[region_id]

            match_score = fuzz.ratio(dcs_name, hum_name)

            if match_score < 90:
                print(
                    "\t❌ NAME MISMATCH",
                    region_id,
                    dcs_name,
                    hum_name,
                    match_score,
                )
                n_mismatch += 1

        if n_mismatch == 0:
            print("✅ NAMES MATCH")
        else:
            print(f"❌ {n_mismatch} NAME MISMATCHES")
    print(" ")


if __name__ == "__main__":
    for dcs_region_label, hum_admin_level in [
        # ("province", 1),
        # ("district", 2),
        ("dsd", 3),
        # ("gnd", 4),
    ]:
        compare(dcs_region_label, hum_admin_level)
