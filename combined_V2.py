import nltk
from nltk.corpus import stopwords
import sense2vec
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pywsd.lesk import simple_lesk
from nltk.corpus import brown
from gensim.models import Word2Vec
import gensim
import string
import operator
import xml.etree.ElementTree as ET

# takes path and returns list of sentences.
def read_data(path="/Users/ozge/Documents/semeval2017_pun_task/data/test/subtask3-homographic-test.xml"):
    result = list()

    tree = ET.parse(path)
    root = tree.getroot()

    for text in root:
        sentence = ''

        for word in text:
            sentence += ' ' + word.text

        result.append(sentence.strip())

    return result

def create_pair(sentences, stop_words):
    tokens = nltk.word_tokenize(sentences.lower())
    tokens_filtered = list()
    punctuations = list(string.punctuation)

    # remove stopwords
    for word in tokens:
        if word not in stop_words and word not in punctuations:
            tokens_filtered.append(word)

    # list of pair tuple
    pair_list = list()

    for word in tokens_filtered:
        for other_word in tokens_filtered[tokens_filtered.index(word) + 1:]:
            pair_list.append((word, other_word))

    return pair_list


def load_pmi_scores(path):
    lines = open(path).readlines()
    pair_pmi = {}

    for line in lines:
        pair = line.split(":")[0]
        word1 = pair.split(",")[0]
        word2 = pair.split(",")[1]
        score_ = line.split(":")[1]
        score = float(score_[:len(score_) - 1])
        pair_pmi[(word1, word2)] = score

    return pair_pmi

def find_pair_scores(pair_list, scores):
    pair_scores = {}

    for pair in pair_list:
        word1 = pair[0].encode('ascii', 'ignore')
        word2 = pair[1].encode('ascii', 'ignore')

        try:
            pair_scores[(word1, word2)] = scores[(word1, word2)]
            if word1 == 'horse' and word2 == 'static':
                print "YEYYYYSYSYVNFENVF"
                break
            if word1 == 'horse' and word2 == 'unchanging':
                print "YEYYYYSYSYVNFENVF"
                break
        except KeyError:
            continue

    # print pair_scores

    try:
        return sorted(pair_scores.items(), key=operator.itemgetter(1), reverse=True)[0], pair_scores
    except IndexError:
        return None, pair_scores

def find_pun(sent, pair_scores, scores):
    word1 = pair_scores[0][0]
    word2 = pair_scores[0][1]
    first_score = pair_scores[1]
    # initialization
    second_score = None
    third_score = None
    candidate_lemma1 = None
    candidate_lemma2 = None
    candidate_sense1 = None
    candidate_sense2 = None

    print "word1, word2, first_score", word1, word2, first_score

    sense_list1 = simple_lesk(sent, word1, lemma=False, nbest=True)
    print "sense_list1", sense_list1

    if sense_list1 is not None or len(sense_list1) != 1:

        # discuss about it.
        for sense in sense_list1[:1]:
            for lemma in sense.lemma_names():

                if lemma == word1:
                    continue
                print "sense:lemma", sense, lemma
                try:
                    candidate_lemma1 = lemma
                    candidate_sense1 = sense
                    second_score = scores[(lemma, word2)]
                    print "second_score", second_score
                    # discuss about it.
                    break
                except KeyError:
                    continue

    sense_list2 = simple_lesk(sent, word2, lemma=False, nbest=True)

    print "sense_list2", sense_list2
    if sense_list2 is not None or len(sense_list2) != 1:

        # discuss about it.
        for sense in sense_list2[:1]:

            for lemma in sense.lemma_names():

                if lemma == word2:
                    continue

                print "sense - lemma", sense, lemma
                try:
                    candidate_sense2 = sense
                    candidate_lemma2 = lemma
                    third_score = scores[(word1, lemma)]
                    print "third_score", third_score
                    break
                except KeyError:
                    continue

    if second_score is None and third_score is None:
        return None

    # which word is pun, which sense is used in sent., which lemma is mixed.
    result1 = (word2, candidate_sense1, candidate_lemma1)
    result2 = (word1, candidate_sense2, candidate_lemma2)

    if second_score is not None and third_score is None:
        return result1

    elif second_score is None and third_score is not None:
        return result2

    diff1 = abs(first_score - second_score)
    diff2 = abs(first_score - third_score)

    print "diff1:", diff1, "diff2:", diff2
    if diff1 > diff2:
        return result1

    return result2


if __name__ == "__main__":

    sentence1 = "I used to be banker, I lost interest"
    sentence = "Cinderella was thrown off the basketball team because she ran away from the ball."
    #sentence = "OLD PILOTS never die, they just more turbulent."
    sentence = "I'm dying, Tom croaked."
    sentence = "Old swords never rust, they just lose their temper."
    sentence3 = "My father slept under the bed, I think he was a little potty."
    sentence2 = "Quick, dive into those reeds! 'Tom rushed'"
    sentence = "The bee got married, he found his honey."
    sentence = "My bakery burned down last night, and now my business is toast."
    sentence = "An optometrist fell into a lens grinder and made a spectacle of himself."
    sentence = "A horse is a very stable animal."

    sentence_list = read_data()
    scores = load_pmi_scores("/Users/ozge/Desktop/score5000_combined.txt")

    for sentence in sentence_list:
        print sentence
        pair_list = create_pair(sentence, stopwords.words("english"))
        #print pair_list

        max_pair_score, pair_scores = find_pair_scores(pair_list, scores)
        print max_pair_score

    '''
    pair_list = create_pair(sentence2, stopwords.words("english"))
    # print pair_list

    scores = load_pmi_scores("/Users/ozge/Desktop/score5000_combined.txt")
    max_pair_score, pair_scores = find_pair_scores(pair_list, scores)
    print max_pair_score

    # TODO: call find pun for two max pair
    print find_pun(sentence, max_pair_score, scores)
    '''

