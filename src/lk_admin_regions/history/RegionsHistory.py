import os

from utils import Log

from lk_admin_regions.builder.BuildEnts import BuildEnts
from lk_admin_regions.builder.BuildGNDEnt import BuildGNDEnt

log = Log("RegionsHistory")


class RegionsHistory:
    DIR_DATA_ENTS_HISTORY = os.path.join(BuildGNDEnt.DIR_DATA_ENTS, "history")

    @classmethod
    def apply_changes(cls, regions, year, modified_list, deleted_list):
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
                d_other = region_idx[cid]
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
            regions = cls.apply_changes(
                regions,
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
        for region_type_name, year_info_list in dict(
            district=[
                dict(
                    year="1984",
                    modified=[
                        dict(
                            id="LK-41",
                            current_ids=["LK-41", "LK-45"],
                            year_last_modified="1984",
                        ),
                    ],
                    deleted=[
                        dict(id="LK-45"),
                    ],
                ),
                dict(
                    year="1978",
                    modified=[
                        dict(
                            id="LK-41",
                            current_ids=["LK-41", "LK-45"],
                            year_last_modified="1984",
                        ),
                        dict(
                            id="LK-11",
                            current_ids=["LK-11", "LK-12"],
                            year_last_modified="1978",
                        ),
                    ],
                    deleted=[
                        dict(id="LK-45"),
                        dict(id="LK-12"),
                    ],
                ),
                dict(
                    year="1961",
                    modified=[
                        dict(
                            id="LK-41",
                            current_ids=["LK-41", "LK-45"],
                            year_last_modified="1984",
                        ),
                        dict(
                            id="LK-11",
                            current_ids=["LK-11", "LK-12"],
                            year_last_modified="1978",
                        ),
                        dict(
                            id="LK-51",
                            current_ids=["LK-51", "LK-52"],
                            year_last_modified="1961",
                        ),
                    ],
                    deleted=[
                        dict(id="LK-45"),
                        dict(id="LK-12"),
                        dict(id="LK-52"),
                    ],
                ),
                dict(
                    year="1959",
                    modified=[
                        dict(
                            id="LK-41",
                            current_ids=["LK-41", "LK-45"],
                            year_last_modified="1984",
                        ),
                        dict(
                            id="LK-11",
                            current_ids=["LK-11", "LK-12"],
                            year_last_modified="1978",
                        ),
                        dict(
                            id="LK-51",
                            current_ids=["LK-51", "LK-52"],
                            year_last_modified="1961",
                        ),
                        dict(
                            id="LK-81",
                            current_ids=["LK-81", "LK-82"],
                            year_last_modified="1959",
                        ),
                    ],
                    deleted=[
                        dict(id="LK-45"),
                        dict(id="LK-12"),
                        dict(id="LK-52"),
                        dict(id="LK-82"),
                    ],
                ),
            ],
            dsd=[
                # Gazette No. 2147/28 (2019-10-29)
                # Nuwara-Eliya, Galle, Ratnapura splits
                dict(
                    year="2019",
                    modified=[
                        dict(
                            id="LK-2303",
                            current_ids=["LK-2302", "LK-2303"],
                            name="Kotmale",
                            year_last_modified="2019",
                        ),  # Kothmale → Kothmale East + Kothmale West
                        dict(
                            id="LK-2306",
                            current_ids=["LK-2306", "LK-2307"],
                            year_last_modified="2019",
                        ),  # Hanguranketha → Hanguranketha + Mathurata
                        dict(
                            id="LK-2309",
                            current_ids=["LK-2309", "LK-2310"],
                            year_last_modified="2019",
                        ),  # Walapane → Walapane + Niladandahinna
                        dict(
                            id="LK-2312",
                            current_ids=["LK-2312", "LK-2313"],
                            year_last_modified="2019",
                        ),  # Nuwara-Eliya → Nuwara-Eliya + Thalawakelle
                        dict(
                            id="LK-2315",
                            current_ids=["LK-2314", "LK-2315"],
                            name="Ambagamuwa",
                            year_last_modified="2019",
                        ),  # Ambagamuwa → Ambagamuwa Korale + Norwood
                        dict(
                            id="LK-3136",
                            current_ids=["LK-3135", "LK-3136", "LK-3137"],
                            year_last_modified="2019",
                        ),  # Hikkaduwa → Hikkaduwa + Rathgama + Madampagama
                        dict(
                            id="LK-3127",
                            current_ids=["LK-3127", "LK-3128"],
                            year_last_modified="2019",
                        ),  # Baddegama → Baddegama + Wanduramba
                        dict(
                            id="LK-9118",
                            current_ids=["LK-9118", "LK-9119"],
                            year_last_modified="2019",
                        ),  # Balangoda → Balangoda + Kaltota
                    ],
                    deleted=[
                        dict(id="LK-2302"),
                        dict(id="LK-2307"),
                        dict(id="LK-2310"),
                        dict(id="LK-2313"),
                        dict(id="LK-2314"),
                        dict(id="LK-3135"),
                        dict(id="LK-3137"),
                        dict(id="LK-3128"),
                        dict(id="LK-9119"),
                    ],
                ),
            ],
        ).items():
            cls.build_region(region_type_name, year_info_list)
