from tqdm import tqdm
from argparse import ArgumentParser
import gzip
import shlex

# Both methods are used together with a compressed (gz) n-triples Wikidata dump


def filter_labels_no_loading(
    filepath: str, output_file: str = "predicate_labels.nt", total=1190348725
):
    input_file = gzip.open(filepath)
    output_file = open(output_file, "w")

    line = input_file.readline()
    pbar = tqdm(total=total)

    while line:
        pbar.update(1)
        split_line = shlex.split(line)

        if not len(split_line) >= 4 or not split_line[0].startswith("http://www.wikidata.org/entity/P"):
            continue

        if (
            "http://www.w3.org/2004/02/skos/core#altLabel" in line
            or "http://www.w3.org/2000/01/rdf-schema#label" in line
        ):
            if (
                "http://www.w3.org/2004/02/skos/core#altLabel" not in split_line[0]
                and "http://www.w3.org/2000/01/rdf-schema#label" not in split_line[0]
            ):
                output_file.write(line)
        line = input_file.readline()
    pbar.close()


def filter_labels_and_descriptions_no_loading(
    filepath: str,
    output_file_labels: str = "labels.nt",
    output_file_descriptions="description.nt",
    total=1325821109,
):
    input_file = gzip.open(filepath)
    output_labels_file = open(output_file_labels, "w")
    output_descriptions_file = open(output_file_descriptions, "w")

    line = input_file.readline()
    pbar = tqdm(total=total)

    while line:
        pbar.update(1)
        split_line = shlex.split(line)

        if not len(split_line) >= 4 or not split_line[0].startswith("http://www.wikidata.org/entity/Q"):
            continue

        if (
            "http://www.w3.org/2004/02/skos/core#altLabel" in line
            or "http://www.w3.org/2000/01/rdf-schema#label" in line
        ):
            if (
                "http://www.w3.org/2004/02/skos/core#altLabel" not in split_line[0]
                and "http://www.w3.org/2000/01/rdf-schema#label" not in split_line[0]
            ):
                output_labels_file.write(line)
        if "http://schema.org/description" in line:
            if "http://schema.org/description" not in split_line[0]:
                output_descriptions_file.write(line)
        line = input_file.readline()
    pbar.close()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    args = parser.parse_args()

    filter_labels_and_descriptions_no_loading(args.filename)
