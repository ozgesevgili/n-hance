from chunk import extract_clause
from idf import IDF



if __name__ == "__main__":
    idfDB = IDF("stem.termid.idf.map.txt")
    for line in open("puns_small.txt"):
        clauses = extract_clause(line.strip())
        for clause in clauses:
            for tagged_list in clause:
                for word, tag in tagged_list:
                    if len(tag) > 1:
                        print word, idfDB.lookup(word, tag)
        print "---------------"
