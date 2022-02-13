# Initial work on wordle automation
from typing import Dict, List, Set, Optional, Iterable, Tuple
from enum import Enum
from dataclasses import dataclass
import copy
import sys
import re

import pandas as pd
import numpy as np


class LetterState(Enum):
    """State of a letter in the alphabet"""

    NOT_IN_WORD = -1
    UNKNOWN = 0
    IN_WORD = 1


class GuessState(Enum):
    """Response from wordle for a particular letter in a particular position"""

    NOT_IN_WORD = 0
    IN_WORD = 1
    CORRECT = 2


ALPHABET = "abcdefghijklmnopqrstuvwxyz"
WORD_LENGTH = 5


@dataclass
class LetterGuess:
    letter: str
    state: GuessState


class PositionState:
    """Class to hold our knowledge about a specific letter position, for instance if we
    know the letter that must go here or we know some letters that cannot go here."""

    def __init__(self):
        self.possible_letters: Set[str] = set(ALPHABET)

    def remove_letter(self, letter: str):
        self.possible_letters.discard(letter)

    def set_letter(self, letter: str):
        self.possible_letters = set(letter)


class WordState:
    def __init__(self, word_length: int = WORD_LENGTH):
        self.word_length = word_length
        self.state = [PositionState() for _ in range(self.word_length)]

    def update_state(self, guess_response: List[LetterGuess]):
        for position, guess in enumerate(guess_response):
            # update the knowledge about the position
            if guess.state == GuessState.CORRECT:
                self.state[position].set_letter(guess.letter)
            elif guess.state == GuessState.IN_WORD:
                self.state[position].remove_letter(guess.letter)
            elif guess.state == GuessState.NOT_IN_WORD:
                for letter_state in self.state:
                    letter_state.remove_letter(guess.letter)

    def get_possible_words(self, word_list: Iterable[str]) -> Set[str]:
        """Filter word_list to possible words given current information obtained from
        guesses."""

        pattern = re.compile(
            "".join(
                [
                    f"[{''.join([letter for letter in position.possible_letters])}]"
                    for position in self.state
                ]
            )
        )

        def _test_word(w: str) -> bool:
            for letter_state, letter in zip(self.state, w):
                if letter not in letter_state.possible_letters:
                    return False
            return True

        possible_words = set([word for word in word_list if _test_word(word)])
        return possible_words


class WordScorer:
    """Interface for classes that score words"""

    def update(self, wordle_bot: "WordleBot") -> None:
        """Update will be called whenever WordleBot knowledge changes"""
        pass

    def score_word(self, word: str):
        raise NotImplementedError


def generate_guess_response(guess_word: str, true_word: str) -> List[LetterGuess]:
    guess_response = []
    for true_letter, guess_letter in zip(true_word, guess_word):
        if guess_letter == true_letter:
            letter_response = GuessState.CORRECT
        elif guess_letter in set(true_word):
            letter_response = GuessState.IN_WORD
        else:
            letter_response = GuessState.NOT_IN_WORD
        guess_response.append(LetterGuess(letter=guess_letter, state=letter_response))
    return guess_response


class WordleBot:
    def __init__(self, word_to_freq: Dict[str, float], word_scorer: WordScorer):
        self.word_to_freq = word_to_freq
        self.word_scorer = word_scorer
        self.letter_state = {letter: LetterState.UNKNOWN for letter in ALPHABET}
        self.word_state = WordState()
        self.guess_idx: int = 0

        self.possible_words = set(word_to_freq.keys())

    def guess(self, guess_response: List[LetterGuess]) -> None:
        self.guess_idx += 1
        for position, guess in enumerate(guess_response):
            if position >= WORD_LENGTH:
                raise ValueError("Wrong length guess?")
            # update the knowledge about the alphabet
            if guess.state == GuessState.NOT_IN_WORD:
                self.letter_state[guess.letter] = LetterState.NOT_IN_WORD
            else:
                self.letter_state[guess.letter] = LetterState.IN_WORD

            self.word_state.update_state(guess_response)
        self._update_possible_words()

    @property
    def all_words(self) -> Set[str]:
        return set(self.word_to_freq.keys())

    def _update_possible_words(self):
        self.possible_words = self.word_state.get_possible_words(self.possible_words)

    def _score_words(self, word_list: Iterable[str]) -> List[Tuple[str, float]]:
        self.word_scorer.update(self)
        scored_words = [(word, self.word_scorer.score_word(word)) for word in word_list]
        scored_words.sort(reverse=True, key=lambda x: x[1])
        return scored_words

    def suggest(self) -> str:
        scored = self._score_words(self.all_words)
        word, score = scored[0]
        print(f"suggested word {word} has score {score}")
        return word

    def play_word(self, true_word) -> int:
        """play a fake game against 'true_word', and return the number of tries needed to win"""
        for guess_idx in range(6):
            guess_word = self.suggest()
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
                return guess_idx
            self.guess(guess_response=guess_response)

        print("Oh no! WordleBot failed!")
        return -1


class FrequencyWordScorer(WordScorer):
    def __init__(self):
        self.lidx_lookup = {letter: lidx for lidx, letter in enumerate(ALPHABET)}

    def _calc_frequency_table(self, possible_words) -> np.ndarray:
        print(f"There are {len(possible_words)} possible words")
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
        word_state = copy.deepcopy(wordle_bot.word_state)
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
        normalized_score = score / len(self.possible_words) ** 2
        sys.stdout.write(".")
        sys.stdout.flush()
        return normalized_score


if __name__ == "__main__":

    wordle_word_freq = pd.read_csv("wordle_word_freq.csv")
    word_to_freq = {
        word: freq
        for word, freq in zip(
            wordle_word_freq.word.values, wordle_word_freq["count"].values
        )
    }

    word_scorer = FrequencyWordScorer()
    wordle_bot = WordleBot(word_to_freq=word_to_freq, word_scorer=word_scorer)
    wordle_bot.play_word("elder")

    # word_scorer = BruteForceWordScorer()
    # wordle_bot = WordleBot(word_to_freq=word_to_freq, word_scorer=word_scorer)
    # scored_words = wordle_bot._score_words(wordle_bot.all_words)
    # print(scored_words[:10])
