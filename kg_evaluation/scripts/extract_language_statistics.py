import argparse
import bz2
import gzip
import json
import sys


class WikidataItemDocument(object):
    def __init__(self, json):
        self.json = json

    def get(self, field, default_value=None):
        return self.json.get(field, default_value)

    def __repr__(self):
        return "<WikidataItemDocument {}>".format(
            self.json.get("id") or "(unknown qid)"
        )

    def __iter__(self):
        return self.json.__iter__()

    def get_outgoing_edges(self, include_p31=True, numeric=True):
        """
        Given a JSON representation of an item,
        return the list of outgoing edges,
        as integers.
        """
        claims = self.get("claims", {})
        final_key = "numeric-id" if numeric else "id"
        res = []
        for pid, pclaims in claims.items():
            if pid == "P31" and not include_p31:
                continue
            for c in pclaims:
                try:
                    res.append(c["mainsnak"]["datavalue"]["value"][final_key])
                except (KeyError, TypeError):
                    pass

                qualifiers = c.get("qualifiers", {})
                for pid, qs in qualifiers.items():
                    for q in qs:
                        try:
                            res.append(q["datavalue"]["value"][final_key])
                        except (KeyError, TypeError):
                            pass
        return res

    def get_nb_statements(self):
        """
        Number of claims on the item
        """
        nb_claims = 0
        for pclaims in self.get("claims", {}).values():
            nb_claims += len(pclaims)
        return nb_claims

    def get_nb_sitelinks(self):
        """
        Number of sitelinks on this item
        """
        return len(self.get("sitelinks", []))

    def get_types(self, pid="P31"):
        """
        Values of P31 claims
        """
        type_claims = self.get("claims", {}).get(pid, [])
        type_qids = [
            claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
            for claim in type_claims
        ]
        valid_type_qids = [qid for qid in type_qids if qid]
        return valid_type_qids

    def get_default_label(self, language):
        """
        English label if provided, otherwise any other label
        """
        labels = self.get("labels", {})
        preferred_label = labels.get(language, {}).get("value")
        if preferred_label:
            return preferred_label
        enlabel = labels.get("en", {}).get("value")
        if enlabel:
            return enlabel
        for other_lang in labels:
            return labels.get(other_lang, {}).get("value")
        return None

    def get_all_terms(self):
        """
        All labels and aliases in all languages, made unique
        """
        all_labels = {label["value"] for label in self.get("labels", {}).values()}
        for aliases in self.get("aliases", {}).values():
            all_labels |= {alias["value"] for alias in aliases}
        return all_labels

    def get_aliases(self, lang):
        aliases = [alias["value"] for alias in self.get("aliases", {}).get(lang, [])]
        return aliases

    def get_identifiers(self, pid):
        # Fetch GRID
        id_claims = self.get("claims", {}).get(pid, [])
        ids = [
            claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            for claim in id_claims
        ]
        valid_ids = [id for id in ids if id]
        return valid_ids


class WikidataDumpReader(object):
    """
    Generates a stream of `WikidataItemDocument` from
    a Wikidata dump.
    """

    def __init__(self, fname: str):
        self.fname = fname
        if fname == "-":
            self.f = sys.stdin
        elif fname.endswith("bz2"):
            self.f = bz2.open(fname, mode="rt", encoding="utf-8")
        else:
            self.f = gzip.open(fname, "rt")

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        if self.fname != "-":
            self.f.close()

    def __iter__(self):
        for line in self.f:
            try:
                # remove the trailing comma
                if line.rstrip().endswith(","):
                    line = line[:-2]
                item = json.loads(line)
                yield WikidataItemDocument(item)
            except ValueError as e:
                # Happens at the beginning or end of dumps with '[', ']'
                continue


def to_triple_object(subject, predicate, object):
    return f"<{subject}> <{predicate}> <{object}> .\n"


def to_triple_literal(subject, predicate, literal, lang):
    return f'<{subject}> <{predicate}> "{literal}"@{lang} .\n'


