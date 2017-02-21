import xml.etree.ElementTree as ET
import nltk
import string
import gensim
import operator
from nltk.corpus import stopwords


# takes path and returns list of sentences.
def read_data(path="/Users/ozge/Documents/semeval2017_pun_task/data/test/subtask3-heterographic-test.xml"):
    result = list()

    tree = ET.parse(path)
    root = tree.getroot()

    for text in root:
        text_id = text.attrib['id']
        pun_id = None
        pun_word = None
        word_id = {}

        sentence = ''

        for word in text:
            if int(word.attrib['senses']) == 2:
                pun_id = word.attrib['id']
                pun_word = word.text

            sentence += ' ' + word.text
            word_id[word.text.lower()] = word.attrib['id']

        # sentence, text id, pun word id, pun word
        result.append((sentence.strip(), text_id, pun_id, pun_word, word_id))

    return result

def read_actual_data(path="/Users/ozge/Documents/semeval2017_pun_task/data/test/subtask2-heterographic-test.xml"):
    result = list()

    tree = ET.parse(path)
    root = tree.getroot()

    for text in root:
        text_id = text.attrib['id']
        word_id = {}

        sentence = ''

        for word in text:
            sentence += ' ' + word.text
            word_id[word.text.lower()] = word.attrib['id']

        result.append((sentence.strip(), text_id, word_id))

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


if __name__ == "__main__":

    scores = load_pmi_scores("/Users/ozge/Desktop/score5000.hete.all.combined.txt")
    print "scores are loaded.."

    sentence_list = read_actual_data()
    print "actual data is read.."

    '''
    sentence_list = read_data()
    print "data is read.."'''

    answer_path = "/Users/ozge/Desktop/answers/heterographic/answer.subtask2.txt"
    file = open(answer_path, 'w')

    not_guessed_pun = 0
    for sentence_info in sentence_list:
        sentence = sentence_info[0]
        text_id = sentence_info[1]
        word_id = sentence_info[2]

        pair_list = create_pair(sentence, stopwords.words("english"))

        max_pair_score, pair_scores = find_pair_scores(pair_list, scores)

        try:
            prediction_word = max_pair_score[0][1]
            file.write(text_id + " " + word_id[prediction_word] + "\n")
        except:
            not_guessed_pun += 1

    '''
    subtask2_counter = 0
    not_guessed_pun = 0
    for sentence_info in sentence_list:
        sentence = sentence_info[0]
        text_id = sentence_info[1]
        pun_id = sentence_info[2]
        pun_word = sentence_info[3]
        word_id = sentence_info[4]

        print sentence
        pair_list = create_pair(sentence, stopwords.words("english"))
        #print pair_list

        max_pair_score, pair_scores = find_pair_scores(pair_list, scores)
        print "all pairs scores:", pair_scores
        print max_pair_score
        prediction_word = None

        try:
            prediction_word = max_pair_score[0][1]
            if prediction_word == pun_word:
                subtask2_counter += 1

            print pun_word, max_pair_score[0][1], subtask2_counter

        except:
            not_guessed_pun += 1
            continue

        try:
            file.write(text_id + " " + word_id[prediction_word] + "\n")
        except:
            print "key error", prediction_word
            not_guessed_pun += 1

    '''
    file.close()
    print len(sentence_list)
    print  "not_quessed", not_guessed_pun

    # homographic subtask2: 560/1298 not guessed: 5
    # heterographic subtask2: 710/1098 not guessed: 14