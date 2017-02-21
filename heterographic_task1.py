import xml.etree.ElementTree as ET
import nltk
import string
import operator
from nltk.corpus import stopwords
import numpy as np
import random

# takes path and returns list of sentences.
def read_data(path="/Users/ozge/Documents/semeval2017_pun_task/data/test/subtask1-heterographic-test.xml"):
    result = list()

    tree = ET.parse(path)
    root = tree.getroot()

    for text in root:
        text_id = text.attrib['id']

        sentence = ''

        for word in text:
            sentence += ' ' + word.text

        # sentence, text id, pun word id, pun word
        result.append((sentence.strip(), text_id))

    return result


# takes two paths and according to overlap, assign puns or not puns.
def count_puns(path1="/Users/ozge/Documents/semeval2017_pun_task/data/test/subtask1-heterographic-test.xml",
               path2="/Users/ozge/Documents/semeval2017_pun_task/data/test/subtask2-heterographic-test.xml"):
    # sentence ids which have pun.
    sentence_ids = list()

    tree1 = ET.parse(path1)
    root1 = tree1.getroot()

    tree2 = ET.parse(path2)
    root2 = tree2.getroot()

    text_ids1 = list()
    for text in root1:
        text_ids1.append(text.attrib['id'])

    for text in root2:
        text_id = text.attrib['id']
        if text_id in text_ids1:
            sentence_ids.append(text_id)

    return sentence_ids


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


def write_scores(text_id, scores, path="/Users/ozge/Desktop/sorted.scores_heterographic.txt"):
    file = open(path, 'a')

    values = str(text_id) + ":"
    for score in scores:
        values += str(score) + " "

    values += '\n'
    file.write(values)
    file.close()


def does_contain_pun(text_id, pair_scores, treshold=0.1):
    prediction = False
    sorted_pair_scores = sorted(pair_scores.items(), key=operator.itemgetter(1), reverse=True)
    print sorted_pair_scores

    scores = pair_scores.values()
    sorted_scores = sorted(scores, reverse=True)
    #write_scores(text_id, sorted_scores)

    diff = sorted_scores[0] - sorted_scores[-1]
    # TODO: normalization and  then apply quartile
    if diff > treshold:
        prediction = True

    return prediction


if __name__ == "__main__":

    scores = load_pmi_scores("/Users/ozge/Desktop/score5000.hete.all.combined.txt")
    print "scores are loaded.."

    sentence_list = read_data()
    print "data is read.."

    pun_ids = count_puns()
    print  "text_ids which contain pun are taken.."

    subtask1_true_positive_counter = 0
    subtask1_true_negative_counter = 0
    subtask1_false_positive_counter = 0
    subtask1_false_negative_counter = 0

    answer_path = "/Users/ozge/Desktop/answers/heterographic/answer.subtask1_fixed.txt"
    file = open(answer_path, 'w')
    counter = 0
    for sentence_info in sentence_list:
        sentence = sentence_info[0]
        text_id = sentence_info[1]

        print sentence
        pair_list = create_pair(sentence, stopwords.words("english"))
        # print pair_list

        try:
            max_pair_score, pair_scores = find_pair_scores(pair_list, scores)
            print max_pair_score

            predicted = 1 if does_contain_pun(text_id, pair_scores, 2.940) else 0

            file.write(text_id + " " + str(predicted) + "\n")

            '''
            truth = True if text_id in pun_ids else False

            if predicted and truth:
                subtask1_true_positive_counter += 1
            elif predicted and not truth:
                subtask1_true_negative_counter += 1
            elif not predicted and truth:
                subtask1_false_positive_counter += 1
            elif not predicted and not truth:
                subtask1_false_negative_counter += 1
            else:
                continue
            '''

        except:
            print "excepted"

            predicted = 1 if random.choice([True, False]) else 0

            file.write(text_id + " " + str(predicted) + "\n")
            counter += 1
            continue

    print "true positive", subtask1_true_positive_counter
    print "true negative", subtask1_true_negative_counter
    print "false positive", subtask1_false_positive_counter
    print "false negative", subtask1_false_negative_counter

    file.close()
    print counter
    print len(sentence_list)
    '''

    sentence1 = "I used to be banker, I lost interest"
    sentence = "Cinderella was thrown off the basketball team because she ran away from the ball."
    sentence = "I'm dying, Tom croaked."
    sentence = "Old swords never rust, they just lose their temper."
    sentence3 = "My father slept under the bed, I think he was a little potty."
    sentence2 = "Quick, dive into those reeds! 'Tom rushed'"
    sentence = "The bee got married, he found his honey."
    sentence = "My bakery burned down last night, and now my business is toast."
    sentence = "An optometrist fell into a lens grinder and made a spectacle of himself."
    sentence = "A horse is a very stable animal."

    pair_list = create_pair(sentence, stopwords.words("english"))
    # print pair_list

    max_pair_score, pair_scores = find_pair_scores(pair_list, scores)
    print max_pair_score

    does_contain_pun("hom_1", pair_scores)'''
