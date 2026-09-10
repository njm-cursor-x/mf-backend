import re

from rapidfuzz import fuzz

_LEADING_ARTICLE = re.compile(r"^(the|a|an)\s+", re.I)
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_title(value: str) -> str:
    text = value.casefold().strip()
    text = _LEADING_ARTICLE.sub("", text)
    text = _NON_ALNUM.sub(" ", text)
    return " ".join(text.split())


def score_title(query: str, title: str) -> int:
    q = normalize_title(query)
    t = normalize_title(title)
    if not q:
        return 0
    if q == t:
        return 100
    if t.startswith(q) or q.startswith(t):
        return max(88, fuzz.ratio(q, t))
    token = fuzz.token_set_ratio(q, t)
    partial = fuzz.partial_ratio(q, t)
    ratio = fuzz.ratio(q, t)
    return int(round(max(token, partial, ratio)))


def rank_movies(query: str, movies: list, limit: int = 5, floor: int = 62) -> list:
    scored = []
    for movie in movies:
        score = score_title(query, movie.title)
        if score >= floor:
            scored.append((score, movie))
    scored.sort(key=lambda item: (-item[0], item[1].title))
    return scored[:limit]
