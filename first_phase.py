import sense2vec
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
import operator
import xml.etree.ElementTree as ET
from nltk.corpus import stopwords

# path = '/Users/ozge/Downloads/semeval2017_pun_task/data/trial/subtask1-homographic-trial.xml'
# takes path and returns list of sentences.
def read_data(path):
    result = list()

    tree = ET.parse(path)
    root = tree.getroot()

    for text in root:
        sentence = ''

        for word in text:
            sentence += ' ' + word.text

        result.append(sentence.strip())

    return result

def match(word_tag):
    result = word_tag[0]
    result += "|VERB" if word_tag[1].startswith("VB") else "|NOUN"
    return result

# takes splitted list of values
# returns matched words.
def find_words(sentence):
    result = list()

    for word_tag in sentence:
        print word_tag
        if word_tag[1].startswith("N") or word_tag[1].startswith("VB"):
            result.append(match(word_tag))

    return result


def find_pair(sentence1, sentence2):
    similarities = {}
    for word in sentence1:
        for other_word in sentence2:
            freq, vector1 = model[unicode(word, "utf-8")]
            #print "word - freq", word, freq
            freq, vector2 = model[unicode(other_word, "utf-8")]
            #print "word - freq", other_word, freq

            similarities[(word, other_word)] = cosine_similarity(np.asarray(vector1).reshape(1, -1),
                                                               np.asarray(vector2).reshape(1, -1))

    return sorted(similarities.items(), key=operator.itemgetter(1), reverse=True)


model = sense2vec.load()

print read_data('/Users/ozge/Downloads/semeval2017_pun_task/data/trial/subtask1-homographic-trial.xml')


# test for find_pair(sentence1, sentence2)

sentence1 = find_words([('used', 'VBD'), ('banker', 'NN')])
sentence2 = find_words([('lost', 'VBD'), ('interest', 'NN')])


print find_pair(sentence1, sentence2)
