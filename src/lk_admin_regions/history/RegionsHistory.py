import os

from utils import Log

from lk_admin_regions.builder.BuildEnts import BuildEnts
from lk_admin_regions.builder.BuildGNDEnt import BuildGNDEnt

log = Log("RegionsHistory")


class RegionsHistory:
    DIR_DATA_ENTS_HISTORY = os.path.join(BuildGNDEnt.DIR_DATA_ENTS, "history")

    @classmethod
    def split(cls, regions, year, old_id, new_ids, old_name=None):
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

        for new_id in new_ids:
            d_new = region_idx[new_id]
            total_area = d_old["area_sqkm"] + d_new["area_sqkm"]
            d_old["center_lat"] = (
                d_old["center_lat"] * d_old["area_sqkm"]
                + d_new["center_lat"] * d_new["area_sqkm"]
            ) / total_area
            d_old["center_lng"] = (
                d_old["center_lng"] * d_old["area_sqkm"]
                + d_new["center_lng"] * d_new["area_sqkm"]
            ) / total_area
            d_old["area_sqkm"] = total_area
            current_ids = (
                [old_id, new_id]
                + d_new.get("current_ids", [])
                + d_old.get("current_ids", [])
            )
            d_old["current_ids"] = sorted(set(current_ids))
            del region_idx[new_id]

        d_old["id"] = f"{old_id}-pre{year}"
        if old_name:
            d_old["name"] = old_name
        region_idx[old_id] = d_old
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
                    regions,
                    year,
                    split["old_id"],
                    split["new_ids"],
                    split.get("old_name"),
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
                    year="1984",
                    splits=[dict(old_id="LK-41", new_ids=["LK-45"])],
                ),
                dict(
                    year="1978",
                    splits=[dict(old_id="LK-11", new_ids=["LK-12"])],
                ),
                dict(
                    year="1961",
                    splits=[dict(old_id="LK-51", new_ids=["LK-52"])],
                ),
                dict(
                    year="1959",
                    splits=[dict(old_id="LK-81", new_ids=["LK-82"])],
                ),
            ],
            dsd=[
                # Gazette No. 2147/28 (2019-10-29)
                # Nuwara-Eliya, Galle, Ratnapura splits
                dict(
                    year="2019",
                    splits=[
                        dict(
                            old_id="LK-2303",
                            old_name="Kotmale",
                            new_ids=["LK-2302"],
                        ),  # Kothmale → Kothmale East + Kothmale West
                        dict(
                            old_id="LK-2306", new_ids=["LK-2307"]
                        ),  # Hanguranketha → Hanguranketha + Mathurata
                        dict(
                            old_id="LK-2309", new_ids=["LK-2310"]
                        ),  # Walapane → Walapane + Niladandahinna
                        dict(
                            old_id="LK-2312", new_ids=["LK-2313"]
                        ),  # Nuwara-Eliya → Nuwara-Eliya + Thalawakelle
                        dict(
                            old_id="LK-2315",
                            old_name="Ambagamuwa",
                            new_ids=["LK-2314"],
                        ),  # Ambagamuwa → Ambagamuwa Korale + Norwood
                        dict(
                            old_id="LK-3136", new_ids=["LK-3137", "LK-3135"]
                        ),  # Hikkaduwa → Hikkaduwa + Rathgama + Madampagama
                        dict(
                            old_id="LK-3127", new_ids=["LK-3128"]
                        ),  # Baddegama → Baddegama + Wanduramba
                        dict(
                            old_id="LK-9118", new_ids=["LK-9119"]
                        ),  # Balangoda → Balangoda + Kaltota
                    ],
                ),
            ],
        ).items():
            cls.build_region(region_type_name, split_info_list)
