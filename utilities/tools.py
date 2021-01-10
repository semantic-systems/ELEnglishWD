import shlex


def n_wise(iterable, n=2):
    new_list = []

    temp_list = []
    for item in iterable:
        if len(temp_list) == n:
            new_list.append(temp_list)
            temp_list = []
        temp_list.append(item)
    else:
        if temp_list:
            new_list.append(temp_list)
    return new_list


def split_uri_and_label(line: str):
    split_line = shlex.split(line)
    uri = split_line[0]
    uri = uri[1:-1]
    label: str = split_line[2]
    label = label.replace("@en", "")
    return uri, label