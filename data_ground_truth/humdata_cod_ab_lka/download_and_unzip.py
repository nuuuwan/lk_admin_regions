import os
import urllib.request
import zipfile

from utils import File, Log

log = Log("download")

DIR_SOURCE = os.path.join(
    "data_ground_truth",
    "humdata_cod_ab_lka",
)

URL = "https://data.humdata.org/dataset/0bedcaf3-88cd-4591-b9d5-5d3220e26abf/resource/ac173fa4-dd42-4be4-aaed-a2e445525865/download/lka_admin_boundaries.geojson.zip"

ZIP_PATH = os.path.join(
    DIR_SOURCE,
    "lka_admin_boundaries.geojson.zip",
)

DIR_UNZIPPED = os.path.join(DIR_SOURCE, "lka_admin_boundaries")


def download():
    if os.path.exists(ZIP_PATH):
        log.warning(f"☑️ {File(ZIP_PATH)} already exists. Skipping download.")
        return
    log.debug(f"Downloading {URL} to {ZIP_PATH}...")
    urllib.request.URLretrieve(URL, ZIP_PATH)
    log.info(f"✅ Downloaded {URL} to {File(ZIP_PATH)}")


def unzip():
    log.debug(f"Unzipping {ZIP_PATH} to {DIR_UNZIPPED}...")
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extractall(DIR_UNZIPPED)
    log.info(f"✅ Unzipped {File(ZIP_PATH)} to {File(DIR_UNZIPPED)}")


if __name__ == "__main__":
    download()
    unzip()
