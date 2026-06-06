import os

from utils import Log

from lk_admin_regions.builder.BuildEnts import BuildEnts
from lk_admin_regions.builder.BuildGNDEnt import BuildGNDEnt

log = Log("DistrictHistory")


class DistrictHistory:
    DIR_DATA_ENTS_HISTORY = os.path.join(BuildGNDEnt.DIR_DATA_ENTS, "history")

    @classmethod
    def split(cls, districts, year, old_id, new_id):
        district_idx = {
            d["id"]: dict(
                id=d["id"],
                name=d["name"],
                area_sqkm=float(d["area_sqkm"]),
                center_lat=float(d["center_lat"]),
                center_lng=float(d["center_lng"]),
            )
            for d in districts
        }
        d_old = district_idx[old_id]
        d_new = district_idx[new_id]

        d_old["center_lat"], d_old["center_lng"] = (
            d_old["center_lat"] * d_old["area_sqkm"]
            + d_new["center_lat"] * d_new["area_sqkm"]
        ) / (d_old["area_sqkm"] + d_new["area_sqkm"]), (
            d_old["center_lng"] * d_old["area_sqkm"]
            + d_new["center_lng"] * d_new["area_sqkm"]
        ) / (
            d_old["area_sqkm"] + d_new["area_sqkm"]
        )
        d_old["area_sqkm"] += d_new["area_sqkm"]
        d_old["id"] = f"{old_id}-pre{year}"

        district_idx[old_id] = d_old
        del district_idx[new_id]
        new_districts = list(district_idx.values())
        new_districts.sort(key=lambda d: d["id"])
        return new_districts

    @classmethod
    def build_all(cls):
        os.makedirs(cls.DIR_DATA_ENTS_HISTORY, exist_ok=True)
        districts = BuildEnts.read("district")

        for year, old_id, new_id in [
            ("1984", "LK-41", "LK-45"),
            ("1978", "LK-11", "LK-12"),
            ("1961", "LK-51", "LK-52"),
            ("1959", "LK-81", "LK-82"),
        ]:
            districts = cls.split(districts, year, old_id, new_id)
            districts_path_base = os.path.join(
                cls.DIR_DATA_ENTS_HISTORY, f"districts-pre{year}"
            )
            log.info(
                f"Writing {len(districts)} districts"
                + f" to {districts_path_base}.[json|tsv]"
            )
            BuildGNDEnt.write_all_types(districts, districts_path_base)


if __name__ == "__main__":
    DistrictHistory.build_all()
