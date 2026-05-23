from fuzzywuzzy import fuzz

from lk_admin_regions import GNDListFinalXLSX, LKAAdminBoundariesXLSX

ID_CORRECTION_MAP = {
    "LK-2304": "LK-2321",  # Kothmale West
    "LK-2307": "LK-2318",  # Mathurata
    "LK-2310": "LK-2309",  # Niladandahinna
    "LK-2309": "LK-2324",  # Walapane
    "LK-2313": "LK-2327",  # Thalawakelle
    "LK-2316": "LK-2330",  # Norwood
    "LK-3137": "LK-3163",  # Rathgama
    "LK-3138": "LK-3160",  # Madampagama
    "LK-3128": "LK-3157",  # Wanduramba
    "LK-9119": "LK-9154",  # Kaltota
}


def correct(d_list, gcs_region_key, hum_region_key):

    corrected_d_list = []
    for d in d_list:
        for before, after in ID_CORRECTION_MAP.items():
            region_id = "LK-" + d[hum_region_key][2:]
            # if before in d[hum_region_key]:
            #     region_id = region_id.replace(before, after)
            d[gcs_region_key] = region_id
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
    region_id_to_name_hum = {
        d[dcs_region_id_key]: d[hum_region_name_key]
        for d in correct(
            data_hum[hum_sheet_name], dcs_region_id_key, hum_region_id_key
        )
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
