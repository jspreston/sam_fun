# Files

## data

- `unigram_frequency.csv`: English word frequency from kaggle
- `wordle_archive_words.csv`: Set of words selected by wordle in 2022
- `wordle_word_freq.csv`: Output set of likely wordle words and frequency, created by `create_wordle_frequency.py`.

## code

- `create_wordle_frequency.py`: used to create `wordle_word_freq.csv` by merging `unigram_frequency.csv` with the scrabble dictionary, and selecting only 5-letter words.
