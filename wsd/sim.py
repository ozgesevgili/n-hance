from nltk.corpus import wordnet
from nltk.corpus import wordnet_ic
from nltk.corpus import genesis

genesis_ic = wordnet.ic(genesis, False, 0.0)
brown_ic = wordnet_ic.ic('ic-brown.dat')
semcor_ic = wordnet_ic.ic('ic-semcor.dat')

inp = [["used", "banker"], ["lost", "interest"]]

for word1 in inp[0]:
    for word2 in inp[1]:
        s = []
        for syn1 in wordnet.synsets(word1):
            for syn2 in wordnet.synsets(word2):
                # result = syn1.path_similarity(syn2)
                # if result is not None:
                #     print "path", word1, word2, result

                # if syn1.name().split(".")[1] in ["a", "s"] or syn1.name().split(".")[1] != syn2.name().split(".")[1]:
                #     continue
                #
                # result = syn1.lch_similarity(syn2)
                # if result is not None:
                #     print "lch", word1, word2, result

                result = syn1.wup_similarity(syn2)
                if result is not None:
                    s.append(result)
        if len(s) > 0:
            print word1, word2, max(s)
                #
                # result = syn1.res_similarity(syn2, genesis_ic)
                # if result is not None:
                #     print "res", word1, word2, result
                #
                # result = syn1.jcn_similarity(syn2, genesis_ic)
                # if result is not None:
                #     print "jcn", word1, word2, result
                #
                # result = syn1.lin_similarity(syn2, semcor_ic)
                # if result is not None:
                #     print "lin", word1, word2, result
