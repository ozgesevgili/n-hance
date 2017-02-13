import xml.etree.ElementTree as ET
from nltk.corpus import cmudict, wordnet, brown
from gensim.models import Word2Vec
# init
db = cmudict.dict()
for key in db:
    for i in xrange(len(db[key])):
        for j in xrange(len(db[key][i])):
            db[key][i][j] = db[key][i][j].replace("0", "").replace("1", "").replace("2", "")

brown_vec = Word2Vec(brown.sents())

def is_same_pronunce(w1, w2, ratio=0.55):
    from difflib import SequenceMatcher
    try:
        for p1 in db[w1]:
            for p2 in db[w2]:
                sm = SequenceMatcher(None, p1, p2)
                if sm.ratio() >= ratio:
                    return True
    except KeyError:
        pass
    return False


def find_same_pronunce(word, ratio=0.55):
    ret = []
    for w in db:
        if word != w and is_same_pronunce(word, w, ratio):
            ret.append(w)
    return ret


def find_word_average_similarity(tokens, word):
    s = []
    for t in tokens:
        if t == word:
            continue
        try:
            s.append(brown_vec.similarity(t, word))
        except KeyError:
            pass
    if len(s) == 0:
        return 0
    else:
        return sum(s)/len(s)

tree = ET.parse("data/test/subtask1-heterographic-test.xml")
root = tree.getroot()
threshold = 0.4

for text in root:
    tokens = []
    ids = []
    for word in text:
        tokens.append(word.text)
        ids.append(word.attrib['id'])
    sentence = " ".join(tokens).strip()
    print sentence
    for token in tokens:
        if not token.isalpha():
            continue

        base_similarity = find_word_average_similarity(tokens, token)
        if base_similarity + threshold >= 0.9:
            # Already good similarity, lower the expectation
            base_similarity = 1 - 2 * threshold

        same_pronunce = []
        synsets = wordnet.synsets(token)
        if len(synsets) == 1:
            synset = synsets[0]
            for lemma in synset.lemma_names():
                # We are expandig with lemmas so we use higher ratio
                for same in find_same_pronunce(lemma, ratio=0.85):
                    same_pronunce.append(same)
        else:
            # We are not expending so using lower ratio
            for same in find_same_pronunce(token, ratio=0.70):
                same_pronunce.append(same)

        for same in same_pronunce:
            similarity = find_word_average_similarity([e for e in tokens if e != token], same)
            if similarity - base_similarity > threshold:
                print token, same, similarity - base_similarity
