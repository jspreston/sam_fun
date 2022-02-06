# COMMAND ----------
import itertools

import pandas as pd

# COMMAND ----------
wordle_word_freq = pd.read_csv("wordle_word_freq.csv").set_index("word")
wordle_word_freq
# COMMAND ----------
words = wordle_word.freq.index.values
chars = list(itertools.chain(*[set(word) for word in words]))