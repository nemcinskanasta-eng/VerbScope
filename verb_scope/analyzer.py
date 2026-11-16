"""Morphological analysis of Ukrainian verbs with Stanza."""

from functools import lru_cache
import stanza


@lru_cache(maxsize=1)
def get_pipeline():
    """Create the Ukrainian Stanza pipeline (downloads the model if needed)."""
    try:
        return stanza.Pipeline(
            lang="uk",
            processors="tokenize,pos,lemma",
            use_gpu=False,
            verbose=False,
        )
    except Exception as exc:
        raise RuntimeError(
            "Не вдалося завантажити мовну модель Stanza для української. "
            "Перевірте інтернет і виконайте: uv run python -c "
            "\"import stanza; stanza.download('uk')\""
        ) from exc


def _feature(word, key):
    value = word.feats or ""
    for item in value.split("|"):
        if item.startswith(key + "="):
            return item.split("=", 1)[1]
    return None


def _translate_time(value):
    return {
        "Past": "минулий",
        "Pres": "теперішній",
        "Fut": "майбутній",
    }.get(value, "не визначено")


def _translate_number(value):
    return {
        "Sing": "однина",
        "Plur": "множина",
    }.get(value, "не визначено")


def _translate_gender(value):
    return {
        "Masc": "чоловічий",
        "Fem": "жіночий",
        "Neut": "середній",
    }.get(value, "не визначено")


def analyze_text(text):
    """
    Return a list of detected verb forms and grammatical features.

    Stanza's Ukrainian model supplies UPOS and morphological features.
    Infinitives and participles may not have tense/number/gender values;
    these are shown as 'не визначено' rather than guessed.
    """
    if not text or not text.strip():
        return []

    doc = get_pipeline()(text)
    results = []
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.upos not in {"VERB", "AUX"}:
                continue

            tense = _feature(word, "Tense")
            number = _feature(word, "Number")
            gender = _feature(word, "Gender")

            results.append({
                "word": word.text,
                "lemma": word.lemma or word.text,
                "upos": word.upos,
                "time": _translate_time(tense),
                "number": _translate_number(number),
                "gender": (
                    _translate_gender(gender)
                    if tense == "Past"
                    else "—"
                ),
            })
    return results
