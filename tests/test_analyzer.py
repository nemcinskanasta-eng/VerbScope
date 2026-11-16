"""Basic tests for the Ukrainian verb analyzer.

The first run may download the Stanza Ukrainian model.
Run with: uv run pytest
"""

import pytest
from verb_scope.analyzer import analyze_text


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Марія читала книжку.", "читала"),
        ("Студенти пишуть роботу.", "пишуть"),
        ("Завтра ми поїдемо додому.", "поїдемо"),
    ],
)
def test_expected_verb_is_detected(text, expected):
    results = analyze_text(text)
    forms = [item["word"].lower() for item in results]
    assert expected in forms


def test_empty_text_returns_empty_list():
    assert analyze_text("   ") == []
