from w3lib.html import replace_tags


def cleanup(data):
    if data is None:
        return ""
    elif isinstance(data, list):
        result = list()
        for e in data:
            result.append(cleanup(e))
        return result
    else:
        return replace_tags(data, " ").strip().strip("\n")
