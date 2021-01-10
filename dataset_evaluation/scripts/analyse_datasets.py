import json
import math
from pathlib import Path

from dataset_evaluation.scripts.dataset_readers import (
    load_mewsli,
    load_tweeki_data,
    load_tweeki_gold,
    load_hipe,
    load_kdwd,
    load_lcquad20,
    load_nif_file,
    load_trex_files,
    load_lcquad_file,
    load_wikidata_disamb,
    load_knowledge_net_file,
)
from dataset_evaluation.scripts.paths import datasets_path, results_path
from dataset_evaluation.scripts.wikidata_extractors import (
    extract_number_descriptions,
    extract_entities_stats,
    extract_aliases_labels,
)


def reduce(data):
    return [item[1] for item in data[0]], data[1]


def update(results, new_results):
    if "extractor" in new_results:
        if "extractors" not in results:
            results["extractors"] = []
        results["extractors"] = list(
            set(results["extractors"] + [new_results["extractor"]])
        )
        del new_results["extractor"]
    results.update(new_results)


def dump(filename, ids, additional_info=None):
    if not additional_info:
        additional_info = (math.nan, math.nan)
    num_docs, emerging_entities = additional_info
    path = Path(results_path + "/" + filename)
    if path.exists():
        results = json.load(path.open())
    else:
        results = {}

    if "extractors" in results:
        # if "qualifiers" not in results["extractors"]:
        #     update(results, extract_number_qualifiers(set(ids)))
        if "descriptions" not in results["extractors"]:
            update(results, extract_number_descriptions(set(ids)))
        if "labels" not in results["extractors"]:
            update(results, extract_aliases_labels(set(ids)))
        if "entities" not in results["extractors"]:
            update(results, extract_entities_stats(ids, num_docs, emerging_entities))

    else:
        # update(results, extract_number_qualifiers(set(ids)))
        update(results, extract_number_descriptions(set(ids)))
        update(results, extract_aliases_labels(set(ids)))
        update(results, extract_entities_stats(ids, num_docs, emerging_entities))

    json.dump(results, path.open("w"), indent=4)


def analyze_knowledge_net():
    print("Analyze Knowledge Net")
    ids, num_docs = reduce(
        load_knowledge_net_file("./" + datasets_path + "/Knowledge Net/train.json")
    )
    dump("results_knowledge_net_train.json", ids, num_docs)

    # ids, num_docs = load_knowledge_net_file('./"+datasets_path+"/Knowledge Net/test-no-facts.json')
    # dump('results_knowledge_net_test.json', ids, num_docs)


def analyze_wikidata_disambig():
    print("Analyze Wikidata-Disamb")
    ids, num_docs = reduce(
        load_wikidata_disamb("./" + datasets_path + "/wikidata-disambig-train.json")
    )
    dump("results_wikidata_train.json", ids, num_docs)

    ids, num_docs = reduce(
        load_wikidata_disamb("./" + datasets_path + "/wikidata-disambig-test.json")
    )
    dump("results_wikidata_test.json", ids, num_docs)

    ids, num_docs = reduce(
        load_wikidata_disamb("./" + datasets_path + "/wikidata-disambig-dev.json")
    )
    dump("results_wikidata_dev.json", ids, num_docs)


def analyze_istex():
    print("Analyze ISTEX")
    ids, num_docs = reduce(load_nif_file("./" + datasets_path + "/istex_train.ttl"))

    dump("results_istex_train.json", ids, num_docs)

    ids, num_docs = reduce(load_nif_file("./" + datasets_path + "/istex_test.ttl"))

    dump("results_istex_test.json", ids, num_docs)


def analyze_trex():
    print("Analyze TREx")
    ids, num_docs = reduce(load_trex_files("./" + datasets_path + "/TREx"))

    dump("results_trex.json", ids, num_docs)


def analyze_kore50():
    print("Analyze Kore50")
    ids, num_docs = reduce(
        load_nif_file("./" + datasets_path + "/kore50-lrec2020/KORE_50_Wikidata.ttl")
    )

    dump("results_kore50.json", ids, num_docs)


def analyze_lcquad20():
    print("Analyze LCQUAD20")
    ids, num_docs = load_lcquad20("./" + datasets_path + "/LCQUAD2.0/lcquad_2_0.json")

    dump("results_lcquad2.0.json", ids, num_docs)


def analyze_lcquad20_both_files():
    print("Analyze LCQUAD")
    ids, num_docs = load_lcquad_file("./" + datasets_path + "/LCQUAD2.0/train.json")
    dump("results_lcquad_train.json", ids)

    ids, num_docs = load_lcquad_file("./" + datasets_path + "/LCQUAD2.0/test.json")
    dump("results_lcquad_test.json", ids)


def analyze_kdwd():
    print("Analyze KDWD")
    ids, num_docs = reduce(load_kdwd())
    dump("results_kdwd.json", ids, num_docs)


def analyze_hipe():
    print("Analyze HIPE")
    ids, num_docs = reduce(
        load_hipe("./" + datasets_path + "/hipe/HIPE-data-v1.2-dev-en.tsv")
    )
    dump("results_hipe_dev.json", ids, num_docs)

    ids, num_docs = reduce(
        load_hipe("./" + datasets_path + "/hipe/HIPE-data-v1.3-test-en.tsv")
    )
    ids = [item[1] for item in ids]
    dump("results_hipe_test.json", ids, num_docs)


def analyze_tweeki_gold():
    print("Analyze tweeki_gold")

    ids, num_docs = reduce(load_tweeki_gold())
    dump("results_tweeki_gold.json", ids, num_docs)


def analyze_tweeki_data():
    print("Analyze tweeki_data")

    ids, num_docs = reduce(load_tweeki_data())
    dump("results_tweeki_data.json", ids, num_docs)


def analyze_mewsli():
    print("Analyze mewsli")

    ids, num_docs = reduce(load_mewsli())
    dump("results_mewsli.json", ids, num_docs)


analyze_hipe()
analyze_lcquad20()
analyze_istex()
analyze_kore50()
analyze_knowledge_net()
analyze_wikidata_disambig()
analyze_trex()
analyze_tweeki_data()
analyze_mewsli()
analyze_tweeki_gold()
