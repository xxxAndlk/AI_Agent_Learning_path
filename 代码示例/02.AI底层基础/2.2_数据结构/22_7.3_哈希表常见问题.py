from collections import defaultdict

def group_anagrams(strs):
    """按排序后的字符串作为键"""
    groups = defaultdict(list)
    for s in strs:
        key = "".join(sorted(s))
        groups[key].append(s)
    return list(groups.values())
