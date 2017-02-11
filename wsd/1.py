from pywsd.lesk import simple_lesk
from pywsd.lesk import cosine_lesk
from pywsd.lesk import adapted_lesk
from pywsd.similarity import max_similarity
from nltk import word_tokenize
from pprint import pprint

def find_pun(sent):
    max_score_word = ""
    for word in word_tokenize(sent):
        sense_list = simple_lesk(
         sent,
         word,
         nbest=True
        )
        if sense_list is None or len(sense_list) == 1:
            continue

        print word

        sense_names = [e.name() for e in sense_list[:2]]
        for sense in sense_list[:2]:
            for lemma in sense.lemma_names():
                if lemma == word:
                    continue
                lemma_sense_list = simple_lesk(
                 sent.replace(word, lemma),
                 word,
                 nbest=True,
                )
                if len(lemma_sense_list) < 2:
                    break
                lemma_sense_names = [e.name() for e in lemma_sense_list]

                inersect = [e for e in lemma_sense_list if e in sense_list]
                #print inersect
                if len(inersect) == 1:
                    print "Result:", word
                break

        print "----------"
    return None

for line in open("../puns_small.txt"):
    sent = line.strip()
    print "Sent:", sent
    pun = find_pun(sent)
    print "Result:", pun if pun is not None else "No Pun!"
