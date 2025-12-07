from lk_admin_regions import BuildEnts, BuildGeo

if __name__ == "__main__":
    BuildEnts.build_all()
    BuildGeo.build_all()
    BuildGeo._HACK_delete_large_files()
