from pywsd.lesk import simple_lesk
from pywsd.lesk import cosine_lesk
from pywsd.lesk import adapted_lesk
from pywsd.similarity import max_similarity
from nltk import word_tokenize
from nltk.wsd import lesk
from pprint import pprint

sense_list = simple_lesk("I used to be banker, I lost interest", "I", nbest=True)

def find_pun(sent):
    for word in word_tokenize(sent):
        sense_list = simple_lesk(
         sent,
         word,
         nbest=True
        )
        if sense_list is None or len(sense_list) == 1:
            continue

        sense_names = [e.name() for e in sense_list[:2]]
        for sense in sense_list[:1]:
            for lemma in sense.lemma_names():
                if lemma == word:
                    continue
                lemma_sense_list = simple_lesk(
                 sent.replace(word, lemma),
                 lemma,
                 nbest=True,
                )[0]

                lemma_sense_names = [e.name() for e in lemma_sense_list]

                inersect = [e for e in lemma_sense_names if e in sense_names]
                #print inersect
                if len(inersect) > 1:
                    print "Result:", word
                break

        print "----------"
    return None

for line in open("../puns_small.txt"):
    sent = line.strip()
    print "Sent:", sent
    pun = find_pun(sent)
    print "Result:", pun if pun is not None else "No Pun!"
