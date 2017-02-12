import nltk
from nltk.corpus import stopwords
import sense2vec
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pywsd.lesk import simple_lesk, adapted_lesk
from nltk.corpus import brown
from gensim.models import Word2Vec

'''
POS for sense2vec:
ADJ ADP ADV AUX CONJ DET INTJ NOUN NUM PART PRON PROPN PUNCT SCONJ SYM VERB X

NAMED ENTITIES for sense2vec:
NORP FACILITY ORG GPE LOC PRODUCT EVENT WORK_OF_ART LANGUAGE
'''

def filter(tokens):
    """
POS tag list:
CC	coordinating conjunction
CD	cardinal digit
DT	determiner
EX	existential there (like: "there is" ... think of it like "there exists")
FW	foreign word
IN	preposition/subordinating conjunction
JJ	adjective	'big'
JJR	adjective, comparative	'bigger'
JJS	adjective, superlative	'biggest'
LS	list marker	1)
MD	modal	could, will
NN	noun, singular 'desk'
NNS	noun plural	'desks'
NNP	proper noun, singular	'Harrison'
NNPS	proper noun, plural	'Americans'
PDT	predeterminer	'all the kids'
POS	possessive ending	parent's
PRP	personal pronoun	I, he, she
PRP$	possessive pronoun	my, his, hers
RB	adverb	very, silently,
RBR	adverb, comparative	better
RBS	adverb, superlative	best
RP	particle	give up
TO	to	go 'to' the store.
UH	interjection	errrrrrrrm
VB	verb, base form	take
VBD	verb, past tense	took
VBG	verb, gerund/present participle	taking
VBN	verb, past participle	taken
VBP	verb, sing. present, non-3d	take
VBZ	verb, 3rd person sing. present	takes
WDT	wh-determiner	which
WP	wh-pronoun	who, what
WP$	possessive wh-pronoun	whose
WRB	wh-abverb	where, when
    """
    ret = []
    relevant = ["JJ", "NN", "VB", "RB", "CC"]

    # Set of all stopwords in english dictionary
    stop_words = set(stopwords.words("english"))
    for t in tokens:
        for check in relevant:
            if t[1].startswith("CC") or t[1].startswith("RB"):
                t = ("XXX", ",")  # XXX is not stop word
            if (t[1].startswith(check) or len(t[1]) == 1) and \
                            t[0] not in stop_words:
                ret.append(t)
                break
    return ret

def extract_clause(text):
    tokens = nltk.word_tokenize(text.lower())

    tagged = nltk.pos_tag(tokens)
    tagged = filter(tagged)
    sentences = []
    for i in range(len(tagged)):
        # if tag is . , ! and etc. and also is not first or last tagged element
        # split with it
        if len(tagged[i][1]) ==  1 and i != 0 and i != len(tagged) -1:
            sentences.append(tagged[:i])
            sentences.append(tagged[i+1:])

    # if its only one clause
    if len(sentences) == 0:
        sentences = [tagged]

    return sentences

def match(word_tag):
    result = word_tag[0]
    tag = word_tag[1]

    if tag.startswith("VB"):
        result += "|VERB"
    elif tag.startswith("N"):
        result += "|NOUN"
    elif tag.startswith("J"):
        result += "|ADJ"
    else:
        return None

    #TODO: complete list

    return result

# takes splitted list of values
# returns matched words.
def find_words(sentence):
    result = list()
    print "find words", sentence
    for word_tag in sentence:
        print word_tag
        matched = match(word_tag)
        if matched != None:
            result.append(matched)

    return result

def create_pair(sentences):
    sentence1 = find_words(sentences[0])
    sentence2 = find_words(sentences[1])

    # list of pair tuple
    pair_list = list()

    for word in sentence1:
        for other_word in sentence2:
            pair_list.append((word, other_word))

    return pair_list

def find_most_similar_sense(word_tag1, word_tag2, senselist):
    word = word_tag1.split("|")[0]
    tag = word_tag1.split("|")[1]

    max = 0
    result_sense = ""

    for sense in senselist:
        #print sense.name()
        #print sense.definition()
        #print sense.lemma_names()

        for lemma in sense.lemma_names():
            if lemma == word:
                continue
            lemma_tag = lemma + "|" + tag

            try:
                freq, vector1 = model[unicode(word_tag2, "utf-8")]
                freq, vector2 = model[unicode(lemma_tag)]
            except:
                continue
            sim = cosine_similarity(np.asarray(vector1).reshape(1, -1), np.asarray(vector2).reshape(1, -1))

            if sim > max:
                result_sense = sense.name()
                max = sim

            break

    return (result_sense, max)


# assumption, second sentence has pun!
def find_pun(sent, pair_list, treshold=0.2):

    for pair in pair_list:
        word_tag1 = pair[0]
        word_tag2 = pair[1]

        freq, vector1 = model[unicode(word_tag1)]
        freq, vector2 = model[unicode(word_tag2)]

        first_sim = cosine_similarity(np.asarray(vector1).reshape(1, -1),
                                np.asarray(vector2).reshape(1, -1))

        print "before", pair, first_sim


        word = word_tag2.split("|")[0]
        sense_list = simple_lesk(
         sent,
         word,
         lemma=False,
         nbest=True
        )
        if sense_list is None or len(sense_list) == 1:
            continue


        for sense in sense_list[:1]:
            for lemma in sense.lemma_names():
                if lemma == word:
                    continue

                lemma_tag = lemma + '|' + word_tag2.split('|')[1]
                try:
                    freq, vector1 = model[unicode(lemma_tag)]
                    freq, vector2 = model[unicode(word_tag1)]
                except:
                    try:
                        brown_word2vec = Word2Vec(brown.sents(), size=128)
                        vector1 = brown_word2vec[lemma_tag]
                        vector2 = brown_word2vec[word_tag1]
                    except:
                        #TODO: try with new Word2vec
                        continue

                sim = cosine_similarity(np.asarray(vector1).reshape(1, -1),
                                                             np.asarray(vector2).reshape(1, -1))

                print word_tag1, lemma_tag, sim
                print "--------------------"
                # TODO: find max distance, not first one.
                if abs(first_sim - sim) > treshold:
                    other_sense, sim = find_most_similar_sense(word_tag2, word_tag1, sense_list)
                    return (pair, word_tag2, sense.name(), other_sense)
                break
    return None


if __name__ == "__main__":
    #sentence = "The bee got married, he found his honey."
    #sentence = "I used to be banker, I lost interest"
    #sentence = "Quick dive into those reeds! 'Tom rushed'"
    sentence = "Cinderella was thrown off the basketball team because she ran away from the ball."
    sentence = "Old swords never rust, they just lose their temper."

    sentences = extract_clause(sentence)
    print sentences

    pair_list = create_pair(sentences)
    print pair_list

    model = sense2vec.load()
    print find_pun(sentence, pair_list)

