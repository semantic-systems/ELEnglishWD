from functools import partial

from numpy import mean
from scipy.stats import scoreatpercentile

from tqdm import tqdm

from utilities.sparql_handler import SparqlHandler
from utilities.tools import n_wise


def single_extract(items, sh):
    counter = 0
    number_of_qualifiers = 0

    count_dict = {0: 0}

    items_string = " ".join(items)

    response = sh.send_query(
        """
                    SELECT (count(?q) as ?c) WHERE {
                        values ?sub {"""
        + items_string
        + """}
                        ?sub  ?p   ?s  .  # ?s is the the statement node
                               ?s  rdf:type  wikibase:BestRank .  # that simulates the predicate 
                               ?s  ?q ?o.
                      filter strstarts(str(?q),str(pq:))
                      filter (!strstarts(str(?q),str(pqv:)))
                     }
                    group by ?s ?c
                """
    )
    for item in response["results"]["bindings"]:
        counted_qualifiers = int(item["c"]["value"])
        if counted_qualifiers not in count_dict:
            count_dict[counted_qualifiers] = 0
        count_dict[counted_qualifiers] += 1
        number_of_qualifiers += counted_qualifiers
        counter += 1

    response = sh.send_query(
        """
                        SELECT (count(distinct ?p) as ?c) WHERE {
                            values ?sub {"""
        + items_string
        + """}
                            ?sub  ?p   ?s  .  # ?s is the the statement node

                          FILTER NOT EXISTS { ?s  ?q ?o. }
                         }
                    """
    )
    statements_without_qualifier = int(response["results"]["bindings"][0]["c"]["value"])
    counter += statements_without_qualifier
    count_dict[0] += statements_without_qualifier

    return number_of_qualifiers, count_dict, counter


def process(ids, extractor):
    ids = list(ids)
    for idx in range(len(ids)):
        ids[idx] = "wd:Q" + str(idx)
    nwise_items = n_wise(ids, 200)

    sh = SparqlHandler("https://query.wikidata.org/sparql")

    extractor = partial(extractor, sh=sh)
    return map(extractor, tqdm(nwise_items))


def extract_entities_stats(ids, num_docs, emerging_entities):
    if isinstance(emerging_entities, tuple):
        mentions = len(ids) + sum(emerging_entities)
        emerging_count = emerging_entities[0]
        unmappable_count = emerging_entities[1]
    else:
        emerging_count = emerging_entities
        unmappable_count = 0
        mentions = len(ids) + emerging_entities
    return {
        "num_entities": len(ids),
        "mentions": mentions,
        "mentions_ratio": mentions / num_docs,
        "num_unique_entities": len(set(ids)),
        "emerging_entities": emerging_entities,
        "num_docs": num_docs,
        "ratio": len(ids) / num_docs,
        "percentage_entities": len(ids) / mentions,
        "percentage_emerging_entities": emerging_count / mentions,
        "percentage_non_mappable": unmappable_count / mentions,
        "percentage_unique": len(set(ids)) / mentions,
        "extractor": "entities",
    }


def extract_number_qualifiers(ids):
    results = process(ids, single_extract)
    number_of_qualifiers = 0
    count_dict = {}
    counter = 0
    for result in results:
        number_of_qualifiers += result[0]
        counter += result[2]
        for key, value in result[1].items():
            if key not in count_dict:
                count_dict[key] = 0
            count_dict[key] += value

    return {
        "average": number_of_qualifiers / counter if counter != 0 else 0,
        "total_num_qualifiers": number_of_qualifiers,
        "total_statements": counter,
        "count_dict": count_dict,
        "extractor": "qualifiers",
    }


def single_extract_descriptions(items, sh):
    items_string = " ".join(items)
    response = sh.send_query(
        """
                        select * where
                            {
                            values ?s {"""
        + items_string
        + """}
                            ?s schema:description ?d.
                            FILTER(lang(?d) = 'en')
                            }

                    """
    )

    have_description = set()
    for item in response["results"]["bindings"]:
        have_description.add(item["s"]["value"])

    return len(have_description), len(items)


def extract_number_descriptions(ids):
    results = process(ids, single_extract_descriptions)

    counter_descriptions = 0
    counter = 0
    for result in results:
        counter_descriptions += result[0]
        counter += result[1]

    return {
        "total_items": counter,
        "counter_descriptions": counter_descriptions,
        "extractor": "descriptions",
    }


def single_extract_aliases_labels(items, sh):
    items_string = " ".join(items)
    response = sh.send_query(
        """
    
                        select * where
                            {
                              values ?s {"""
        + items_string
        + """}
                              values ?p {rdfs:label skos:altLabel}
                              ?s ?p ?l.
                                 
                              FILTER(lang(?l) = 'en')
                            }
                    """
    )

    len_aliases = {}
    len_labels = []
    for item in response["results"]["bindings"]:
        entity = item["s"]["value"]
        if entity not in len_aliases:
            len_aliases[entity] = []
        label_alias = item["l"]["value"]
        is_label = item["p"]["value"] == "http://www.w3.org/2000/01/rdf-schema#label"
        if not is_label:
            len_aliases[entity].append(len(label_alias))
        else:
            len_labels.append(len(label_alias))
    len_aliases = list(len_aliases.values())
    return len_labels, len_aliases


def extract_aliases_labels(ids):
    results = process(ids, single_extract_aliases_labels)

    len_aliases = []
    len_labels = []
    for result in results:
        len_labels += result[0]
        len_aliases += result[1]

    number_aliases = [len(item) for item in len_aliases]
    all_len_aliases = [len_ for lens in len_aliases for len_ in lens]

    percentiles = list(range(101))
    return {
        "average_number_aliases": mean(number_aliases),
        "average_length_labels": mean(len_labels),
        "average_length_aliases": mean(all_len_aliases),
        "average_length_aliases_labels": mean(all_len_aliases + len_labels),
        "average_length_aliases_per_entity": mean(
            [mean(lens) if len(lens) > 0 else 0 for lens in len_aliases]
        ),
        "percentiles_label_lengths": list(scoreatpercentile(len_labels, percentiles)),
        "percentiles_number_aliases": list(
            scoreatpercentile(number_aliases, percentiles)
        ),
        "percentiles_len_aliases": list(
            scoreatpercentile(all_len_aliases, percentiles)
        ),
        "percentiles_len_aliases_labels": list(
            scoreatpercentile(all_len_aliases + len_labels, percentiles)
        ),
        "extractor": "labels",
    }
