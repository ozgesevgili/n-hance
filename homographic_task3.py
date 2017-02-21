import xml.etree.ElementTree as ET
import gensim
from pywsd.lesk import simple_lesk
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
import string
import operator
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn

# takes path and returns list of sentences.
def read_data(path="/Users/ozge/Documents/semeval2017_pun_task/data/test/subtask3-homographic-test.xml"):
    result = list()

    tree = ET.parse(path)
    root = tree.getroot()

    for text in root:
        text_id = text.attrib['id']
        pun_word = None
        pun_id = None

        sentence = ''

        for word in text:
            if int(word.attrib['senses']) == 2:
                pun_word = word.text
                pun_id = word.attrib['id']

            sentence += ' ' + word.text

        # sentence, text id, pun word id, pun word
        result.append((sentence.strip(), text_id, pun_word, pun_id))

    return result

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

def create_pair(sentences, stop_words):
    tokens = nltk.word_tokenize(sentences.lower())
    tokens_filtered = list()
    punctuations = list(string.punctuation)

    # remove punctuation
    for word in tokens:
        if len(word) > 2 and word not in stop_words and word not in punctuations:
            tokens_filtered.append(word)

    # list of pair tuple
    pair_list = list()

    for word in tokens_filtered:
        for other_word in tokens_filtered[tokens_filtered.index(word) + 1:]:
            pair_list.append((word, other_word))

    return pair_list

def find_pair_scores(pair_list, scores):
    pair_scores = {}

    for pair in pair_list:
        word1 = pair[0].encode('ascii', 'ignore')
        word2 = pair[1].encode('ascii', 'ignore')

        try:
            pair_scores[(word1, word2)] = scores[(word1, word2)]

        except KeyError:
            continue

    # print pair_scores
    return pair_scores

def find_most_similar_sense(word1, word2, senselist):

    max = 0
    result_sense = None

    for sense in senselist[1:]:

        for lemma in sense.lemma_names():
            if lemma == word2:
                continue

            try:
                vector1 = model[word1]
                vector2 = model[lemma]
                sim = cosine_similarity(np.asarray(vector1).reshape(1, -1), np.asarray(vector2).reshape(1, -1))
            except:
                continue


            if sim > max:
                result_sense = sense.name()
                max = sim

            break

    return (result_sense, max)

def find_pun_word2vec(sent, pair_scores):
    word1 = pair_scores[0][0]
    word2 = pair_scores[0][1]

    sense_list = simple_lesk(sent, word2, lemma=False, nbest=True)
    #print "sense_list1", sense_list

    counter = 0

    if sense_list is not None or len(sense_list) != 1:
        sense = sense_list[0]
        if len(sense_list) > 1:
            other_sense, sim = find_most_similar_sense(word1, word2, sense_list)
            # TODO: fix it
            if other_sense is None:
                other_sense = sense.name()
            return (word2, sense.name(), other_sense)
        return (word2, sense.name(), sense.name())

    return None

def find_max_pair_with_pun(pair_scores, pun):
    max_value = None
    max_pair = None
    all_scores = []

    for pair in pair_scores.keys():
        if pun in pair:
            all_scores.append((pair, pair_scores[pair]))

        score = pair_scores[pair]
        if max_value == None or score > max_value:
            if pun == pair[1]:
                max_pair = pair
                max_value = score
            elif pun == pair[0]:
                max_pair = (pair[1], pun)
                max_value = score

    return (max_pair, max_value), all_scores

if __name__ == "__main__":

    sentence_list = read_data()
    print "actual data is read.."

    model = gensim.models.Word2Vec.load_word2vec_format("/Users/ozge/Desktop/wiki.en.text128.vector", binary=False)
    print "model is loaded.."

    scores = load_pmi_scores("/Users/ozge/Desktop/score5000.homo.all.combined.txt")
    print "scores are loaded.."

    answer_path = "/Users/ozge/Desktop/answers/homographic/answer.subtask3_fixed.txt"
    file = open(answer_path, 'w')
    '''
    # sample data ----------
    sentence = "If you send a letter to the Philippines put it in a Manila envelope ."
    pun_word = "high"


    pair_scores = {('giraffes', 'good'): 3.93207496619, ('good', 'maintenance'): 0.0928711780931, ('good', 'pets'): 1.6652884255, ('pets', 'maintenance'): 4.49053192195, ('pets', 'high'): 1.65996482152, ('high', 'maintenance'): 1.409475669, ('giraffes', 'high'): 3.34178886149, ('good', 'high'): 0.458701290468, ('giraffes', 'pets'): 9.32973571004, ('giraffes', 'maintenance'): 6.75731846264}
    max_pair_score, all_scores = find_max_pair_with_pun(pair_scores, pun_word)

    #sample_pair_

    print max_pair_score


    print find_pun_word2vec(sentence, max_pair_score)
    # ----------------------
    '''
    counter = 0
    for sentence_info in sentence_list:
        sentence = sentence_info[0]
        text_id = sentence_info[1]
        pun_word = sentence_info[2].lower()
        pun_id = sentence_info[3]

        pair_list = create_pair(sentence, stopwords.words("english"))
        pair_scores = find_pair_scores(pair_list, scores)
        max_pair_score, all_scores = find_max_pair_with_pun(pair_scores, pun_word)

        print sentence
        print pair_scores
        print max_pair_score

        try:
            pun_senses = find_pun_word2vec(sentence, max_pair_score)
            '''if pun_senses[2] == None and len(all_scores) > 1:
                for scores in all_scores:
                    if max_pair_score == scores:
                        continue
                    pun_senses = find_pun_word2vec(sentence, scores)
                    if pun_senses[2] is not None:
                        break'''
            print pun_senses

            if pun_senses[2] is not None:
                s1 = wn.synset(pun_senses[1])
                s2 = wn.synset(pun_senses[2])
                file.write(pun_id + ' ' + str(s1.lemmas()[0]._key) + ' ' + str(s2.lemmas()[0]._key) + '\n')

        except:
            print "not found"
            counter += 1
            continue

    print counter

