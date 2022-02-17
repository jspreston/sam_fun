from typing import Set, List
import copy
import sys

from .wordlebot import (
    WordScorer,
    WordleBot,
    generate_guess_response,
    ALPHABET,
    WORD_LENGTH,
)

import numpy as np


class BruteForceWordScorer(WordScorer):
    def __init__(self):
        pass

    def update(self, wordle_bot: WordleBot) -> None:
        self.possible_words = set(wordle_bot.possible_words)
        self.word_state = copy.deepcopy(wordle_bot.word_state)

    def _calc_updated_possible_words(
        self, possible_words: Set[str], true_word: str, guess_word: str
    ) -> Set[str]:
        """given a set of possible words and the true word, return the updated set of
        possible words once 'guess_word' is guessed"""
        word_state = copy.deepcopy(self.word_state)
        word_state.update_state(generate_guess_response(guess_word, true_word))
        return word_state.get_possible_words(possible_words)

    def score_word(self, word: str) -> float:
        score = 0
        for true_word in self.possible_words:
            # check how many words remain if true_word is actually the true_word
            remaining_words = self._calc_updated_possible_words(
                set(self.possible_words), true_word=true_word, guess_word=word
            )
            removed_words = len(self.possible_words) - len(remaining_words)
            score += removed_words
            # make sure to score finding the true word as well
            if word == true_word:
                score += 1
        normalized_score = score / len(self.possible_words) ** 2
        return normalized_score


class FastBruteForceWordScorer(WordScorer):
    def __init__(self, all_words: List[str]):
        self.letter_to_index = {letter: idx for idx, letter in enumerate(ALPHABET)}
        self.all_words = list(all_words)
        self.all_words_array = self._word_list_to_array(self.all_words)

    def _word_list_to_array(self, word_list: List[str]) -> np.ndarray:
        word_array = np.zeros((len(word_list), WORD_LENGTH), dtype=np.int8)
        for widx, word in enumerate(word_list):
            word_array[widx, :] = self._word_to_indices(word)
        return word_array

    def _word_to_indices(self, word: str) -> np.ndarray:
        return np.array(
            [self.letter_to_index[letter] for letter in word], dtype=np.int8
        )

    def update(self, wordle_bot: WordleBot) -> None:
        self.possible_words = list(wordle_bot.possible_words)
        self.possible_words_array = self._word_list_to_array(self.possible_words)

    def _calc_letter_state(
        self, true_word_array: np.ndarray, guess_word_array: np.ndarray
    ):
        """create internal numpy arrays"""
        letter_state = np.ones((WORD_LENGTH, len(ALPHABET)), dtype=np.bool8)
        required_letters = set()
        # guess_array = self._word_to_indices(guess_word)
        # true_array = self._word_to_indices(true_word)
        for letter_pos, (true_idx, guess_idx) in enumerate(
            zip(true_word_array, guess_word_array)
        ):
            if guess_idx == true_idx:
                # only this letter can be true at this position
                letter_state[letter_pos, :] = False
                letter_state[letter_pos, guess_idx] = True
            elif np.any(guess_idx == true_word_array):
                # guess letter can't be at this position
                letter_state[letter_pos, guess_idx] = False
                required_letters.add(guess_idx)
            else:
                # this letter can't be at any position
                letter_state[:, guess_idx] = False

        self.letter_state = letter_state
        self.required_letters = required_letters

    def score_word(self, word: str) -> float:
        score = 0
        guess_word_array = self._word_to_indices(word)
        letter_positions = np.arange(WORD_LENGTH, dtype=np.int8)
        for true_idx in range(len(self.possible_words)):
            true_word_array = self.possible_words_array[true_idx]
            self._calc_letter_state(
                true_word_array=true_word_array, guess_word_array=guess_word_array
            )
            for test_idx in range(len(self.possible_words)):
                # check if it contains letters we know to be absent
                test_word = self.possible_words_array[test_idx]
                # if the word is missing letters that are required
                if self.required_letters.difference(set(test_word)):
                    score += 1
                # if any of the letters can't occur at the given position
                elif not np.all(self.letter_state[letter_positions, test_word]):
                    score += 1

        normalized_score = score / len(self.possible_words) ** 2
        return normalized_score
