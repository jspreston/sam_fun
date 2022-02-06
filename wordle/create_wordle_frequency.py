# create a reasonable list of wordle-valid words sorted by frequency
# COMMAND ----------
import pandas as pd
# COMMAND ----------
# read the word frequency list and the scrabble dictionary
word_freq = pd.read_csv("unigram_freq.csv").set_index("word")
word_freq
# COMMAND ----------
fname = "../scrabble/scrabble_words_2019.txt"
with open(fname) as fp:
    scrabble_words = [line.strip().lower() for line in fp]
scrabble_words

# COMMAND ----------
wordle_words = set([w for w in scrabble_words if len(w) == 5])
wordle_word_freq = word_freq[word_freq.index.isin(wordle_words)].reset_index()
wordle_word_freq.index.name = "rank"
wordle_word_freq = wordle_word_freq.reset_index().set_index("word")
wordle_word_freq

# COMMAND ----------
wordle_word_freq.to_csv("wordle_word_freq.csv")

# COMMAND ----------
wordle_archive = pd.read_csv("wordle_archive_words.csv")
wordle_archive
# COMMAND ----------
wordle_archive_words = set(wordle_archive.Word.apply(str.lower).values)
# COMMAND ----------
wordle_archive_freq = wordle_word_freq[wordle_word_freq.index.isin(wordle_archive_words)]
wordle_archive_freq
# COMMAND ----------
import matplotlib.pyplot as plt
import numpy as np
plt.hist(wordle_archive_freq["rank"].values, bins=20)
# COMMAND ----------
max(wordle_archive_freq["rank"].values)
# COMMAND ----------
