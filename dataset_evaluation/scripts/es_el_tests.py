import json
from typing import Iterable
from elasticsearch import Elasticsearch, helpers
from tqdm import tqdm

from dataset_evaluation.scripts.dataset_readers import (
    load_mewsli,
    load_tweeki_gold,
    load_hipe,
    load_tweeki_data,
    load_trex_files,
    load_nif_file,
    load_wikidata_disamb,
    load_knowledge_net_file,
    load_kdwd_es,
)
from dataset_evaluation.scripts.paths import datasets_path, results_path

es = Elasticsearch()


def append_search_query(surface_form: str, queries: list, match=True):
    queries.append({"index": "wikidata_entity_index_english"})
    if match:
        queries.append(
            {"query": {"match": {"label": {"query": surface_form,}}}, "size": 100}
        )
    else:
        queries.append({"query": {"match": {"label": surface_form}}, "size": 10000})


def interpret_match_query(elastic_results):
    hits = elastic_results["hits"]["hits"]
    results = []
    for hit in hits:
        results.append((hit["_source"]["uri"], hit["_score"]))

    results = results[:100]
    results = sorted(results, key=lambda x: (int(x[0][x[0].rfind("/") + 2 :]), -x[1]))
    results = results[0:20]
    results = sorted(results, key=lambda x: (-x[1], int(x[0][x[0].rfind("/") + 2 :])))
    return results[0] if len(results) > 0 else ("", "")


def interpret_term_query(elastic_results, surface_form):
    hits = elastic_results["hits"]["hits"]
    results = []
    for hit in hits:
        results.append((hit["_source"]["uri"], hit["_source"]["label"]))

    results = [item[0] for item in results if item[1].lower() == surface_form.lower()]
    return set(results)


def run_and_dump(
    filename: str, label_id_tuples: Iterable, total=None, memory_mode=False,
):
    if memory_mode:
        try:
            content: dict = json.load(open("mention_dict.json"))
        except FileNotFoundError:
            raise RuntimeError(
                "mention_dict.json has to be created first to use memory mode. \n"
                "See calculate_mention_overlap_plus_mention_dictionary.py"
            )
        label_dict = {}
        for key in list(content.keys()):
            value = content[key]
            key_l = key.lower()
            if key_l in label_dict:
                label_dict[key_l].union(set(value))
            else:
                label_dict[key_l] = set(value)
            del content[key]
        del content
        successful = 0
        counter = 0
        exact_matches_true = 0
        unsuccessful = 0
        exact_matches_num = []
        for item in tqdm(label_id_tuples, total=total):
            id: str = str(item[1])
            id = "wd:Q%s" % id
            id = id.replace("wd:", "http://www.wikidata.org/entity/")
            try:
                exact_matches = label_dict.get(item[0].lower(), [])
                exact_matches_num.append(len(exact_matches))
            except Exception as e:
                unsuccessful += 1
                continue

            counter += 1
        accuracy = successful / counter
        accuracy_filtered_v1 = -1
        accuracy_filtered_v2 = -1
    else:
        successful = 0
        successful_v = 0
        exact_matches_true = 0
        counter = 0
        counter_v2 = 0
        unsuccessful = 0
        exact_matches_num = []
        queries = []
        surface_forms = []
        ids = []
        for item in tqdm(label_id_tuples, total=total):
            if len(queries) > 200:
                request = ""
                for each in queries:
                    request += "%s \n" % json.dumps(each)
                resp = es.msearch(body=request)
                for elastic_results, surface_form, id in zip(
                    resp["responses"], surface_forms, ids
                ):
                    result = interpret_match_query(elastic_results)
                    exact_matches = interpret_term_query(elastic_results, surface_form)
                    exact_matches_num.append(len(exact_matches))
                    if result[0] == id:
                        successful += 1
                        if len(exact_matches) != 1:
                            successful_v += 1
                        else:
                            exact_matches_true += 1
                    if len(exact_matches) != 1:
                        counter_v2 += 1
                    counter += 1
                queries, surface_forms, ids = [], [], []

            id: str = str(item[1])
            id = id.replace("http://www.wikidata.org/entity/", "wd:")
            if not id.startswith("wd:"):
                id = "wd:%s" % id
            elif not id.startswith("wd:Q"):
                id = "wd:Q%s" % id
            id = id.replace("wd:", "http://www.wikidata.org/entity/")
            try:
                append_search_query(item[0], queries, False)
                ids.append(id)
                surface_forms.append(item[0])
            except Exception as e:
                unsuccessful += 1
                continue
        if queries:
            request = ""
            for each in queries:
                request += "%s \n" % json.dumps(each)
            resp = es.msearch(body=request)
            for elastic_results, surface_form, id in zip(
                resp["responses"], surface_forms, ids
            ):
                result = interpret_match_query(elastic_results)
                exact_matches = interpret_term_query(elastic_results, surface_form)
                exact_matches_num.append(len(exact_matches))
                if result[0] == id:
                    successful += 1
                    if len(exact_matches) != 1:
                        successful_v += 1
                    else:
                        exact_matches_true += 1
                if len(exact_matches) != 1:
                    counter_v2 += 1
                counter += 1
        accuracy = successful / counter
        accuracy_filtered_v1 = successful_v / counter
        accuracy_filtered_v2 = successful_v / counter_v2
    with open(results_path + "/" + filename, "w") as f:
        json.dump(
            {
                "accuracy": accuracy,
                "accuracy_filtered_v1": accuracy_filtered_v1,
                "accuracy_filtered_v2": accuracy_filtered_v2,
                "counter": counter,
                "successful": successful,
                "unsuccessful": unsuccessful,
                "exact_matches": exact_matches_num,
                "exact_matches_true": exact_matches_true,
                "average_exact_matches": sum(exact_matches_num) / counter,
            },
            f,
            indent=4,
        )


