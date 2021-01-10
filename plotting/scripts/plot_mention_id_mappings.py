import json
import matplotlib.pyplot as plt
import numpy

from matplotlib import rcParams
from scipy.interpolate import make_interp_spline

rcParams.update({"figure.autolayout": True})

line_width = 2
font_size = 15


def plot_mention_id_mappings(limit=None, interpolate=False):
    with open("../wikidata_results.json") as f:
        content = json.load(f)
    details = content["details"]
    average = content["avg_ids_per_mention"]
    x = []
    y = []
    for key in sorted(details.keys(), key=lambda x: int(x)):
        x.append(int(key))
        y.append(int(details[key]))

    if interpolate:
        x = numpy.array(x)
        xnew = numpy.linspace(x.min(), x.max(), 300)
        spl = make_interp_spline(x, y, k=7)
        x = xnew
        y = spl(xnew)
    plt.figure(dpi=600)
    if limit:
        axes = plt.plot(
            x[0:limit] + [x[limit - 1] + 1],
            y[0:limit] + [sum(y[limit:])],
            linewidth=line_width,
        )
    else:
        axes = plt.plot(x, y, linewidth=line_width)
    plt.yscale("log")
    plt.xscale("log")
    plt.xlabel("Number of items", fontsize=font_size)
    plt.ylabel("Number of labels/aliases", fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.savefig("mention_id_mapping.pdf")


plot_mention_id_mappings()
