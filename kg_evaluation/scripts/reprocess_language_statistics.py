import json
import copy
from argparse import ArgumentParser

def sort_dictionary(dict_: dict, by_key=False, reversed_=True):
    return {
        key: value
        for key, value in sorted(
            list(dict_.items()),
            key=lambda a: a[0 if by_key else 1] * (-1 if reversed_ else 1),
        )
    }


def interpret(sub_content: dict):
    sub_reprocessed = {}
    counter = sub_content["counter"]
    sub_reprocessed["average_overlap"] = (
        sub_content["overlap"]["average_number"] / counter
    )
    sub_reprocessed["average_percentage"] = (
        sub_content["overlap"]["average_percentage"] / counter
    )
    sub_reprocessed["any_sf_per_language"] = sort_dictionary(
        {
            key: value / counter
            for key, value in copy.deepcopy(sub_content["languages_any_sf"]).items()
        }
    )
    sub_reprocessed["label_per_entity"] = sort_dictionary(
        {
            key: value / counter
            for key, value in copy.deepcopy(sub_content["languages_labels"]).items()
        }
    )
    sub_reprocessed["languages_aliases"] = sort_dictionary(
        {
            key: value / counter
            for key, value in copy.deepcopy(sub_content["languages_aliases"]).items()
        }
    )
    sub_reprocessed["num_languages"] = len(sub_content["languages_labels"])

    sub_reprocessed["languages_per_entity"] = sort_dictionary(
        {
            key: value / counter
            for key, value in sub_content["languages_per_entity"].items()
        },
        False,
        True,
    )
    sub_reprocessed["languages_num_labels_aliases"] = sort_dictionary(
        {
            key: sum([int(key_) * value_ for key_, value_ in value.items()]) / counter
            for key, value in sub_content["labels_per_entity_per_language"].items()
        }
    )

    sub_reprocessed["average_number_of_labels"] = (
        sum(
            [
                int(key) * value
                for key, value in sub_content["labels_per_entity"].items()
            ]
        )
        / counter
    )
    sub_reprocessed["languages_per_entity_avg"] = (
        sum(
            [
                int(key) * value
                for key, value in sub_content["languages_per_entity"].items()
            ]
        )
        / counter
    )

    sub_reprocessed["average_number_of_languages_labels"] = (
        sum(
            [
                int(key) * value
                for key, value in sub_content["languages_per_entity_labels"].items()
            ]
        )
        / counter
    )

    sub_reprocessed["average_number_of_languages_descriptions"] = (
        sum(
            [
                int(key) * value
                for key, value in sub_content["descriptions_per_entity"].items()
            ]
        )
        / counter
    )
    sub_reprocessed["average_number_of_languages_descriptions_v2"] = (
        sum(
            [
                int(key) * value
                for key, value in sub_content[
                    "languages_per_entity_description"
                ].items()
            ]
        )
        / counter
    )
    sub_reprocessed["description_per_languages"] = sort_dictionary(
        {
            key: value / counter
            for key, value in copy.deepcopy(
                sub_content["descriptions_per_language"]
            ).items()
        }
    )
    sub_reprocessed["descriptions_per_entity"] = sort_dictionary(
        {
            key: value / counter
            for key, value in sub_content["descriptions_per_entity"].items()
        },
        False,
        True,
    )

    return sub_reprocessed


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)

    args = parser.parse_args()
    reprocessed = {}
    with open(args.filename) as f:
        content = json.load(f)
        reprocessed["items"] = interpret(content["items"])

        reprocessed["properties"] = interpret(content["properties"])

    with open("language_statistics_reprocessed.json", "w") as f:
        json.dump(reprocessed, f, indent=4)
