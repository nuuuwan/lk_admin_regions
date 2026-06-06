import os

from utils import Log

from lk_admin_regions.builder.BuildEnts import BuildEnts
from lk_admin_regions.builder.BuildGNDEnt import BuildGNDEnt

log = Log("RegionsHistory")


class RegionsHistory:
    DIR_DATA_ENTS_HISTORY = os.path.join(BuildGNDEnt.DIR_DATA_ENTS, "history")

    @classmethod
    def split(cls, regions, year, old_id, new_id):
        region_idx = {
            d["id"]: dict(
                id=d["id"],
                name=d["name"],
                area_sqkm=float(d["area_sqkm"]),
                center_lat=float(d["center_lat"]),
                center_lng=float(d["center_lng"]),
                current_ids=d.get("current_ids", [d["id"]]),
            )
            for d in regions
        }
        d_old = region_idx[old_id]
        d_new = region_idx[new_id]

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

        current_ids = (
            [old_id, new_id]
            + d_new.get("current_ids", [])
            + d_old.get("current_ids", [])
        )
        current_ids = sorted(set(current_ids))
        d_old["current_ids"] = current_ids

        region_idx[old_id] = d_old
        del region_idx[new_id]
        new_regions = list(region_idx.values())
        new_regions.sort(key=lambda d: d["id"])
        return new_regions

    @classmethod
    def build_region(cls, region_type_name, split_info_list):
        os.makedirs(cls.DIR_DATA_ENTS_HISTORY, exist_ok=True)
        regions = BuildEnts.read(region_type_name)

        for year_info in split_info_list:
            year = year_info["year"]
            for split in year_info["splits"]:
                regions = cls.split(
                    regions, year, split["old_id"], split["new_id"]
                )
            regions_path_base = os.path.join(
                cls.DIR_DATA_ENTS_HISTORY,
                f"{region_type_name}s-pre{year}",
            )
            log.info(
                f"Writing {len(regions)} {region_type_name}s"
                + f" to {regions_path_base}.[json|tsv]"
            )
            BuildGNDEnt.write_all_types(regions, regions_path_base)

    @classmethod
    def build_all(cls):
        for region_type_name, split_info_list in dict(
            district=[
                dict(
                    year="1984", splits=[dict(old_id="LK-41", new_id="LK-45")]
                ),
                dict(
                    year="1978", splits=[dict(old_id="LK-11", new_id="LK-12")]
                ),
                dict(
                    year="1961", splits=[dict(old_id="LK-51", new_id="LK-52")]
                ),
                dict(
                    year="1959", splits=[dict(old_id="LK-81", new_id="LK-82")]
                ),
            ]
        ).items():
            cls.build_region(region_type_name, split_info_list)
