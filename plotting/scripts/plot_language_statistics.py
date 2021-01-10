import json
from matplotlib import pyplot as plt


def sub_plot_routine(data, normalizer=1, filename=None):
    plt.figure(dpi=600)
    tuple_list = list(data.items())
    tuple_list = [(int(key), value / normalizer) for key, value in tuple_list]
    tuple_list = sorted(tuple_list, key=lambda x: x[0])

    x, y = [], []
    for key, value in tuple_list:
        x.append(int(key))
        y.append(value)
    cumulative_y = []
    current_sum = 0
    already_printed = False
    for item_x, item in zip(x, y):
        current_sum += item
        if current_sum >= 0.5 and not already_printed:
            print(filename)
            print(item_x)
            already_printed = True
        cumulative_y.append(current_sum)
    plt.plot(x, cumulative_y)
    plt.xlabel("Number of languages")
    plt.ylabel("Percentage having up to x languages")
    plt.savefig(filename + ".png")


def plot_and_save(sub_content: dict, suffix: str):
    normalizer = sub_content["counter"]
    languages_per_entity = sub_content["languages_per_entity"]
    sub_plot_routine(languages_per_entity, normalizer, "languages_" + suffix)

    languages_per_entity_description = sub_content["languages_per_entity_description"]
    sub_plot_routine(
        languages_per_entity_description, normalizer, "languages_desc_" + suffix
    )
    languages_per_entity_labels = sub_content["languages_per_entity_labels"]
    sub_plot_routine(
        languages_per_entity_description, normalizer, "languages_labels_" + suffix
    )


with open("language_statistics.json") as f:
    content = json.load(f)
    plot_and_save(content["items"], "items")

    plot_and_save(content["properties"], "props")
