import csv
import json
import datetime
import matplotlib.pyplot as plt
from matplotlib import rcParams


def parse_date(date: str):
    return datetime.date(int(date[0:4]), int(date[4:6]), int(date[6:8]))


def plot_labels_per_item(data):
    labels_per_item = []
    percentage_without_aliases = []
    x = []
    count = 0
    for key, item in data.items():
        days = parse_date(key) - start_date
        x.append(days.days)
        current_labels_per_item = 0
        count_items = 0
        number_without_aliases = 0
        for key, value in item["labels_per_item"].items():
            current_labels_per_item += int(key) * value
            count_items += value
            if key == "1":
                number_without_aliases = value
        percentage_without_aliases.append(number_without_aliases / count_items * 100)
        current_labels_per_item /= count_items
        labels_per_item.append(current_labels_per_item)
        count += 1
    plt.figure(dpi=600)
    axes = plt.plot(x, labels_per_item, linewidth=line_width)
    plt.xlabel("Days since launch", fontsize=font_size)
    plt.ylabel("Average number of labels per item", fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.savefig("labels_per_item.pdf")

    plt.figure(dpi=600)
    axes = plt.plot(x, percentage_without_aliases, linewidth=line_width)
    plt.xlabel("Days since launch", fontsize=font_size)
    plt.ylabel("% of items without aliases", fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.savefig("percentage_items_without_aliases.pdf")


# uses active_editors.csv which can be found at https://stats.wikimedia.org/#/wikidata.org/contributing/active-editors/
def plot_active_editors():
    t = []
    e = []
    with open("../data/active_editors.csv") as f:
        reader = csv.DictReader(f)
        for line in reader:
            date = line.get("month")
            date = datetime.date(int(date[0:4]), int(date[5:7]), int(date[8:10]))
            t.append(date)
            e.append(int(line.get("total.total")))

    fig = plt.figure(dpi=600)
    plt.plot(t, e, linewidth=line_width)
    plt.xlabel("Time", fontsize=font_size)
    plt.ylabel("Active editors", fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    fig.autofmt_xdate()
    plt.savefig("active_editors.pdf")


def plot_statements_per_item(data):
    statements_per_item = []
    x = []
    count = 0
    for key, item in data.items():
        if not isinstance(item["statements_per_item"], dict):
            continue
        days = parse_date(key) - start_date
        x.append(days.days)
        current_statements_per_item = 0
        count_items = 0

        for key, value in item["statements_per_item"].items():
            current_statements_per_item += int(key) * value
            count_items += value
        current_statements_per_item /= count_items
        statements_per_item.append(current_statements_per_item)
        count += 1
    plt.figure()
    axes = plt.plot(x, statements_per_item)
    plt.xlabel("Days since launch")
    plt.ylabel("Statements per item")
    plt.savefig("statements_per_item.pdf")


def plot_descriptions_per_item(data):
    descriptions_per_item = []
    percentage_without_aliases = []
    x = []
    count = 0
    for key, item in data.items():
        days = parse_date(key) - start_date
        x.append(days.days)
        current_descriptions_per_item = 0
        count_items = 0
        number_without_description = 0
        for key, value in item["descs_per_item"].items():
            current_descriptions_per_item += int(key) * value
            count_items += value
            if key == "0":
                number_without_description = value
        percentage_without_aliases.append(
            number_without_description / count_items * 100
        )
        current_descriptions_per_item /= count_items
        descriptions_per_item.append(current_descriptions_per_item)
        count += 1
    plt.figure(dpi=600)
    axes = plt.plot(x, descriptions_per_item, linewidth=line_width)
    plt.xlabel("Days since launch", fontsize=font_size)
    plt.ylabel("Average number of descriptions per item", fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.savefig("descriptions_per_item.pdf")

    plt.figure(dpi=600)
    axes = plt.plot(x, percentage_without_aliases, linewidth=line_width)
    plt.xlabel("Days since launch", fontsize=font_size)
    plt.ylabel("% of items without description", fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.savefig("percentage_items_without_description.pdf")


def plot_links_per_item(data):
    statements_per_item = []
    x = []
    count = 0
    for key, item in data.items():
        days = parse_date(key) - start_date
        x.append(days.days)
        current_statements_per_item = 0
        count_items = 0
        for key, value in item["links_per_item"].items():
            current_statements_per_item += int(key) * value
            count_items += value
        current_statements_per_item /= count_items
        statements_per_item.append(current_statements_per_item)
        count += 1
    plt.figure()
    axes = plt.plot(x, statements_per_item)
    plt.xlabel("Days since launch")
    plt.ylabel("Links per item")
    plt.savefig("links_per_item.pdf")


def plot_num_items(data):
    total_items = []
    x = []
    count = 0
    for key, item in data.items():
        days = parse_date(key) - start_date
        x.append(days.days)
        total_items.append(item["total_items"])
        count += 1
    fig = plt.figure(dpi=600)
    axes = plt.plot(x, total_items, linewidth=line_width)
    plt.xlabel("Days since launch", fontsize=font_size)
    plt.ylabel("Number of items", fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    axes[0].axes.yaxis.get_offset_text().set_fontsize(font_size)
    plt.savefig("items_wikidata.pdf")


rcParams.update({"figure.autolayout": True})

line_width = 2
font_size = 15

# stats.php.json is provided at https://wikidata-todo.toolforge.org/stats.php
with open("stats.php.json") as f:
    data = json.load(f)

start_date = datetime.date(2013, 2, 4)