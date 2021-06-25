import json
import os
import urllib.request
from functools import partial
from pathlib import Path
import argparse
from urllib.parse import urlparse

from tqdm import tqdm


def download_with_progress_bar(link, target_dir):
    size = urllib.request.urlopen(link).info().get('Content-Length')
    size = int(size) if size else None
    pbar = tqdm(total=size)

    def show_progress(block_num, block_size, total_size):
        pbar.update(block_size)

    urllib.request.urlretrieve(link, target_dir, show_progress)
    pbar.close()


def main(dataset_links_file: Path, target_dir: Path):
    datasets = json.load(dataset_links_file.open())

    for dataset in datasets:
        try:
            download = dataset.get("download", True)
            if not download:
                print(f"Please download the dataset {dataset['name']} manually:\n{dataset['links']}")
                continue
            print(f"Downloading {dataset['name']} ...")
            dataset_path = target_dir.joinpath(dataset["name"].replace(" ","_"))
            dataset_path.mkdir(exist_ok=True)
            for link in dataset["links"]:
                link_file_name = os.path.basename(urlparse(link).path)
                download_with_progress_bar(link, dataset_path.joinpath(link_file_name))
        except Exception as e:
            print(f"Something went wrong. Please try to download {dataset['name']} manually:\n{dataset['links']}")
            raise e



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_links_file", default="dataset_links.json", type=Path)
    parser.add_argument("--target_dir", default="./", type=Path)
    args = parser.parse_args()

    main(args.dataset_links_file, args.target_dir)