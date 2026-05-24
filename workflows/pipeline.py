import os

from lk_admin_regions import BuildEnts, BuildGeo, CombineDCSAndHumData

if __name__ == "__main__":
    CombineDCSAndHumData.combine(dcs_region_label="gnd", hum_admin_level=4)
    BuildEnts.build_all()
    BuildGeo.build_all()
    os.system("find data -type f -size +25M -delete")
