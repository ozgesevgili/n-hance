from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import PorterStemmer, LancasterStemmer, SnowballStemmer

class IDF:
    def __init__(self, filename):
        self.map = {}
        self.wnl = WordNetLemmatizer()
        self.ls = LancasterStemmer()
        self.ps = PorterStemmer()
        self.sb = SnowballStemmer("english")
        for line in open(filename):
            sec = line.strip().split()
            self.map[sec[0]] = float(sec[2])

    def lookup(self, word, tag=""):
        if word in self.map:
            return self.map[word]

        if tag.startswith("VB"):
            w = self.wnl.lemmatize(word, 'v')
            if w in self.map:
                return self.map[w]

        # Look up after Lancaster Stemmer
        w = self.ls.stem(word)
        if w in self.map:
            return self.map[w]

        # Look up after Porter stemmer
        w = self.ps.stem(word)
        if w in self.map:
            return self.map[w]

        # Look up after Snowball stemmer
        w = self.sb.stem(word)
        if w in self.map:
            return self.map[w]

        WordNetLemmatizer().lemmatize(word,'v')
        # Give up
        return None
