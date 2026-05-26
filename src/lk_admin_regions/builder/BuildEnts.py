import os
from functools import cache

from utils import Log, TSVFile

from lk_admin_regions.builder.BuildGNDEnt import BuildGNDEnt

log = Log("BuildEnts")

LIM_FUZZ_RATIO = 80
LIM_FUZZ_RATIO2 = 60


class BuildEnts:
    DIR_DATA = "data"
    DIR_DATA_ENTS = os.path.join(DIR_DATA, "ents")

    @classmethod
    def build_parent(cls, parent_label, expand_gnd=None, extra_fields=None):

        denormalized_gnds = BuildGNDEnt.read_denormalized_gnds()
        if expand_gnd:
            denormalized_gnds = [expand_gnd(gnd) for gnd in denormalized_gnds]

        id_key = f"{parent_label}_id"
        name_key = f"{parent_label}_name"

        gnds_by_parent = {}
        for gnd in denormalized_gnds:
            parent_id = gnd[id_key]
            if parent_id not in gnds_by_parent:
                gnds_by_parent[parent_id] = []
            gnds_by_parent[parent_id].append(gnd)

        parents = []
        for parent_id, gnds_for_parent in gnds_by_parent.items():
            parent_name = gnds_for_parent[0][name_key]

            w_area_sqkm = 0
            w_center_lat = 0
            w_center_lng = 0
            for gnd in gnds_for_parent:
                area_sqkm = float(gnd["area_sqkm"])
                w_area_sqkm += area_sqkm
                w_center_lat += area_sqkm * float(gnd["center_lat"])
                w_center_lng += area_sqkm * float(gnd["center_lng"])

            center_lat = w_center_lat / w_area_sqkm if w_area_sqkm else 0
            center_lng = w_center_lng / w_area_sqkm if w_area_sqkm else 0

            parent_d = dict(
                id=parent_id,
                name=parent_name,
                area_sqkm=round(w_area_sqkm, 2),
                center_lat=round(center_lat, 6),
                center_lng=round(center_lng, 6),
            )
            if extra_fields:
                for k in extra_fields:
                    parent_d[k] = gnds_for_parent[0][k]

            parents.append(parent_d)

        parents.sort(key=lambda d: d["id"])
        BuildGNDEnt.write_all_types(
            parents,
            os.path.join(cls.DIR_DATA_ENTS, f"{parent_label}s"),
        )

    @classmethod
    def build_parents(cls):
        for parent_label in ["dsd", "district", "province", "country"]:
            cls.build_parent(parent_label)

    @classmethod
    def build_all(cls):
        cls.build_parents()

    @classmethod
    @cache
    def read(cls, ent_type_name):
        file_path = os.path.join(cls.DIR_DATA_ENTS, f"{ent_type_name}s.tsv")
        return TSVFile(file_path).read()


if __name__ == "__main__":
    BuildEnts.build_all()
