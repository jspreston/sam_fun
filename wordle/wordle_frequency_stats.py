# COMMAND ----------
import itertools
import collections

import pandas as pd
import matplotlib.pyplot as plt

# COMMAND ----------
wordle_word_freq = pd.read_csv("wordle_word_freq.csv").set_index("word")
wordle_word_freq

# COMMAND ----------
words = wordle_word_freq.index.values
chars = list(itertools.chain(*[set(word) for word in words]))
char_freq = collections.Counter(chars)
# COMMAND ----------
chars, counts = zip(*char_freq.most_common())
plt.bar(chars, counts)

# COMMAND ----------
