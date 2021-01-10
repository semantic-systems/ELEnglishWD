from tqdm import tqdm

with open("labels.nt") as f:

    line = f.readline()
    ids = set()
    pbar = tqdm(total=81065185)
    while line:
        splits = line.split()
        ident = splits[0]
        ident = ident.replace(">", "")
        ident = ident.replace("<", "")
        ident = int(ident[ident.rfind("/") + 2 :])
        ids.add(ident)
        line = f.readline()
        pbar.update(1)
    print(len(ids))
