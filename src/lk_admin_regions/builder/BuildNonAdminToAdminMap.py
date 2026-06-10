from lk_admin_regions.builder.BuildGNDEnt import BuildGNDEnt


class BuildNonAdminToAdminMap:

    @staticmethod
    def build_parent_to_gnd_map():
        gnds = BuildGNDEnt.read_denormalized_gnds()
        idx = {}
        for parent_type in ["district", "dsd", "gnd", "pd", "ed", "lg"]:
            if parent_type not in idx:
                idx[parent_type] = {}
            parent_id_key = f"{parent_type}_id"

            for gnd in gnds:
                gnd_id = gnd["gnd_id"]
                parent_id = gnd[parent_id_key]
                if parent_id not in idx[parent_type]:
                    idx[parent_type][parent_id] = set()
                idx[parent_type][parent_id].add(gnd_id)

        return idx

    @staticmethod
    def build():
        idx = BuildNonAdminToAdminMap.build_parent_to_gnd_map()
        for non_admin_type in ["pd"]:
            for non_admin_id, gnd_ids_for_non_admin_id in sorted(
                idx[non_admin_type].items(), key=lambda x: x[0]
            ):
                child_admin_type = None
                for admin_type in ["district", "dsd"]:
                    child_ids = []
                    child_gnd_ids = set()
                    for admin_id, gnd_ids_for_admin_id in idx[
                        admin_type
                    ].items():
                        if gnd_ids_for_admin_id <= gnd_ids_for_non_admin_id:
                            child_ids.append(admin_id)
                            child_gnd_ids.update(gnd_ids_for_admin_id)

                    if child_gnd_ids == gnd_ids_for_non_admin_id:
                        print(f"{non_admin_id} = {child_ids}")
                        child_admin_type = admin_type
                        break

                if child_admin_type is None:
                    print(f"{non_admin_id} = NONE")

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


if __name__ == "__main__":
    BuildNonAdminToAdminMap.build()
    BuildNonAdminToAdminMap.compare("pd", "EC-11C", "district", "LK-44")
