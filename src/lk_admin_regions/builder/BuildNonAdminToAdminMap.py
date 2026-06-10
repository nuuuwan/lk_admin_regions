import os

from utils import JSONFile, Log

from lk_admin_regions.builder.BuildEnts import BuildEnts

log = Log("BuildNonAdminToAdminMap")


class BuildNonAdminToAdminMap:

    @staticmethod
    def build_parent_to_gnd_map():
        gnds = BuildEnts.read("gnd")
        idx = {}
        for parent_type in ["district", "dsd", "gnd", "pd", "ed", "lg"]:
            if parent_type not in idx:
                idx[parent_type] = {}
            parent_id_key = (
                f"{parent_type}_id" if parent_type != "gnd" else "id"
            )

            for gnd in gnds:
                gnd_id = gnd["id"]
                parent_id = gnd[parent_id_key]
                if parent_id not in idx[parent_type]:
                    idx[parent_type][parent_id] = set()
                idx[parent_type][parent_id].add(gnd_id)

        return idx

    @staticmethod
    def build():
        idx = BuildNonAdminToAdminMap.build_parent_to_gnd_map()
        for non_admin_type in ["pd", "ed", "lg"]:
            d_list = {}
            for non_admin_id, gnd_ids_for_non_admin_id in sorted(
                idx[non_admin_type].items(), key=lambda x: x[0]
            ):
                min_child_admin_type = None
                child_ids = []
                child_gnd_ids = set()
                for admin_type in ["district", "dsd", "gnd"]:
                    for admin_id, gnd_ids_for_admin_id in idx[
                        admin_type
                    ].items():
                        if gnd_ids_for_admin_id <= child_gnd_ids:
                            continue
                        if gnd_ids_for_admin_id <= gnd_ids_for_non_admin_id:
                            child_ids.append(admin_id)
                            child_gnd_ids.update(gnd_ids_for_admin_id)

                    if child_gnd_ids == gnd_ids_for_non_admin_id:
                        min_child_admin_type = admin_type
                        if len(child_ids) > 3:
                            print(
                                f"{non_admin_id}"
                                + f" ({len(child_ids)}/{min_child_admin_type})"
                                + f" = {child_ids[:3]}..."
                            )
                        else:
                            print(
                                f"{non_admin_id}"
                                + f" ({len(child_ids)}/{min_child_admin_type})"
                                + f" = {child_ids}"
                            )
                        break

                if min_child_admin_type is None:
                    print(f"{non_admin_id} = NONE")
                d = dict(
                    id=non_admin_id,
                    min_child_admin_type=min_child_admin_type,
                    child_ids=child_ids,
                )
                d_list[non_admin_id] = d
            non_admin_map_json_file = JSONFile(
                os.path.join(
                    "data_temp",
                    "non_admin_maps",
                    f"{non_admin_type}_to_admin_map.json",
                )
            )
            non_admin_map_json_file.write(d_list)
            log.info(f"Wrote {non_admin_map_json_file}")

    @staticmethod
    def compare(a_type, a_id, b_type, b_id):
        idx = BuildNonAdminToAdminMap.build_parent_to_gnd_map()
        gnds_for_a = idx[a_type][a_id]
        gnds_for_b = idx[b_type][b_id]
        common_gnds = gnds_for_a & gnds_for_b
        a_diff_b = gnds_for_a - gnds_for_b
        b_diff_a = gnds_for_b - gnds_for_a
        print("common_gnds", common_gnds)
        print("a_diff_b", a_diff_b)
        print("b_diff_a", b_diff_a)

    @staticmethod
    def similar_not_same():
        idx = BuildNonAdminToAdminMap.build_parent_to_gnd_map()
        for admin_type, non_admin_type in [
            ["district", "ed"],
            ["dsd", "pd"],
        ]:
            log.info(f"Comparing {admin_type} vs. {non_admin_type}")
            for admin_id, admin_gnds in sorted(
                idx[admin_type].items(), key=lambda x: x[0]
            ):
                for non_admin_id, non_admin_gnds in sorted(
                    idx[non_admin_type].items(), key=lambda x: x[0]
                ):
                    if admin_gnds == non_admin_gnds:
                        continue

                    common_gnds = admin_gnds & non_admin_gnds
                    if not common_gnds:
                        continue

                    admin_diff_non_admin = admin_gnds - non_admin_gnds
                    non_admin_diff_admin = non_admin_gnds - admin_gnds
                    uncommon_gnds = (
                        admin_diff_non_admin | non_admin_diff_admin
                    )

                    if (
                        len(common_gnds) > 5
                        and len(uncommon_gnds) < 5
                        and non_admin_diff_admin
                    ):
                        log.info(
                            f"{admin_id} vs. {non_admin_id}: "
                            + f" {len(common_gnds)} common"
                            + f" {len(uncommon_gnds)} uncommon"
                        )
                        log.debug(
                            "\tadmin_diff_non_admin = "
                            + ",".join(admin_diff_non_admin)
                        )
                        log.debug(
                            "\tnon_admin_diff_admin = "
                            + ",".join(non_admin_diff_admin)
                        )


if __name__ == "__main__":
    # BuildNonAdminToAdminMap.build()
    # BuildNonAdminToAdminMap.compare("pd", "EC-11C", "district", "LK-44")
    BuildNonAdminToAdminMap.similar_not_same()
