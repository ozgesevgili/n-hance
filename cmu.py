from nltk.corpus import cmudict

db = cmudict.dict()


# Remove stress
for key in db:
    for i in xrange(len(db[key])):
        for j in xrange(len(db[key][i])):
            sound = db[key][i][j].replace("0", "").replace("1", "").replace("2", "")
            db[key][i][j] = sound

#print db["propane"]

def lcs_length(a, b):
    table = [[0] * (len(b) + 1) for _ in xrange(len(a) + 1)]
    for i, ca in enumerate(a, 1):
        for j, cb in enumerate(b, 1):
            table[i][j] = (
                table[i - 1][j - 1] + 1 if ca == cb else
                max(table[i][j - 1], table[i - 1][j]))
    return table[-1][-1]

def is_same_pronunce(w1, w2):
    for p1 in db[w1]:
        for p2 in db[w2]:
            diff = set(p1) - set(p2)
            if len(diff) == 0 or len(diff) == 1:
                return True
    return False

def find_same_pronunce(word):
    ret = []
    for w in db:
        if is_same_pronunce(word, w):
            ret.append(w)
    return ret

print is_same_pronunce("propane", "profane")
print find_same_pronunce("propane")
