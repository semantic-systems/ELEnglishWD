import logging

from elasticsearch import helpers, Elasticsearch
from tqdm import tqdm

from utilities.tools import split_uri_and_label


def populate_properties_elasticsearch(bulk_size=1000):
    populate_elasticsearch(
        bulk_size, "wikidata_property_index", "predicate_labels.nt"
    )


def populate_entities_elasticsearch(bulk_size=1000):
    populate_elasticsearch(
        bulk_size, "wikidata_entity_index_english", "labels.nt", total=81065185
    )


def populate_descriptions_elasticsearch(bulk_size=1000):
    populate_elasticsearch(
        bulk_size, "wikidata_descriptions_index_english", "description.nt", total=64626844
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
