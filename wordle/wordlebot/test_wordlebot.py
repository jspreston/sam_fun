
from wordle.wordlebot.wordlebot import generate_guess_response, GuessState


def test_generate_guess_response():
    guess_response = generate_guess_response(guess_word="strap", true_word="cares")
    assert guess_response[0] == GuessState.NOT_IN_WORD
    assert guess_response[1] == GuessState.IN_WORD
    assert guess_response[2] == GuessState.CORRECT
    assert guess_response[3] == GuessState.NOT_IN_WORD
    assert guess_response[4] == GuessState.IN_WORD


if __name__ == "__main__":
    test_generate_guess_response()
    