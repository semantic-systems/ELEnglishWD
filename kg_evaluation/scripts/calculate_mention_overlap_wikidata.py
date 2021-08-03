import json
import logging
from tqdm import tqdm
from argparse import ArgumentParser

from utilities.tools import split_uri_and_label


# Behaves similar to calculate_mention_overlap.py but only works with a prefiltered Wikidata n-triples file
def gather_ambiguous_mentions(filename="labels.nt", total=81065185, language=None):

    input_file = open(filename)

    line = input_file.readline()
    pbar = tqdm(total=total)

    mention_dict = {}
    while line:
        try:
            uri, label = split_uri_and_label(line)
        except:
            logging.warning(f"Line {line} could not be split.")
            line = input_file.readline()
            continue
        uri = uri[uri.rfind("/") + 1 :]
        if label not in mention_dict:
            mention_dict[label] = []
        mention_dict[label].append(uri)
        pbar.update(1)
        line = input_file.readline()

    num_mentions_all = {}
    avg_ids_per_mention = 0
    for key, value in mention_dict.items():
        num = len(set(value))
        if num not in num_mentions_all:
            num_mentions_all[num] = 1
        else:
            num_mentions_all[num] += 1
        avg_ids_per_mention += num
    avg_ids_per_mention /= len(mention_dict.keys())

    with open("wikidata_results.json", "w") as f:
        json.dump(
            {"avg_ids_per_mention": avg_ids_per_mention, "details": num_mentions_all}, f
        )

    with open("mention_dict.json", "w") as f:
        json.dump(mention_dict, f)


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--filename", type=str, default="labels.nt")
    args = parser.parse_args()

    gather_ambiguous_mentions(args.filename)
