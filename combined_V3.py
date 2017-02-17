import xml.etree.ElementTree as ET
import nltk
import string
import gensim
import operator
import numpy as np
from nltk.corpus import stopwords
from pywsd.lesk import simple_lesk
from sklearn.metrics.pairwise import cosine_similarity


# takes path and returns list of sentences.
def read_data(path="/Users/ozge/Documents/semeval2017_pun_task/data/test/subtask3-homographic-test.xml"):
    result = list()

    tree = ET.parse(path)
    root = tree.getroot()

    for text in root:
        text_id = text.attrib['id']
        pun_id = None
        pun_word = None

        sentence = ''

        for word in text:
            if int(word.attrib['senses']) == 2:
                pun_id = word.attrib['id']
                pun_word = word.text

            sentence += ' ' + word.text

        # sentence, text id, pun word id, pun word
        result.append((sentence.strip(), text_id, pun_id, pun_word))

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

        except KeyError:
            continue

    # print pair_scores

    try:
        return sorted(pair_scores.items(), key=operator.itemgetter(1), reverse=True)[0], pair_scores
    except IndexError:
        return None, pair_scores

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

    if sense_list is not None or len(sense_list) != 1:
        sense = sense_list[0]
        if len(sense_list) > 1:
            other_sense, sim = find_most_similar_sense(word1, word2, sense_list)
            return (word2, sense.name(), other_sense)
        return (word2, sense.name(), sense.name())

    return None

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

    scores = load_pmi_scores("/Users/ozge/Desktop/score5000_combined.txt")
    print "scores are loaded.."

    model = gensim.models.Word2Vec.load_word2vec_format("/Users/ozge/Desktop/wiki.en.text128.vector", binary=False)
    print "model is loaded.."

    sentence_list = read_data()
    print "data is read.."

    subtask2_counter = 0
    not_guessed_pun = 0
    for sentence_info in sentence_list:
        sentence = sentence_info[0]
        text_id = sentence_info[1]
        pun_id = sentence_info[2]
        pun_word = sentence_info[3]

        print sentence
        pair_list = create_pair(sentence, stopwords.words("english"))
        #print pair_list

        max_pair_score, pair_scores = find_pair_scores(pair_list, scores)
        print "all pairs scores:", pair_scores
        print max_pair_score
        try:
            if max_pair_score[0][1] == pun_word:
                subtask2_counter += 1

            print pun_word, max_pair_score[0][1], subtask2_counter
        except:
            not_guessed_pun += 1
            continue

    print len(sentence_list)
    print  "not_quessed", not_guessed_pun

    # homographic subtask2: 560/1298
    # heterographic subtask2:
    '''
        try:
            print find_pun_word2vec(sentence, max_pair_score)
        except:
            continue
            '''
    '''
    #pair_list = create_pair(sentence2, stopwords.words("english"))
    # print pair_list

    #max_pair_score, pair_scores = find_pair_scores(pair_list, scores)
    #print max_pair_score

    # TODO: call find pun for two max pair,
    print find_pun_word2vec(sentence2, (('reeds', 'rushed'), 7.23744477842))
    '''
