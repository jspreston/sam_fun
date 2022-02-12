# Initial work on wordle automation
from typing import Dict, List, Set, Optional, Iterable, Tuple
from enum import Enum
from dataclasses import dataclass
import re

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


class WordScorer:
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
        self.word: List[PositionState] = [PositionState() for _ in range(WORD_LENGTH)]
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
            # update the knowledge about the position
            if guess.state == GuessState.CORRECT:
                self.word[position].set_letter(guess.letter)
            elif guess.state == GuessState.IN_WORD:
                self.word[position].remove_letter(guess.letter)
            elif guess.state == GuessState.NOT_IN_WORD:
                for state in self.word:
                    state.remove_letter(guess.letter)
        self._update_possible_words()

    @property
    def all_words(self) -> Set[str]:
        return set(self.word_to_freq.keys())

    def _update_possible_words(self):
        self.possible_words = self.get_possible_words(self.possible_words)

    def get_possible_words(self, word_list: Optional[Iterable[str]] = None) -> Set[str]:
        """Filter word_list to possible words given current information obtained from
        guesses.  If word_list is omitted, start from all possible words in the original
        frequency mapping."""
        if word_list is None:
            word_list = self.all_words

        pattern = re.compile(
            "".join(
                [
                    f"[{''.join([letter for letter in position.possible_letters])}]"
                    for position in self.word
                ]
            )
        )
        possible_words = set([word for word in word_list if pattern.match(word)])
        return possible_words

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
                letter_state = wordle_bot.word[lidx]
                if (
                    letter not in letter_state.possible_letters
                    or len(letter_state.possible_letters) == 1
                ):
                    self.letter_frequency[lidx, self.lidx_lookup[letter]] = 0
        print(self.letter_frequency)

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


if __name__ == "__main__":
    import pandas as pd

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
