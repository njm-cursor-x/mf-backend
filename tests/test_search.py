from app.search import rank_movies, score_title


class _Movie:
    def __init__(self, movie_id: str, title: str):
        self.id = movie_id
        self.title = title


def test_strips_leading_article():
    assert score_title("odyssey", "The Odyssey") >= 88


def test_asr_near_miss():
    movies = [
        _Movie("the-odyssey", "The Odyssey"),
        _Movie("sinners", "Sinners"),
    ]
    ranked = rank_movies("the odysy", movies)
    assert ranked[0][1].id == "the-odyssey"


def test_ambiguous_keeps_short_list():
    movies = [
        _Movie("spider-man-brand-new-day", "Spider-Man: Brand New Day"),
        _Movie("sinners", "Sinners"),
        _Movie("the-end-of-oak-street", "The End of Oak Street"),
    ]
    ranked = rank_movies("spider man", movies)
    assert ranked[0][1].id == "spider-man-brand-new-day"
    assert len(ranked) <= 5
