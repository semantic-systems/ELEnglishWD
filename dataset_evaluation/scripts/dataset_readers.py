import csv
import json
import math
import re
import sys
from pathlib import Path

import jsonlines
import pynif
from tqdm import tqdm

from dataset_evaluation.scripts.paths import datasets_path


def load_mewsli():
    docs = []
    with open(datasets_path + "/mewsli-9/output/dataset/en/docs.tsv") as f:
        docs_reader = csv.reader(f, delimiter="\t", quotechar='"')
        docs_reader.__next__()
        for line in docs_reader:
            docs.append(line)

    mentions = []
    with open(datasets_path + "/mewsli-9/output/dataset/en/mentions.tsv") as f:
        docs_reader = csv.reader(f, delimiter="\t", quotechar='"')
        docs_reader.__next__()
        for line in docs_reader:
            mentions.append(line)

    path = Path(datasets_path + "/mewsli-9/output/dataset/en/text")
    txt_files = path.glob("en*")
    texts = {}
    for file in txt_files:
        name = file.stem
        texts[name] = "".join(file.open().readlines())

    ids = []
    for mention in mentions:
        ids.append([mention[3], mention[6]])
    return ids, (len(texts), 0)


def load_tweeki_gold():
    data = []
    with open(datasets_path + "/TweekiGold/Tweeki_gold.jsonl") as f:
        for line in f.readlines():
            data.append(json.loads(line))
    ids = []
    pattern = re.compile("Q[0-9]+")
    emerging = 0
    for item in data:
        for span, identifier in zip(item["index"], item["link"]):
            surface_form = item["sentence"][span[0] : span[1]]
            qid = identifier.split("|")
            if len(qid) == 2 and pattern.match(qid[1]):
                ids.append((surface_form, "wd:" + qid[1]))
            else:
                emerging += 1
        # emerging += len(item["index"]) - len(item["link"])
    return ids, (len(data), emerging)


def load_tweeki_data():
    path = Path(datasets_path + "/TweekiData")
    csv_files = path.glob("*.csv")
    num_documents = 0
    num_emerging = 0
    ids = []
    pattern = re.compile("Q[0-9]+")
    for file in tqdm(csv_files, total=9):
        csv_reader = csv.reader(file.open(), delimiter=",", quotechar='"')
        csv_reader.__next__()
        for line in csv_reader:
            tokens = eval(line[1])
            identifiers = eval(line[-1])
            types = eval(line[2])
            types_together = eval(line[3])
            tokens_together = eval(line[4])
            for identifier, tokens_together_, types_together_ in zip(
                identifiers, tokens_together, types_together
            ):
                if identifier == 0 and types_together_:
                    num_emerging += 1
                elif identifier != 0 and types_together_:
                    identifier = identifier.split("|")[1]
                    if not pattern.match(identifier):
                        raise RuntimeError()
                    ids.append((" ".join(tokens_together_), "wd:" + identifier))
            num_documents += 1
    return ids, (num_documents, num_emerging)


def load_hipe(filename: str):
    csv.field_size_limit(sys.maxsize)
    fp = open(filename)
    csv_reader = csv.DictReader(filter(lambda row: row[0] != "#", fp), delimiter="\t")
    current_identifier = ""
    current_surface_form = ""
    ids = []
    for line in csv_reader:
        if line["NEL-LIT"] != "_":
            if line["NEL-LIT"] != current_identifier:
                if current_identifier:
                    ids.append((current_surface_form.rstrip(), current_identifier))
                current_identifier = line["NEL-LIT"]
                current_surface_form = ""
            current_surface_form += line["TOKEN"] + " "
        else:
            if current_identifier:
                ids.append((current_surface_form.rstrip(), current_identifier))
                current_identifier = ""
                current_surface_form = ""
    if current_identifier:
        ids.append((current_surface_form.rstrip(), current_identifier))

    fp2 = open(filename)
    file = filter(lambda row: row[0] == "#", fp2)

    doc_set = set()
    for item in file:
        if "document_id" in item:
            doc_set.add(item)
    num_docs = len(doc_set)

    unfiltered_length = len(ids)
    ids = [item for item in ids if item[1] != "NIL"]
    return ids, (num_docs, unfiltered_length - len(ids))


def load_trex_files(folder):
    num_docs = math.nan
    entities_path = Path("trex_entities.json")
    if not entities_path.exists():
        num_docs = 0
        path = Path(folder)

        json_files = path.glob("*.json")
        ids = []
        for file in tqdm(json_files, total=465):
            data = json.load(file.open())
            for item in data:
                entities = [
                    (entity["surfaceform"], entity["uri"])
                    for entity in item["entities"]
                    if entity["annotator"] == "Wikidata_Spotlight_Entity_Linker"
                ]
                entities.append((item['title'], item["docid"]))
                entities = [(entity[0], entity[1][entity[1].rfind("/") + 1 :]) for entity in entities]
                ids += entities
            num_docs += len(data)

        for idx, item in enumerate(ids):
            ids[idx] = "wd:" + item

        with entities_path.open("w") as f:
            json.dump(ids, f)
    else:
        ids = json.load(entities_path.open())

    pattern = re.compile("wd:Q[0-9]+")
    before_filtering = len(ids)
    wrong_ids = set([id_ for id_ in ids if not pattern.match(id_[1])])
    wrong_ids = set([id_ for id_ in wrong_ids if not id_[1].startswith("wd:P")])
    ids = [id_ for id_ in ids if pattern.match(id_[1])]
    return ids, (num_docs, before_filtering - len(ids))


