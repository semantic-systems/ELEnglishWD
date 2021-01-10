import json

import matplotlib.pyplot as plt

with open("../data/wikidata_label_lengths.json") as f:
    content = json.load(f)

lengths_ = content["percentiles"]
percentiles = list(range(0, 101, 1))
line_width = 2
font_size = 15
fig = plt.figure(dpi=600)
plt.plot(lengths_, percentiles, linewidth=line_width)
plt.xlabel(r"Length $\ell$", fontsize=font_size)
plt.ylabel(r"% of labels with $length \leq \ell$", fontsize=font_size)
plt.xticks(fontsize=font_size)
plt.yticks(fontsize=font_size)
fig.autofmt_xdate()
plt.savefig("wikidata_length_percentiles.pdf")
