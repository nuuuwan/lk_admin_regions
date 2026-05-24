import os

from lk_admin_regions import (
    BuildEnts,
    BuildGeo,
    BuildNonAdminEnts,
    BuildNonAdminGeo,
    CombineDCSAndHumData,
    GNDListFinalXLSX,
)


def main():
    GNDListFinalXLSX.build_gnd_table()
    CombineDCSAndHumData.combine(dcs_region_label="gnd", hum_admin_level=4)

    BuildEnts.build_all()
    BuildGeo.build_all()

    BuildNonAdminEnts.build_all()
    BuildNonAdminGeo.build_all()

    os.system("find data -type f -size +25M -delete")


if __name__ == "__main__":
    main()
