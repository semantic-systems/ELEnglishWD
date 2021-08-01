import gzip
import json
import shlex
from pathlib import Path

import tqdm


# reads through all lines of an (compressed) n-triples file and gathers the surface forms in a dictionary with
# the number of entities in the values (assumption that an entity does not have two equal labels)
def compute_mention_overlap(
    filename: str, output_file_name=None, lang=None, filtered_relations=None
):
    if not output_file_name or (
        output_file_name and not Path(output_file_name).exists()
    ):
        mention_dictionary = {}
        tqdm_ = tqdm.tqdm(total=15290824)
        if filename.endswith("gz"):
            f = gzip.open(filename, "rt")
        else:
            f = open(filename)

        line = f.readline()
        identifiers = set()
        while line:
            line = line.replace("'", "\\'")
            split_line = shlex.split(line)
            tqdm_.update(1)
            relation = split_line[1]
            label: str = split_line[2]
            if lang and not label.endswith("@" + lang):
                line = f.readline()
                continue
            label = label[0: label.rfind("@")]
            if relation in filtered_relations:
                identifiers.add(split_line[0])
                if label not in mention_dictionary:
                    mention_dictionary[label] = 0
                mention_dictionary[label] += 1
            line = f.readline()
        with open(output_file_name, "w") as f:
            json.dump(mention_dictionary, f, indent=4)
    else:
        with open(output_file_name) as f:
            mention_dictionary = json.load(f)
        identifiers = None
    return mention_dictionary, identifiers


def calculate_overlap(mention_dictionary: dict, identifiers=None):
    if not identifiers:
        identifiers = []

    number_of_entities = {}
    for key, value in mention_dictionary.items():
        if value not in number_of_entities:
            number_of_entities[value] = 0
        number_of_entities[value] += int(key)
    three_ten = 0
    for i in range(3, 11):
        three_ten += number_of_entities.get(i, 0)
    eleven_hundred = 0
    for i in range(11, 101):
        if i in number_of_entities:
            eleven_hundred += number_of_entities.get(i,0)
    rest = 0
    for key, value in number_of_entities.items():
        if key > 100:
            rest += value

    results = {
        "num_identifiers": len(identifiers),
        "exact_match": number_of_entities.get(1,0),
        "two_match": number_of_entities.get(2,0),
        "three-ten": three_ten,
        "eleven_hundred": eleven_hundred,
        "rest": rest,
        "details": number_of_entities,
    }
    return results


if __name__ == "__main__":

    filtered_relations = ["<http://www.w3.org/2000/01/rdf-schema#label>",
                          "<http://www.w3.org/2004/02/skos/core#altLabel>",
                          "<http://schema.org/alternateName>"]

    # Has to be replaced with the different KG dumps
    filename = "../DBpedia/labels_lang=en.ttl"

    mention_dictionary, identifiers = compute_mention_overlap(
        filename,
        output_file_name="dbpedia.json",
        lang="en",
        filtered_relations=filtered_relations,
    )
    results = calculate_overlap(mention_dictionary, identifiers)

    with open("../results/dbedia_results.json", "w") as f:
        json.dump(results, f, indent=4)