def reduce(data):
    return data[0]


def run_knowledge_net():
    print("Analyze Knowledge Net")
    ids = reduce(
        load_knowledge_net_file("./" + datasets_path + "/Knowledge_Net/train.json")
    )
    run_and_dump("results_es_knowledge_net_train.json", ids)


def run_wikidata_disambig():
    print("Analyze Wikidata-Disamb")

    ids = reduce(
        load_wikidata_disamb("./" + datasets_path + "/Wiki-Disamb30/wikidata-disambig-test.json")
    )
    run_and_dump("results_es_wikidata_test.json", ids)

    ids = reduce(
        load_wikidata_disamb("./" + datasets_path + "/Wiki-Disamb30/wikidata-disambig-dev.json")
    )
    run_and_dump("results_es_wikidata_dev.json", ids)

    ids = reduce(
        load_wikidata_disamb("./" + datasets_path + "/Wiki-Disamb30/wikidata-disambig-train.json")
    )
    run_and_dump("results_es_wikidata_train.json", ids)


def run_istex():
    print("Analyze ISTEX")
    ids = reduce(load_nif_file("./" + datasets_path + "/ISTEX-1000/istex_train.ttl"))

    run_and_dump("results_es_istex_train.json", ids)

    ids = reduce(load_nif_file("./" + datasets_path + "/ISTEX-1000/istex_test.ttl"))

    run_and_dump("results_es_istex_test.json", ids)


def run_kore50():
    print("Analyze KORE50")
    ids = reduce(
        load_nif_file("./" + datasets_path + "/KORE50DYWC/KORE_50_Wikidata.ttl")
    )

    run_and_dump("results_es_kore50_new.json", ids)


def run_trex():
    print("Analyze TREx")
    ids = reduce(load_trex_files("./" + datasets_path + "/TREx"))

    run_and_dump("results_es_trex.json", ids, memory_mode=True)


def run_kdwd():
    print("Analyze KDWD")
    ids = load_kdwd_es()

    run_and_dump("results_es_kdwd.json", ids, 121835453, True)


def run_hipe():
    print("Analyze HIPE")
    ids = reduce(load_hipe("./" + datasets_path + "/CLEF_HIPE_2020/HIPE-data-v1.2-dev-en.tsv"))
    run_and_dump("results_es_hipe_dev.json", ids)
    ids = reduce(load_hipe("./" + datasets_path + "/CLEF_HIPE_2020/HIPE-data-v1.3-test-en.tsv"))
    run_and_dump("results_es_hipe_test.json", ids)


def run_tweeki_gold():
    print("Analyze tweeki gold")
    ids = reduce(load_tweeki_gold())
    run_and_dump("results_es_tweeki_gold.json", ids)


def run_tweeki_data():
    print("Analyze tweeki data")
    ids = reduce(load_tweeki_data())
    run_and_dump("results_es_tweeki_data.json", ids, memory_mode=True)


def run_mewsli():
    print("Analyze mewsli")
    ids = reduce(load_mewsli())
    run_and_dump("results_es_mewsli.json", ids)


if __name__ == "__main__":
    run_tweeki_gold()
    run_hipe()
    run_kore50()
    run_knowledge_net()
    run_istex()
    run_mewsli()
    run_tweeki_data()
    run_trex()
    run_kdwd()
