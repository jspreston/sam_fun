import os
import re
import itertools
from typing import List
import argparse

# dictionary = "words_alpha.txt"
dictionary = "scrabble_words_2019.txt"

alphabet = "abcdefghijklmnopqrstuvwxyz"


with open(dictionary) as fp:
    text = fp.read().lower()

dict_set = set([word.strip() for word in text.split("\n")])


def merge_to_form(letters: str, form: str, letter_indices: List[int]):
    word = list(form)
    for letter_idx, letter in zip(letter_indices, letters):
        word[letter_idx] = letter
    return ''.join(word)


def expand_blanks(word: str):
    
    words_queue = [list(word)]
    while words_queue:
        word = words_queue.pop()
        if '.' not in word:
            yield ''.join(word)
        else:
            blank_idx = word.index('.')
            for letter in alphabet:
                new_word = list(word)
                new_word[blank_idx] = letter
                words_queue.append(new_word)
    

def matching_words(letters: str, form: str):
    """
    Given a set of letters (possibly including blanks ('.') and a
    "form" consisting of available letters and open positions ('_'),
    return valid scrabble words that can be played.
    """

    letter_indices = [idx for idx, char in enumerate(form) if char == "_"]
    num_letters = len(letter_indices)

    # we may not be using all the letters, get each possible subset of the right length
    letter_sets = set(itertools.combinations(letters, num_letters))
    # for each letter subset, get all permutations
    letter_permutations = list(itertools.chain(*[itertools.permutations(letter_set) for letter_set in letter_sets]))
    # for each permutation, merge it with the 'form' to get possible words
    possible_words = set([merge_to_form(letters, form, letter_indices) for letters in letter_permutations])
    # expand any blanks with all possible completions
    possible_words = set(itertools.chain(*[expand_blanks(word) for word in possible_words]))
    # find all valid words within possible words
    valid_words = list(dict_set.intersection(possible_words))
    return valid_words



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("letters", help="the list of letters in your hand ('.' for blank), e.g. 'hllomp.'")
    parser.add_argument("form", help="The spaces you'd like to fill with a word, including letters on the board.  For instance, 'b___ast' assumes the 'b' and 'ast' are on the board, with three spaces separating them.")
    args = parser.parse_args()
    words = matching_words(letters=args.letters, form=args.form)
    print(words)

