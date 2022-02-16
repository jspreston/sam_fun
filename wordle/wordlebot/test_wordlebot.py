from wordle.wordlebot import generate_guess_response, GuessState, WordState


def test_generate_guess_response():
    guess_response = generate_guess_response(guess_word="cares", true_word="strap")
    assert guess_response[0].letter == "c"
    assert guess_response[0].state == GuessState.NOT_IN_WORD
    assert guess_response[1].letter == "a"
    assert guess_response[1].state == GuessState.IN_WORD
    assert guess_response[2].letter == "r"
    assert guess_response[2].state == GuessState.CORRECT
    assert guess_response[3].letter == "e"
    assert guess_response[3].state == GuessState.NOT_IN_WORD
    assert guess_response[4].letter == "s"
    assert guess_response[4].state == GuessState.IN_WORD


def test_word_state():
    vocab = [
        "zebra",
        "moose",
        "birds",
        "robin",
        "snake",
        "mouse",
        "tapir",
        "sheep",
        "goose",
        "ayaye",
    ]
    true_word = "mouse"

    ws = WordState()
    filtered_words = ws.get_possible_words(vocab)
    assert set(filtered_words) == set(vocab)

    # guess snake
    guess_response = generate_guess_response(guess_word="snake", true_word=true_word)
    assert guess_response[0].state == GuessState.IN_WORD
    assert guess_response[1].state == GuessState.NOT_IN_WORD
    assert guess_response[2].state == GuessState.NOT_IN_WORD
    assert guess_response[3].state == GuessState.NOT_IN_WORD
    assert guess_response[4].state == GuessState.CORRECT
    ws.update_state(guess_response=guess_response)
    filtered_words = ws.get_possible_words(vocab)
    expected_words = ["moose", "goose", "mouse"]
    assert set(filtered_words) == set(expected_words)


if __name__ == "__main__":
    test_generate_guess_response()
    test_word_state()
