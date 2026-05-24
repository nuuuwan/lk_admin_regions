import os

from fuzzywuzzy import fuzz
from utils import File

from lk_admin_regions import GNDListFinalXLSX, LKAAdminBoundariesXLSX
from lk_admin_regions.corrections.ID_CORRECTION_MAP_dsd import (
    ID_CORRECTION_MAP_dsd,
)
from lk_admin_regions.corrections.ID_CORRECTION_MAP_gnd import (
    ID_CORRECTION_MAP_gnd,
)

ID_CORRECTION_MAP = ID_CORRECTION_MAP_dsd | ID_CORRECTION_MAP_gnd
NAME_MATCH_THRESHOLD = 0.75


class CombineDCSAndHumData:
    @staticmethod
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

    @staticmethod
    def _build_region_name_maps(dcs_region_label, hum_admin_level):
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

        data_hum_corrected = CombineDCSAndHumData.correct(
            data_hum[hum_sheet_name], dcs_region_id_key, hum_region_id_key
        )
        if len(data_hum_corrected) != len(data_hum[hum_sheet_name]):
            print(
                "❌ HUM DUPLICATE IDS",
                len(data_hum_corrected),
                len(data_hum[hum_sheet_name]),
            )
        region_id_to_name_hum = {
            d[dcs_region_id_key]: str(d[hum_region_name_key])
            for d in data_hum_corrected
        }
        return region_id_to_name_dcs, region_id_to_name_hum

    @staticmethod
    def _find_unmatched_ids(region_id_to_name_dcs, region_id_to_name_hum):
        dcs_minus_hum = set()
        n_match_0 = 0
        for dcs_id, dcs_name in region_id_to_name_dcs.items():
            hum_name = region_id_to_name_hum.get(dcs_id)
            if hum_name is None:
                dcs_minus_hum.add(dcs_id)
                continue

            match_score = fuzz.ratio(dcs_name, hum_name)
            if match_score < NAME_MATCH_THRESHOLD:
                dcs_minus_hum.add(dcs_id)

            n_match_0 += 1

        hum_minus_dcs = set()
        for hum_id, hum_name in region_id_to_name_hum.items():
            dcs_name = region_id_to_name_dcs.get(hum_id)
            if dcs_name is None:
                hum_minus_dcs.add(hum_id)
                continue
            match_score = fuzz.ratio(dcs_name, hum_name)
            if match_score < NAME_MATCH_THRESHOLD:
                hum_minus_dcs.add(hum_id)
        return dcs_minus_hum, hum_minus_dcs, n_match_0

    @staticmethod
    def _normalize_parent_region_id(parent_region_id):
        if parent_region_id in ["LK-5221", "LK-5224"]:
            return "LK-5221/5224"
        return parent_region_id

    @staticmethod
    def _build_parent_to_ids(region_ids):
        parent_id_to_ids = {}
        for region_id in region_ids:
            parent_region_id = CombineDCSAndHumData._normalize_parent_region_id(
                region_id[:-3]
            )
            if parent_region_id not in parent_id_to_ids:
                parent_id_to_ids[parent_region_id] = []
            parent_id_to_ids[parent_region_id].append(region_id)
        return parent_id_to_ids

    @staticmethod
    def _print_parent_groups(
        parent_id_to_hum_ids,
        parent_id_to_dcs_ids,
        region_id_to_name_hum,
        region_id_to_name_dcs,
    ):
        all_parent_ids = set(parent_id_to_hum_ids.keys()) | set(
            parent_id_to_dcs_ids.keys()
        )
        for parent_id in sorted(all_parent_ids):
            hum_ids = parent_id_to_hum_ids.get(parent_id, [])
            dcs_ids = parent_id_to_dcs_ids.get(parent_id, [])
            print(parent_id, len(dcs_ids), "DCS", len(hum_ids), "HUM")
            for dcs_id in dcs_ids:
                dcs_name = region_id_to_name_dcs[dcs_id]
                print("\t- DCS ", dcs_id, dcs_name)
            for hum_id in hum_ids:
                hum_name = region_id_to_name_hum[hum_id]
                print("\t- HUM ", hum_id, hum_name)
            print("-" * 16)

    @staticmethod
    def _append_match_1_lines(
        lines,
        hum_minus_dcs,
        dcs_minus_hum,
        region_id_to_name_hum,
        region_id_to_name_dcs,
    ):
        lines.extend(
            [
                "    #",
                "    # " + "=" * 64,
                "    # MATCH 1 - Similar Name",
                "    # " + "=" * 64,
                "    #",
            ]
        )
        previous_parent_region_id = None
        n_match_1 = 0
        for hum_id in sorted(hum_minus_dcs):
            hum_name = region_id_to_name_hum[hum_id]
            match_list = []

            for dcs_id in dcs_minus_hum:
                parent_region_id = dcs_id[:-3]
                if parent_region_id not in hum_id:
                    continue
                dcs_name = region_id_to_name_dcs[dcs_id]
                match_score = fuzz.ratio(dcs_name, hum_name)
                if match_score < 80:
                    continue
                match_list.append((dcs_id, dcs_name, match_score))

            match_list.sort(key=lambda x: x[2], reverse=True)
            if match_list:
                print("\t", hum_id, hum_name)
                for dcs_id, dcs_name, match_score in match_list:
                    parent_region_id = dcs_id[:-3]
                    print("\t\t- ", dcs_id, dcs_name, match_score)
                    if parent_region_id != previous_parent_region_id:
                        lines.append("    " + "# --------")
                        lines.append("    " + f"# {parent_region_id}")
                        lines.append("    " + "# --------")
                        previous_parent_region_id = parent_region_id
                    n_match_1 += 1
                    lines.append(
                        "    "
                        + f'"{hum_id}": "{dcs_id}",'
                        + f"  # {n_match_1:03d}."
                        + f" {hum_name} -> {dcs_name} ({match_score})"
                    )
                    break
        return n_match_1

    @staticmethod
    def _append_match_2_lines(
        lines,
        n_match_1,
        parent_id_to_hum_ids,
        parent_id_to_dcs_ids,
        region_id_to_name_hum,
        region_id_to_name_dcs,
    ):
        if n_match_1:
            return

        n_match_2 = 0
        lines.extend(
            [
                "    #",
                "    # " + "=" * 64,
                "    # MATCH 2 - Parent with same num of unmatched HUM & DCS",
                "    # " + "=" * 64,
                "    #",
            ]
        )

        for parent_id, hum_ids in parent_id_to_hum_ids.items():
            hum_ids = sorted(hum_ids)
            dcs_ids = parent_id_to_dcs_ids.get(parent_id, [])
            dcs_ids = sorted(dcs_ids)
            if len(hum_ids) != len(dcs_ids):
                continue
            print("\tPARENT ", parent_id)
            for hum_id in hum_ids:
                hum_name = region_id_to_name_hum[hum_id]
                print("\t\t- HUM ", hum_id, hum_name)
            for dcs_id in dcs_ids:
                dcs_name = region_id_to_name_dcs[dcs_id]
                print("\t\t- DCS ", dcs_id, dcs_name)

            for hum_id, dcs_id in zip(hum_ids, dcs_ids):
                hum_name = region_id_to_name_hum[hum_id]
                dcs_name = region_id_to_name_dcs[dcs_id]
                match_score = fuzz.ratio(dcs_name, hum_name)
                n_match_2 += 1
                lines.append(
                    "    "
                    + f'"{hum_id}": "{dcs_id}",'
                    + f"  # {n_match_1 + n_match_2:03d}."
                    + f" {hum_name} -> {dcs_name} ({match_score})"
                )

    @staticmethod
    def _print_name_mismatches(
        dcs_minus_hum,
        hum_minus_dcs,
        region_id_to_name_dcs,
        region_id_to_name_hum,
    ):
        if dcs_minus_hum != set() or hum_minus_dcs != set():
            return

        print("✅ IDs MATCH")
        n_mismatch = 0
        for region_id in region_id_to_name_dcs:
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

    @staticmethod
    def _write_output(var_name, lines):
        lines.extend(
            [
                "}",
                "",
            ]
        )
        lines_file = File(os.path.join("workflows", f"{var_name}.DRAFT.py"))
        lines_file.write("\n".join(lines))
        print(f"Wrote {lines_file}")

    @staticmethod
    def combine(dcs_region_label, hum_admin_level):
        var_name = f"ID_CORRECTION_MAP_{dcs_region_label}"
        lines = [
            "# ⚠️ Auto Generated by workflows/temp_analyze.py. REVIEW MANUALLY.",
            "# flake8: noqa: E501",
            "",
            "",
            f"{var_name} = {{",
        ]
        print("-" * 32)
        print("LEVEL ", hum_admin_level, dcs_region_label)
        print("-" * 32)

        (
            region_id_to_name_dcs,
            region_id_to_name_hum,
        ) = CombineDCSAndHumData._build_region_name_maps(
            dcs_region_label, hum_admin_level
        )

        # IMPORTANT: For a DCS and HUM region to match,
        # they should match in both id (exactly) name (similar)

        dcs_minus_hum, hum_minus_dcs, n_match_0 = (
            CombineDCSAndHumData._find_unmatched_ids(
                region_id_to_name_dcs, region_id_to_name_hum
            )
        )

        parent_id_to_hum_ids = CombineDCSAndHumData._build_parent_to_ids(
            hum_minus_dcs
        )
        parent_id_to_dcs_ids = CombineDCSAndHumData._build_parent_to_ids(
            dcs_minus_hum
        )
        CombineDCSAndHumData._print_parent_groups(
            parent_id_to_hum_ids,
            parent_id_to_dcs_ids,
            region_id_to_name_hum,
            region_id_to_name_dcs,
        )

        # ATTEMPT TO MATCH

        n_match_1 = CombineDCSAndHumData._append_match_1_lines(
            lines,
            hum_minus_dcs,
            dcs_minus_hum,
            region_id_to_name_hum,
            region_id_to_name_dcs,
        )

        # MATCH 2 - Check if some parent has exactly one DCS Gnd without a match,
        # and exaclty one HUM Gnd without a match

        CombineDCSAndHumData._append_match_2_lines(
            lines,
            n_match_1,
            parent_id_to_hum_ids,
            parent_id_to_dcs_ids,
            region_id_to_name_hum,
            region_id_to_name_dcs,
        )

        CombineDCSAndHumData._print_name_mismatches(
            dcs_minus_hum,
            hum_minus_dcs,
            region_id_to_name_dcs,
            region_id_to_name_hum,
        )

        print(" ")
        CombineDCSAndHumData._write_output(var_name, lines)

        print("-" * 32)
        print("DCS ^ HUM = ", n_match_0)
        print("DCS - HUM = ", len(dcs_minus_hum))
        print("HUM - DCS = ", len(hum_minus_dcs))
        print("TOTAL MISMATCHES = ", len(dcs_minus_hum) + len(hum_minus_dcs))

    @staticmethod
    def compare(dcs_region_label, hum_admin_level):
        return CombineDCSAndHumData.combine(dcs_region_label, hum_admin_level)


if __name__ == "__main__":
    for dcs_region_label, hum_admin_level in [
        # ("province", 1),
        # ("district", 2),
        # ("dsd", 3),
        ("gnd", 4),
    ]:
        CombineDCSAndHumData.compare(dcs_region_label, hum_admin_level)
