from .wordlebot import (
    WordScorer,
    WordleBot,
    ALPHABET,
    WORD_LENGTH,
)

import numpy as np
import pandas as pd


class FrequencyWordScorer(WordScorer):
    def __init__(self):
        self.lidx_lookup = {letter: lidx for lidx, letter in enumerate(ALPHABET)}

    def _calc_frequency_table(self, possible_words) -> np.ndarray:
        print(f"There are {len(possible_words)} possible words")
        if len(possible_words) < 10:
            print(possible_words)
        else:
            print("too many to print...")
        letter_count_table = np.zeros([WORD_LENGTH, len(ALPHABET)])
        for word in possible_words:
            for lidx, letter in enumerate(word):
                letter_count_table[lidx, self.lidx_lookup[letter]] += 1
        return letter_count_table / len(possible_words)

    def update(self, wordle_bot: WordleBot) -> None:
        possible_words = wordle_bot.possible_words
        self.letter_frequency = self._calc_frequency_table(possible_words)
        # set zero value for letter/position combos we know can't work
        for letter in ALPHABET:
            for lidx in range(WORD_LENGTH):
                letter_state = wordle_bot.word_state.state[lidx]
                if (
                    letter not in letter_state.possible_letters
                    or len(letter_state.possible_letters) == 1
                ):
                    self.letter_frequency[lidx, self.lidx_lookup[letter]] = 0
        self.print_pretty_letter_frequency()

    def print_pretty_letter_frequency(self):
        print(pd.DataFrame(self.letter_frequency, columns=list(ALPHABET)))

    def _score_letter(self, lidx: int, letter: str) -> float:
        return self.letter_frequency[lidx, self.lidx_lookup[letter]]

    def score_word(self, word: str) -> float:
        score = 0
        used_letters = set()
        for lidx, letter in enumerate(word):
            if letter in used_letters:
                continue
            used_letters.add(letter)
            score += self._score_letter(lidx, letter)
        return score
