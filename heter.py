import xml.etree.ElementTree as ET
from nltk.corpus import cmudict, wordnet, brown
from gensim.models import Word2Vec
from collections import defaultdict
from nltk.corpus import stopwords
from fuzzy import nysiis

# init
db = cmudict.dict()

#brown_vec = Word2Vec(brown.sents())


def is_same_pronunce(w1, w2, ratio=0.7):
    from difflib import SequenceMatcher
    sm = SequenceMatcher(None, list(nysiis(w1)), list(nysiis(w2)))
    if sm.ratio() >= ratio:
        return True
    return False


def find_same_pronunce(word, ratio=0.55):
    ret = []
    for w in db:
        if word != w and is_same_pronunce(word, w, ratio):
            ret.append(w)
    return ret

print "hurried" in find_same_pronunce("harried", 0.8)

#
# def find_word_average_similarity(tokens, word):
#     s = []
#     for t in tokens:
#         if t == word:
#             continue
#         try:
#             s.append(brown_vec.similarity(t, word))
#         except KeyError:
#             pass
#     if len(s) == 0:
#         return 0
#     else:
#         return sum(s)/len(s)
#
# tree = ET.parse("../nlp/subtask1/data/test/subtask3-heterographic-test.xml")
#
# #Extend stopwords
# stop_words = set(stopwords.words("english"))
#
# word_freq = defaultdict(lambda: 0)
# for text in tree.getroot():
#     for word in text:
#         word_freq[word.text.lower()] += 1
#
# high_freq = set()
# for word in word_freq:
#     if word_freq[word] > 10:
#         high_freq.add(word)
# stop = stop_words | high_freq
#
#
# def main(threshold=0.4):
#     #for text in tree.getroot():
#     if 1:
#         text = tree.getroot()[4]
#         tokens = []
#         ids = []
#         for word in text:
#             if word.text.isalpha():
#                 tokens.append(word.text)
#                 ids.append(word.attrib['id'])
#         sentence = " ".join(tokens).strip()
#         print sentence
#         for token in tokens:
#             if token in stop:
#                 continue
#
#             base_similarity = find_word_average_similarity(tokens, token)
#             print token, base_similarity
#
#             # if base_similarity + threshold >= 0.9:
#             #     # Already good similarity, lower the expectation
#             #     base_similarity = 1 - 2 * threshold
#
#             same_pronunce = []
#             synsets = wordnet.synsets(token)
#             if len(synsets) == 1:
#                 synset = synsets[0]
#                 for lemma in synset.lemma_names():
#                     # We are expandig with lemmas so we use higher ratio
#                     for same in find_same_pronunce(lemma, ratio=0.8):
#                         same_pronunce.append(same)
#             else:
#                 # We are not expending so using lower ratio
#                 for same in find_same_pronunce(token, ratio=0.8):
#                     same_pronunce.append(same)
#             for same in same_pronunce:
#                 similarity = find_word_average_similarity([e for e in tokens if e != token], same)
#                 if similarity > threshold:
#                     print token, same, similarity #- base_similarity
#         return
# main()