def load_kdwd():
    wikidata_mappings = {}
    information = Path("./datasets/kensho/information.json")
    if not information.exists():
        file = open("./datasets/kensho/page.csv")
        csv_reader = csv.reader(file, delimiter=",")
        csv_reader.__iter__().__next__()
        for line in csv_reader:
            wikidata_mappings[line[0]] = line[1]

        json_reader = jsonlines.Reader(
            open("./datasets/kensho/link_annotated_text.jsonl")
        )
        element = json_reader.read()
        print("Start id generation")
        num_docs = 0
        ids = []
        not_found = 0
        while element:
            num_docs += len(element["sections"])
            for item in element["sections"]:
                for page_id, offset, link_length in zip(
                    item["target_page_ids"], item["link_offsets"], item["link_lengths"]
                ):
                    mention = item["text"][offset : offset + link_length]
                    if str(page_id) in wikidata_mappings:
                        ids.append(wikidata_mappings[str(page_id)])
                    else:
                        not_found += 1
                        print("ID not found ")
            try:
                element = json_reader.read()
            except EOFError:
                element = None

        json.dump(
            {"ids": ids, "num_docs": num_docs, "not_found": not_found},
            information.open("w"),
        )
    else:
        content = json.load(information.open())
        ids = content["ids"]
        num_docs = content["num_docs"]
        not_found = content["not_found"]
    return ids, (num_docs, (0, not_found))


def load_kdwd_es():
    wikidata_mappings = {}
    ids_mentions_file = Path("./datasets/kensho/ids_mentions.csv")
    if not ids_mentions_file.exists():
        file = open("./datasets/kensho/page.csv")
        csv_reader = csv.reader(file, delimiter=",")
        csv_reader.__iter__().__next__()
        for line in csv_reader:
            wikidata_mappings[line[0]] = line[1]

        csv_writer = csv.writer(ids_mentions_file.open("w"), delimiter=",")
        json_reader = jsonlines.Reader(
            open("./datasets/kensho/link_annotated_text.jsonl")
        )
        element = json_reader.read()
        print("Start id generation")
        num_docs = 0

        while element:
            num_docs += len(element["sections"])
            for item in element["sections"]:
                for page_id, offset, link_length in zip(
                    item["target_page_ids"], item["link_offsets"], item["link_lengths"]
                ):
                    mention = item["text"][offset : offset + link_length]
                    if str(page_id) in wikidata_mappings:
                        csv_writer.writerow([mention, wikidata_mappings[str(page_id)]])
                    else:
                        print("ID not found ")
            try:
                element = json_reader.read()
            except EOFError:
                element = None

    ids = []
    csv_reader = csv.reader(ids_mentions_file.open(), delimiter=",")
    return csv_reader


def load_nif_file(filename):
    try:
        data = pynif.NIFCollection.load(filename)
    except:
        with open(filename, "r", encoding="iso-8859-1") as f:
            data = pynif.NIFCollection.loads(f.read(), format="turtle")

    ids = []

    emerging_entities = 0
    pattern = re.compile("Q[0-9]+")
    for context in data.contexts:
        for phrase in context.phrases:
            id = phrase.taIdentRef
            id = id[id.rfind("/") + 1 :]
            if pattern.match(id):
                id = "wd:" + id
                ids.append((phrase.mention, id))
            else:
                emerging_entities += 1

    return ids, (len(data.contexts), emerging_entities)


def load_knowledge_net_file(filename):
    pattern = re.compile(".*Q[0-9]+")

    with open(filename) as f:
        data = f.readlines()

    ids = []
    for line in data:
        parsed_line = eval(line)
        for passage in parsed_line["passages"]:
            for fact in passage["facts"]:
                if pattern.match(fact["subjectUri"]):
                    ids.append((fact["subjectText"], fact["subjectUri"]))
                if pattern.match(fact["objectUri"]):
                    ids.append((fact["objectText"], fact["objectUri"]))

    return ids, (len(data), 0)


def load_lcquad_file(filename):
    with open(filename) as f:
        data = json.load(f)

    ids = []

    pattern = re.compile("wd:Q[0-9]+")

    for item in data:
        query = item["sparql_wikidata"]
        found = pattern.findall(query)
        ids += found

    return ids


def load_lcquad20(filename):

    re_rule = re.compile("wd:Q[0-9]+")
    with open(filename) as f:
        content = json.load(f)
    ids = []
    for item in content:
        ids += re_rule.findall(item["sparql_wikidata"])
    return ids, (len(content), 0)


def load_wikidata_disamb(filename):

    with open(filename) as f:
        data = json.load(f)

    ids = []

    for item in data:
        ids.append((item["string"], "wd:" + item["correct_id"]))

    return ids, (len(data), 0)


