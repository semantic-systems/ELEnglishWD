from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

import json

from matplotlib import rcParams

# Plots the qualifier statistics for the LC-QuAD 2.0 dataset and Wikidata

line_width = 2
font_size = 15
rcParams.update({"figure.autolayout": True})

with open("./results/datasets_stats/results_lcquad2.0.json") as f:
    data = json.load(f)
count_dict_lc_quad: dict = data["count_dict"]
sorted_lc_quad = sorted(count_dict_lc_quad.items(), key=lambda x: int(x[0]))

with open("./scripts/output.json") as f:
    data = json.load(f)
count_dict_wikidata: dict = data["items"]["claims_counter"]
sorted_wikidata = sorted(count_dict_wikidata.items(), key=lambda x: int(x[0]))

x = [int(item[0]) for item in sorted_lc_quad]
y = [int(item[1]) for item in sorted_lc_quad]
y = [item / sum(y) * 100 for item in y]
panda_data = {x[idx]: [y[idx]] for idx in range(6)}
panda_data["> 5"] = sum(y[6:])
df_lc_quad = pd.DataFrame(panda_data, index=["LC-QuAD 2.0"])


x = [int(item[0]) for item in sorted_wikidata]
y = [int(item[1]) for item in sorted_wikidata]
y = [item / sum(y) * 100 for item in y]
panda_data = {x[idx]: [y[idx]] for idx in range(6)}
panda_data["> 5"] = sum(y[6:])
df_wikidata = pd.DataFrame(panda_data, index=["Wikidata"])

fig = plt.figure(dpi=1200)

containers = (
    pd.concat(dict(df1=df_lc_quad, df2=df_wikidata), axis=0)
    .plot(kind="bar", stacked=True, legend=True)
    .containers
)

for container in containers:
    container[1].xy = (0.5, container[1].xy[1])

plt.xticks(ticks=[0, 0.75], labels=["LC-QuAD 2.0", "Wikidata"], rotation="horizontal")
ax = plt.axes()
ax.legend(title="Qualifiers", loc="upper right")
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
plt.ylabel("Percentage", fontsize=font_size)
plt.xticks(fontsize=font_size)
plt.yticks(fontsize=font_size)
fig.autofmt_xdate()
ax.set_rasterized(True)
plt.savefig("statement_qualifiers_bar_both.pdf",)
