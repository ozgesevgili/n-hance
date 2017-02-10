from pywsd.lesk import simple_lesk
from nltk import word_tokenize


def find_pun(sent):
    max_score_word = ""
    current_max = 0
    for word in word_tokenize(sent):
        synnets = simple_lesk(sent,
         word,
         nbest=True,
         keepscore=True
        )
        if synnets is None:
            continue
        #print word, synnets
        max_score = max([e[0] for e in synnets])
        if max_score >= current_max:
            current_max = max_score
            max_score_word = word
    if max_score == 2:
        return max_score_word
    return None

for line in open("../puns_small.txt"):
    sent = line.strip()
    print "Sent:", sent
    pun = find_pun(sent)
    print "Result:", pun if pun is not None else "No Pun!"
