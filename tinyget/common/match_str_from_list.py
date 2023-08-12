from rapidfuzz import process


def match_str_from_list(keyword, str_list, limit):
    found = process.extract(keyword, str_list, limit=limit)
    return [ele[0] for ele in found]
