import os

from utils import Log

from lk_admin_regions.builder.BuildEnts import BuildEnts
from lk_admin_regions.builder.BuildGNDEnt import BuildGNDEnt
from lk_admin_regions.history.RegionsHistorySpec import RegionsHistorySpec

log = Log("RegionsHistory")


class RegionsHistory:
    DIR_DATA_ENTS_HISTORY = os.path.join(BuildGNDEnt.DIR_DATA_ENTS, "history")

    @classmethod
    def apply_changes(
        cls, regions, aux_region_idx, year, modified_list, deleted_list
    ):
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

        for mod in modified_list:
            base_id = mod["id"]
            current_ids = mod["current_ids"]
            name = mod.get("name")
            mod_year = mod.get("year_last_modified", year)
            d_base = region_idx[base_id]
            for cid in current_ids:
                if cid == base_id:
                    continue
                if cid in region_idx:
                    d_other = region_idx[cid]
                elif cid in aux_region_idx:
                    d_other = aux_region_idx[cid]
                else:
                    log.warning(f"ID {cid} not found in any region type")
                    continue
                total_area = d_base["area_sqkm"] + d_other["area_sqkm"]
                d_base["center_lat"] = (
                    d_base["center_lat"] * d_base["area_sqkm"]
                    + d_other["center_lat"] * d_other["area_sqkm"]
                ) / total_area
                d_base["center_lng"] = (
                    d_base["center_lng"] * d_base["area_sqkm"]
                    + d_other["center_lng"] * d_other["area_sqkm"]
                ) / total_area
                d_base["area_sqkm"] = total_area
            d_base["current_ids"] = sorted(set(current_ids))
            d_base["area_sqkm"] = round(d_base["area_sqkm"], 2)
            d_base["center_lat"] = round(d_base["center_lat"], 6)
            d_base["center_lng"] = round(d_base["center_lng"], 6)
            d_base["id"] = f"{base_id}-pre{mod_year}"
            d_base["name"] = (
                name if name else f"{d_base['name']} (pre {mod_year})"
            )
            region_idx[base_id] = d_base

        for del_item in deleted_list:
            del_id = del_item["id"]
            if del_id in region_idx:
                del region_idx[del_id]

        new_regions = list(region_idx.values())
        new_regions.sort(key=lambda d: d["id"])
        return new_regions

    @classmethod
    def build_region(cls, region_type_name, year_info_list):
        os.makedirs(cls.DIR_DATA_ENTS_HISTORY, exist_ok=True)

        for year_info in year_info_list:
            year = year_info["year"]
            regions = BuildEnts.read(region_type_name)
            aux_region_idx = {
                d["id"]: dict(
                    id=d["id"],
                    name=d["name"],
                    area_sqkm=float(d["area_sqkm"]),
                    center_lat=float(d["center_lat"]),
                    center_lng=float(d["center_lng"]),
                )
                for aux_type in year_info.get("aux_region_types", [])
                for d in BuildEnts.read(aux_type)
            }
            regions = cls.apply_changes(
                regions,
                aux_region_idx,
                year,
                year_info.get("modified", []),
                year_info.get("deleted", []),
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
        for (
            region_type_name,
            year_info_list,
        ) in RegionsHistorySpec.get().items():
            cls.build_region(region_type_name, year_info_list)
