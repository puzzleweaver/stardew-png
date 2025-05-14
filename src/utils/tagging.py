
from typing import Callable


def splitTagsBySign(tags):
    tagsToAdd = [
        tag for tag in tags
        if tag[0] != '-'
    ]
    tagsToRemove = [
        tag[1:] for tag in tags
        if tag[0] == '-'
    ]
    return tagsToAdd, tagsToRemove

def addLists(
    list1: list[str], 
    list2: list[str],
) -> list[str]:
    return list(set(list1).union(set(list2)))

def subtractLists(
    list1: list[str],
    list2: list[str],
) -> list[str]:
    return list(set(list1).difference(set(list2)))

def collect(
    list: list[str],
    by: Callable[[str], list[str]],
    transform: Callable[[str], any],
) -> dict[str, list[str]]:
    ret = {}
    for item in list:
        key = by(item)
        if not key in ret: ret[key] = []
        ret[key].append(
            transform(item)
        )
    return ret
