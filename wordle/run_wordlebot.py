from wordlebot import WordleBot, FrequencyWordScorer, FastBruteForceWordScorer
import pandas as pd


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
    wordle_bot.play_word("ultra")

    # word_scorer = FastBruteForceWordScorer(list(word_to_freq.keys()))
    # wordle_bot = WordleBot(word_to_freq=word_to_freq, word_scorer=word_scorer)
    # scored_words = wordle_bot._score_words(wordle_bot.all_words)
    # print(scored_words[:10])
