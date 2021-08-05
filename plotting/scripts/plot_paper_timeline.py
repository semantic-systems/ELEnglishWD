from matplotlib import pyplot as plt

from matplotlib import rcParams

rcParams.update({"figure.autolayout": True})

figure = plt.figure(dpi=600)

# Publishing years and number of scientific works considered in survey
years = [2017, 2018, 2019, 2020]
papers = [0, 2, 2, 11]

plt.bar(years, papers)

line_width = 2
font_size = 15
plt.ylabel("Published papers", fontsize=font_size)
plt.xlabel("Years", fontsize=font_size)

plt.xticks(years, fontsize=font_size)
labels = list(range(0, 12, 1))
labels = [str(item) if idx % 2 == 0 else "" for idx, item in enumerate(labels)]
plt.yticks(list(range(0, 12, 1)), labels, fontsize=font_size)

plt.savefig("papers_timeline.pdf")
