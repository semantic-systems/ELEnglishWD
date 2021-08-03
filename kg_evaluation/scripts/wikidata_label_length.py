import json
import statistics
import scipy.stats as stats
from tqdm import tqdm

from argparse import ArgumentParser


def evaluate_dump(length_list: list, filename):
    avg = statistics.mean(length_list)
    median = statistics.median(length_list)
    percentiles = stats.scoreatpercentile(length_list, list(range(0, 101, 1)))
    with open(filename + ".json", "w") as f:
        json.dump(
            {
                "avg": avg,
                "overall": len(length_list),
                "median": median,
                "percentiles": percentiles.tolist(),
            },
            f,
            indent=4,
        )

    with open(filename + "_raw.json", "w") as f:
        json.dump(length_list, f, indent=4)


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("mention_dict_file", type=str)

    args = parser.parse_args()
    mention_dict: dict = json.load(open(args.mention_dict_file))

    lengths = []
    lengths_per_entity = []
    for mention, entities in tqdm(mention_dict.items()):
        length = len(mention)
        lengths.append(length)
        lengths_per_entity += len(set(entities)) * [length]

    evaluate_dump(lengths, "wikidata_label_lengths")
    evaluate_dump(lengths_per_entity, "wikidata_label_lengths_per_entity")
