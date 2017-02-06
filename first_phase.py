import sense2vec
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
import operator

# takes splitted list of values
# returns matched words.
def find_words(sentence):
    result = list()
    print nltk.pos_tag(sentence)

    for pair in nltk.pos_tag(sentence):
        if pair[1].startswith("N"):
            result.append(pair[0] + "|NOUN")
        elif  pair[1].startswith("VB"):
            result.append(pair[0] + "|VERB")

    return result


def find_pair(words):
    similarities = {}
    for i in range(len(words)):
        for word in words[i+1:]:
            key = words[i]
            freq, query_vector1 = model[unicode(key, "utf-8")]

            key1 = word
            freq, query_vector2 = model[unicode(key1, "utf-8")]
            similarities[(words[i], word)] = cosine_similarity(np.asarray(query_vector1).reshape(1,-1), np.asarray(query_vector2).reshape(1,-1))

    return sorted(similarities.items(), key=operator.itemgetter(1), reverse=True)

model = sense2vec.load()
words = find_words("I used to be a banker, I lost interest.".split())
print words
print find_pair(words)