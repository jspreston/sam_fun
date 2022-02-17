import argparse
from typing import List

from wordlebot import (
    WordleBot,
    FrequencyWordScorer,
    FastBruteForceWordScorer,
    BruteForceWordScorer,
    generate_guess_response,
    GuessState,
    EMOJI_MAP,
)
import pandas as pd


def play_word(wordle_bot: WordleBot, true_word, initial_word: str = None) -> int:
    """play a fake game against 'true_word', and return the number of tries needed to win"""
    for guess_idx in range(1, 7):
        if guess_idx == 1 and initial_word:
            guess_word = initial_word
        else:
            guess_word = wordle_bot.suggest()
        print(f"playing word {guess_word}")
        guess_response = generate_guess_response(
            guess_word=guess_word, true_word=true_word
        )
        if all(
            [
                letter_response.state == GuessState.CORRECT
                for letter_response in guess_response
            ]
        ):
            print(f"WordleBot won in {guess_idx} guesses!")
            guesses = list(wordle_bot.guess_history)
            guesses.append(guess_response)
            for guess in guesses:
                print(
                    "".join([EMOJI_MAP[letter_guess.state] for letter_guess in guess])
                )
            return guess_idx
        wordle_bot.guess(guess_response=guess_response)

    print("Oh no! WordleBot failed!")
    return -1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("true_word")
    parser.add_argument("--scorer", default="brute_force")
    parser.add_argument("--initial_word", default="cares")
    args = parser.parse_args()

    wordle_word_freq = pd.read_csv("wordle_word_freq.csv")
    word_to_freq = {
        word: freq
        for word, freq in zip(
            wordle_word_freq.word.values, wordle_word_freq["count"].values
        )
    }

    if args.scorer == "brute_force":
        word_scorer = BruteForceWordScorer()
    elif args.scorer == "fast_brute_force":
        word_scorer = FastBruteForceWordScorer(list(word_to_freq.keys()))
    elif args.scorer == "frequency":
        word_scorer = FrequencyWordScorer()
    else:
        raise ValueError(f"Unknown scorer {args.scorer}")

    # word_scorer = FrequencyWordScorer()
    wordle_bot = WordleBot(word_to_freq=word_to_freq, word_scorer=word_scorer)
    play_word(wordle_bot, args.true_word, initial_word=args.initial_word)
