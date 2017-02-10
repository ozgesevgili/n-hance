import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import RegexpParser
from nltk.tag.stanford import NERTagger

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

    #Set of all stopwords in english dictionary
    stop_words = set(stopwords.words("english"))
    for t in tokens:
        for check in relevant:
            if t[1].startswith("CC") or t[1].startswith("RB"):
                t = ("XXX", ",") # XXX is not stop word
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
        if (len(tagged[i][1]) ==  1 and i != 0 and i != len(tagged) -1):
            sentences.append((tagged[:i], tagged[i+1:]))

    # if its only one clause
    if len(sentences) == 0:
        sentences = [tagged]

    return sentences


def main():
    from pprint import pprint
    for line in open("puns_small.txt"):
        pprint(extract_clause(line.strip()))
        print "---------------"

if __name__ == "__main__":
    main()
