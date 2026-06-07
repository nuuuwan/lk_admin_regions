class RegionsHistorySpec:
    _DISTRICT_DELTAS = [
        dict(
            year="1984",
            modified=[
                dict(
                    id="LK-41",
                    current_ids=["LK-41", "LK-45"],
                    year_last_modified="1984",
                ),
            ],
            deleted=[dict(id="LK-45")],
        ),
        dict(
            year="1978",
            aux_region_types=["dsd"],
            modified=[
                dict(
                    id="LK-41",
                    current_ids=["LK-41", "LK-45", "LK-4409"],
                    year_last_modified="1978",
                ),  # Jaffna absorbed Puthukkudiyiruppu DSD (→ Mullaitivu)
                dict(
                    id="LK-11",
                    current_ids=["LK-11", "LK-12"],
                    year_last_modified="1978",
                ),
                dict(
                    id="LK-42",
                    current_ids=["LK-42", "LK-4403", "LK-4406"],
                    year_last_modified="1978",
                    # Mannar absorbed Thunukkai + Manthai East DSDs (→
                    # Mullaitivu)
                ),
                dict(
                    id="LK-43",
                    current_ids=["LK-43", "LK-4412", "LK-4415", "LK-4418"],
                    year_last_modified="1978",
                ),  # Vavuniya absorbed Oddusuddan + Maritimepattu + Welioya DSDs
            ],
            deleted=[dict(id="LK-12"), dict(id="LK-44")],
        ),
        dict(
            year="1961",
            modified=[
                dict(
                    id="LK-51",
                    current_ids=["LK-51", "LK-52"],
                    year_last_modified="1961",
                ),
            ],
            deleted=[dict(id="LK-52")],
        ),
        dict(
            year="1959",
            modified=[
                dict(
                    id="LK-81",
                    current_ids=["LK-81", "LK-82"],
                    year_last_modified="1959",
                ),
            ],
            deleted=[dict(id="LK-82")],
        ),
    ]

    _DSD_DELTAS = [
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
    ]

    @classmethod
    def _build_snapshots(cls, deltas):
        # deltas: ordered most-recent year first.
        # For snapshot at index i, accumulate deltas[0..i].
        # Processing order is most-recent → oldest; older entries overwrite newer
        # ones (last-write wins), ensuring the correct year_last_modified is
        # used.
        snapshots = []
        for i, delta in enumerate(deltas):
            merged_modified = {}
            merged_deleted = {}
            merged_aux = set()
            for d in deltas[: i + 1]:
                for mod in d.get("modified", []):
                    merged_modified[mod["id"]] = mod
                for del_item in d.get("deleted", []):
                    merged_deleted[del_item["id"]] = del_item
                for aux in d.get("aux_region_types", []):
                    merged_aux.add(aux)
            snapshot = dict(year=delta["year"])
            if merged_aux:
                snapshot["aux_region_types"] = sorted(merged_aux)
            snapshot["modified"] = list(merged_modified.values())
            snapshot["deleted"] = list(merged_deleted.values())
            snapshots.append(snapshot)
        return snapshots

    @classmethod
    def get(cls):
        return dict(
            district=cls._build_snapshots(cls._DISTRICT_DELTAS),
            dsd=cls._build_snapshots(cls._DSD_DELTAS),
            province=cls._build_snapshots(cls._PROVINCE_DELTAS),
        )

    _PROVINCE_DELTAS = [
        # 1889: Sabaragamuwa (LK-9) carved from Southern (LK-3) and Western
        # (LK-1)
        dict(
            year="1889",
            aux_region_types=["district"],
            modified=[
                dict(
                    id="LK-1",
                    current_ids=["LK-1", "LK-92"],
                    year_last_modified="1889",
                ),
                dict(
                    id="LK-3",
                    current_ids=[
                        "LK-3",
                        "LK-91",
                        "LK-8221",
                        "LK-8224",
                        "LK-8227",
                        "LK-8230",
                        "LK-8233",
                    ],
                    year_last_modified="1889",
                ),
            ],
            deleted=[dict(id="LK-9")],
        ),
        dict(
            year="1886",
            aux_region_types=["district", "dsd"],
            modified=[
                dict(
                    id="LK-2",
                    current_ids=["LK-2", "LK-81"],
                    year_last_modified="1886",
                ),
                dict(
                    id="LK-3",
                    current_ids=[
                        "LK-3",
                        "LK-91",
                        "LK-8221",
                        "LK-8224",
                        "LK-8227",
                        "LK-8230",
                        "LK-8233",
                    ],
                    year_last_modified="1886",
                ),
                dict(
                    id="LK-5",
                    current_ids=[
                        "LK-5",
                        "LK-8218",
                        "LK-8215",
                        "LK-8212",
                        "LK-8209",
                        "LK-8206",
                        "LK-8203",
                    ],
                    year_last_modified="1886",
                ),
            ],
            deleted=[dict(id="LK-8")],
        ),
        dict(
            year="1873",
            aux_region_types=["district"],
            modified=[
                dict(
                    id="LK-4",
                    current_ids=["LK-4", "LK-71"],
                    year_last_modified="1873",
                ),
                dict(
                    id="LK-5",
                    current_ids=[
                        "LK-5",
                        "LK-72",
                        "LK-8218",
                        "LK-8215",
                        "LK-8212",
                        "LK-8209",
                        "LK-8206",
                        "LK-8203",
                    ],
                    year_last_modified="1873",
                ),
            ],
            deleted=[dict(id="LK-7")],
        ),
        # 1845: North Western (LK-6) carved from Western (LK-1)
        dict(
            year="1845",
            aux_region_types=["district", "dsd"],
            modified=[
                dict(
                    id="LK-1",
                    current_ids=[
                        "LK-1",
                        "LK-92",
                        "LK-61",
                        "LK-6203",
                        "LK-6215",
                        "LK-6218",
                        "LK-6221",
                        "LK-6224",
                        "LK-6227",
                        "LK-6230",
                        "LK-6233",
                        "LK-6236",
                        "LK-6239",
                        "LK-6242",
                        "LK-6245",
                        "LK-6248",
                    ],
                    year_last_modified="1845",
                ),
                dict(
                    id="LK-4",
                    current_ids=[
                        "LK-4",
                        "LK-71",
                        "LK-6206",
                        "LK-6209",
                        "LK-6212",
                    ],
                    year_last_modified="1845",
                ),
            ],
            deleted=[dict(id="LK-6")],
        ),
    ]
