import logging

from elasticsearch import helpers, Elasticsearch
from tqdm import tqdm

from utilities.tools import split_uri_and_label
from argparse import ArgumentParser


def populate_properties_elasticsearch(bulk_size=1000,filename="predicate_labels.nt"):
    populate_elasticsearch(
        bulk_size, "wikidata_property_index", filename
    )


def populate_entities_elasticsearch(bulk_size=1000, filename="labels.nt"):
    populate_elasticsearch(
        bulk_size, "wikidata_entity_index_english", filename, total=81065185
    )


def populate_descriptions_elasticsearch(bulk_size=1000, filename="description.nt"):
    populate_elasticsearch(
        bulk_size, "wikidata_descriptions_index_english", filename, total=64626844
    )


def populate_elasticsearch(bulk_size, index_name, filename, total=8774):
    es = Elasticsearch()
    es.indices.delete(index=index_name, ignore=404)
    es.indices.create(
        index=index_name,
        ignore=400,
        body={
            "mappings": {
                "properties": {"uri": {"type": "keyword"}, "label": {"type": "text"}}
            }
        },
    )
    bulk = []
    input_file = open(filename)

    line = input_file.readline()
    counter = 0
    pbar = tqdm(total=total)

    while line:
        if counter == bulk_size:
            counter = 0
            # for success, info in helpers.parallel_bulk(es, bulk):
            #    if not success:
            #        print('A document failed:', info)
            helpers.bulk(es, bulk)
            bulk = []
            pbar.update(bulk_size)

        try:
            uri, label = split_uri_and_label(line)
        except:
            logging.warning(f"Line {line} could not be split.")
            line = input_file.readline()
            continue
        document = {"_index": index_name, "_source": {"uri": uri, "label": label}}
        bulk.append(document)

        line = input_file.readline()
        counter += 1
    else:
        if bulk:
            # for success, info in helpers.parallel_bulk(es, bulk):
            #    if not success:
            #        print('A document failed:', info)
            helpers.bulk(es, bulk)

    pbar.close()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--filename", type=str, default="labels.nt")

    args = parser.parse_args()

    populate_entities_elasticsearch(bulk_size=1000, filename=args.filename)

