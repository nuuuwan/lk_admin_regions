from lk_admin_regions import (BuildEnts, BuildGeo, BuildGNDEnt,
                              BuildNonAdminGeo, CombineDCSAndHumData,
                              GNDListFinalXLSX, RegionsHistory)


def main():
    GNDListFinalXLSX.build_gnd_table()
    CombineDCSAndHumData.combine(dcs_region_label="gnd", hum_admin_level=4)

    BuildGNDEnt.build()
    BuildEnts.build_all()
    BuildGeo.build_all()
    BuildNonAdminGeo.build_all()

    RegionsHistory.build_all()

    BuildGeo.cleanup_big_files()


if __name__ == "__main__":
    main()