def fill_data(data, item):
    data["counter"] += 1

    labels: dict = item.get("labels", {})
    temp_languages = set()
    all_labels = []
    labels_overall = 0
    tmp_labels_found = {}
    for key, value in labels.items():
        if key not in data["languages_labels"]:
            data["languages_labels"][key] = 0
        if value:
            temp_languages.add(key)
            data["languages_labels"][key] += 1
            labels_overall += 1
            all_labels.append(value["value"])
            tmp_labels_found[key] = 1

    aliases = item.get("aliases", {})
    for key, value in aliases.items():
        if key not in data["languages_aliases"]:
            data["languages_aliases"][key] = 0
        if value:
            temp_languages.add(key)
            num_aliases = len(value)
            data["languages_aliases"][key] += num_aliases
            labels_overall += num_aliases
            all_labels += [value_["value"] for value_ in value]
            if key not in tmp_labels_found:
                tmp_labels_found[key] = num_aliases
            else:
                tmp_labels_found[key] += num_aliases

    for key, value in tmp_labels_found.items():
        if key not in data["labels_per_entity_per_language"]:
            data["labels_per_entity_per_language"][key] = {}
        if value not in data["labels_per_entity_per_language"][key]:
            data["labels_per_entity_per_language"][key][value] = 0
        data["labels_per_entity_per_language"][key][value] += 1

    if labels_overall not in data["labels_per_entity"]:
        data["labels_per_entity"][labels_overall] = 0
    data["labels_per_entity"][labels_overall] += 1
    if len(temp_languages) not in data["languages_per_entity_labels"]:
        data["languages_per_entity_labels"][len(temp_languages)] = 0
    data["languages_per_entity_labels"][len(temp_languages)] += 1

    for language in temp_languages:
        if language not in data["languages_any_sf"]:
            data["languages_any_sf"][language] = 0
        data["languages_any_sf"][language] += 1

    claims: dict = item.get("claims", None)
    if claims:
        for value in claims.values():
            for claim in value:
                qualifiers = claim.get("qualifiers", {})
                qualifiers_len = sum([len(content) for content in qualifiers.values()])
                if qualifiers_len not in data["claims_counter"]:
                    data["claims_counter"][qualifiers_len] = 0
                data["claims_counter"][qualifiers_len] += 1

    data["overlap"]["average_number"] += len(all_labels) - len(set(all_labels))
    data["overlap"]["average_percentage"] += (
        len(set(all_labels)) / len(all_labels) if all_labels else 1
    )

    descriptions = item.get("descriptions", {})
    for key, value in descriptions.items():
        if key not in data["descriptions_per_language"]:
            data["descriptions_per_language"][key] = 0
        if value:
            data["descriptions_per_language"][key] += 1

    if len(descriptions) not in data["descriptions_per_entity"]:
        data["descriptions_per_entity"][len(descriptions)] = 0
    data["descriptions_per_entity"][len(descriptions)] += 1

    if len(descriptions.keys()) not in data["languages_per_entity_description"]:
        data["languages_per_entity_description"][len(descriptions.keys())] = 0
    data["languages_per_entity_description"][len(descriptions.keys())] += 1

    all_languages = set(descriptions.keys())
    all_languages.update(temp_languages)
    if len(all_languages) not in data["languages_per_entity"]:
        data["languages_per_entity"][len(all_languages)] = 0
    data["languages_per_entity"][len(all_languages)] += 1


if __name__ == "__main__":
    item_data = {
        "languages_labels": {},
        "languages_any_sf": {},
        "languages_aliases": {},
        "labels_per_entity_per_language": {},
        "languages_per_entity": {},
        "languages_per_entity_description": {},
        "languages_per_entity_labels": {},
        "claims_counter": {},
        "labels_per_entity": {},
        "counter": 0,
        "overlap": {"average_number": 0, "average_percentage": 0},
        "descriptions_per_language": {},
        "descriptions_per_entity": {},
    }

    property_data = {
        "languages_labels": {},
        "languages_any_sf": {},
        "languages_aliases": {},
        "labels_per_entity_per_language": {},
        "languages_per_entity": {},
        "labels_per_entity": {},
        "languages_per_entity_description": {},
        "languages_per_entity_labels": {},
        "claims_counter": {},
        "counter": 0,
        "overlap": {"average_number": 0, "average_percentage": 0},
        "descriptions_per_language": {},
        "descriptions_per_entity": {},
    }

    # Read through whole JSON entitiy by entity, filter and output to json file
    counter = 0
    with WikidataDumpReader("../data/latest-all.json.gz") as reader:
        for item in reader:
            qid = item.get("id")
            if qid[0] == "Q":
                fill_data(item_data, item)
            elif qid[0] == "P":
                fill_data(property_data, item)
            else:
                continue
            counter += 1
            if counter % 100000 == 0:
                print(counter)

        with open("language_statistics.json", "w") as f:
            json.dump({"items": item_data, "properties": property_data}, f)
