import argparse
from typing import List
from pathlib import Path

from wordlebot.wordlebot import GuessState, LetterGuess, LetterState, GuessState
from wordlebot import (
    WordleBot,
    FrequencyWordScorer,
    FastBruteForceWordScorer,
    BruteForceWordScorer,
)
import pandas as pd


def _char_to_guess_response(letter_response: str) -> GuessState:
    if letter_response.lower() == "n":
        return GuessState.NOT_IN_WORD
    elif letter_response.lower() == "i":
        return GuessState.IN_WORD
    elif letter_response.lower() == "c":
        return GuessState.CORRECT
    raise ValueError(f"Unknown response {letter_response}")


def input_to_word_response(user_input) -> List[LetterGuess]:
    word, response = user_input.split()
    letter_responses = [
        LetterGuess(letter, _char_to_guess_response(letter_response))
        for letter, letter_response in zip(word, response)
    ]
    return letter_responses


CUR_DIR = Path(__file__).parent
RESOURCE_DIR = CUR_DIR / "resources"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--scorer", default="brute_force")
    args = parser.parse_args()

    # wordle_word_freq = pd.read_csv("wordle_word_freq.csv")
    # word_to_freq = {
    #     word: freq
    #     for word, freq in zip(
    #         wordle_word_freq.word.values, wordle_word_freq["count"].values
    #     )
    # }

    # read csv with one column and set column name to "word"
    wordle_words = pd.read_csv(RESOURCE_DIR / "word-bank.csv", names=["word"])
    word_to_freq = {word: 1 for word in wordle_words.word.values}

    if args.scorer == "brute_force":
        word_scorer = BruteForceWordScorer()
    elif args.scorer == "fast_brute_force":
        word_scorer = FastBruteForceWordScorer(list(word_to_freq.keys()))
    elif args.scorer == "frequency":
        word_scorer = FrequencyWordScorer()
    else:
        raise ValueError(f"Unknown scorer {args.scorer}")

    guesses = []

    # word_scorer = FrequencyWordScorer()
    wordle_bot = WordleBot(word_to_freq=word_to_freq, word_scorer=word_scorer)
    while True:
        print(f"{len(wordle_bot.possible_words)} possible words remain")
        print(
            "For a suggestion, enter 's', or to print the possible words, enter 'p'. "
            "Otherwise enter 'guess_word response', where response consists of: "
            " n=not in word, i=in word, and c=correct, e.g. 'cares nicnn' "
            "if 'cares' was played, a, was in the word, and r was correct."
        )
        user_input = input().strip().lower()
        if user_input == "p":
            print(wordle_bot.possible_words)
        elif user_input == "s":
            print("Calculating suggestion...")
            suggestion = wordle_bot.suggest()
            print(suggestion)
        else:
            response = input_to_word_response(user_input)
            wordle_bot.guess(response)

    # word_scorer = FastBruteForceWordScorer(list(word_to_freq.keys()))
    # wordle_bot = WordleBot(word_to_freq=word_to_freq, word_scorer=word_scorer)
    # scored_words = wordle_bot._score_words(wordle_bot.all_words)
    # print(scored_words[:10])
