import json
from pathlib import Path

from scipy.stats import scoreatpercentile

folder = Path(".")

files = [file for file in folder.glob("*.json")]
percentiles_range = list(range(101))

for file in files:
    print(file.stem)
    if not file.stem.startswith("results_es"):
        continue
    data = json.load(file.open())
    if "num_no_exact_match" in data:
        continue
    exact_matches = data["exact_matches"]
    unsuccessful = data["unsuccessful"]
    counter = data["counter"]
    num_no_exact_match = round(
        (len([item for item in exact_matches if item == 0])) / counter * 100, 3
    )
    num_one_exact_match = round(
        len([item for item in exact_matches if item == 1]) / counter * 100, 3
    )
    num_greater_one_exact_match = round(
        len([item for item in exact_matches if item > 1]) / counter * 100, 3
    )
    percentiles = scoreatpercentile(sorted(exact_matches), percentiles_range)
    data["average_exact_matches"] = round(sum(exact_matches) / counter, 3)
    data["accuracy"] = round(data["successful"] / counter, 3)
    data["accuracy_filtered_v2"] = round(data["accuracy_filtered_v2"], 3)
    data["percentage_exact_matches_successful"] = round(
        data["exact_matches_true"] / len([item for item in exact_matches if item == 1]),
        2,
    )
    data["accuracy_cleared_of_exact"] = data["accuracy"] - (num_one_exact_match / 100)
    data.update(
        {
            "num_no_exact_match": num_no_exact_match,
            "num_greater_one_exact_match": num_greater_one_exact_match,
            "num_one_exact_match": num_one_exact_match,
            "percentiles": list(percentiles),
        }
    )

    key_order = []
    for key, value in data.items():
        if isinstance(value, list) or isinstance(value, dict):
            key_order.append(key)
        else:
            key_order = [key] + key_order

    new_data = {}
    for key in key_order:
        new_data[key] = data[key]
    json.dump(new_data, Path(file.stem + "_reprocessed.json").open("w"), indent=4)
