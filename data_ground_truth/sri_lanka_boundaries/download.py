import os
from multiprocessing import Pool

import geopandas as gpd
import pandas as pd
from utils import File, Log

log = Log("download")

PAGE_SIZE = 500


def download_chunk(offset):
    layer_id = 1
    base = (
        "https://gisapps.nsdi.gov.lk/server/rest/services/"
        "Srilanka/Boundaries/MapServer/"
    )
    url = base + f"{layer_id}/query"
    q = (
        f"{url}?where=1=1"
        f"&outFields=*"
        f"&f=geojson"
        f"&resultOffset={offset}"
        f"&resultRecordCount={PAGE_SIZE}"
    )

    gdf = gpd.read_file(q)
    log.debug(f"Downloaded {len(gdf):,} records from {q}")
    return gdf


def main():

    output_path = os.path.join(
        "data_ground_truth",
        "sri_lanka_boundaries",
        "gnd.geojson",
    )

    chunks = Pool().map(download_chunk, range(0, 15_000, PAGE_SIZE))
    gdf_concat = pd.concat(chunks, ignore_index=True)
    gdf_concat = gdf_concat.sort_values(by="admin_code").reset_index(drop=True)
    gdf_concat.to_file(output_path, driver="GeoJSON")
    log.info(f"Wrote {len(gdf_concat):,} records to {File(output_path)}")


if __name__ == "__main__":
    main()
