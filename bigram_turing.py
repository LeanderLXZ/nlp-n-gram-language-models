import re
from bigram import biGram

class biGramTuring(biGram):

    def __init__(self, unknown_ratio=0):
        
        # The ratio of unknown words
        self.UNKNOWN_RATIO = unknown_ratio
        
        # Read files
        self.word_list_en, words_en, word_counts_en = \
            self.replace_unknown_words(self.read_file('EN.txt'))
        self.word_list_fr, words_fr, word_counts_fr = \
            self.replace_unknown_words(self.read_file('FR.txt'))
        self.word_list_gr, words_gr, word_counts_gr = \
            self.replace_unknown_words(self.read_file('GR.txt'))
       
        # Get unique probabilities of each language
        self.unique_prob_en = \
            self.get_unique_prob(self.word_list_en, word_counts_en)
        self.unique_prob_fr = \
            self.get_unique_prob(self.word_list_fr, word_counts_fr)
        self.unique_prob_gr = \
            self.get_unique_prob(self.word_list_gr, word_counts_gr) 

        # Get bigram probabilities of each language
        self.bigram_prob_en, self.unknown_prob_en = self.get_bigram_prob(
            word_counts_en, *self.get_n_bigram(words_en, 2))
        self.bigram_prob_fr, self.unknown_prob_fr = self.get_bigram_prob(
            word_counts_fr, *self.get_n_bigram(words_fr, 2))
        self.bigram_prob_gr, self.unknown_prob_gr = self.get_bigram_prob(
            word_counts_gr, *self.get_n_bigram(words_gr, 2))

    def get_bigram_prob(self, word_counts, bigram_list, bigram_counts):
        counts_of_c = {}
        for _, count in bigram_counts.items():
            if count in counts_of_c:
                counts_of_c[count] += 1
            else:
                counts_of_c[count] = 1

        n_c_list = sorted(counts_of_c.items(), key=lambda x:x[0])
        # words with zero frequency
        unknown_prob = n_c_list[0][1] / len(bigram_list)
        
        # print(n_c_list[0][1], len(bigram_list), unknown_prob)

        for i in range(1, n_c_list[-1][0]):
            if i not in counts_of_c:
                counts_of_c[i] = 0
        n_c_list = sorted(counts_of_c.items(), key=lambda x:x[0])

        c_star, p_star = {}, {}
        for c, n_c in n_c_list:
            if (c >= len(n_c_list) - 1) or (n_c == 0):
                c_star[c] = 0
                p_star[c] = 0
            else:
                c_star[c] = (c + 1) * n_c_list[c + 1][1] / n_c
                p_star[c] = c_star[c] / len(bigram_list)

        k = 100
        bigram_prob = {}
        for bigram in bigram_list:
            if bigram_counts[bigram] < k:
                bigram_prob[bigram] = p_star[bigram_counts[bigram]]
            else:
                bigram_prob[bigram] = \
                    bigram_counts[bigram] / word_counts[bigram[0]]

        return bigram_prob, unknown_prob

    def predict(self, sentence):
        max_prob = 0
        language = 'EN'
        for bigram_prob, unknown_prob, lang in \
                [(self.bigram_prob_en, self.unknown_prob_en, 'EN'),
                 (self.bigram_prob_fr, self.unknown_prob_fr, 'FR'),
                 (self.bigram_prob_gr, self.unknown_prob_gr, 'GR')]:
            prob_sentence = 1
            for i in range(len(sentence)):
                if i < len(sentence) - 1:
                    bigram_i = (sentence[i], sentence[i+1])
                    # Test if the bigram is unseen for training set
                    if bigram_prob.get(bigram_i):
                        prob_sentence *= bigram_prob[bigram_i]
                    else:
                        # Unknown bigrams
                        prob_sentence *= unknown_prob
                        # prob_sentence *= 0.000001
            # Get the language with the highest probability
            if prob_sentence > max_prob:
                language = lang
                max_prob = prob_sentence
        return language

if __name__ == '__main__':
    biGramTuring().main()
