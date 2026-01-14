# receipts_mvp.py
import re, math, hashlib
from collections import Counter
from difflib import SequenceMatcher

def normalize(txt):
    txt = txt.lower()
    txt = re.sub(r'https?://\S+|www\.\S+', '', txt)
    txt = re.sub(r'[\s]+', ' ', txt).strip()
    return txt

def shingles(text, k=5):
    return { text[i:i+k] for i in range(max(0, len(text)-k+1)) }

def jaccard(a, b):
    inter = len(a & b)
    union = len(a | b)
    return inter/union if union else 0.0

def simhash(tokens, bits=64):
    v = [0]*bits
    for t in tokens:
        h = int(hashlib.md5(t.encode()).hexdigest(), 16)
        for i in range(bits):
            v[i] += 1 if (h >> i) & 1 else -1
    fingerprint = 0
    for i, val in enumerate(v):
        if val >= 0:
            fingerprint |= (1 << i)
    return fingerprint

def hamming(x, y):
    return bin(x ^ y).count('1')

def stylometry_vector(txt):
    sents = re.split(r'[.!?]+', txt)
    sents = [s.strip() for s in sents if s.strip()]
    avg_len = sum(len(s.split()) for s in sents)/len(sents) if sents else 0
    commas = txt.count(',')
    excls = txt.count('!')
    colons = txt.count(':')
    return [avg_len, commas, excls, colons]

def cosine(u, v):
    num = sum(a*b for a,b in zip(u,v))
    den = math.sqrt(sum(a*a for a in u))*math.sqrt(sum(b*b for b in v))
    return num/den if den else 0.0

def compare(source, suspect):
    s = normalize(source)
    t = normalize(suspect)

    # overlap
    j = jaccard(shingles(s), shingles(t))

    # style
    style = cosine(stylometry_vector(s), stylometry_vector(t))

    # fuzzy token sim via SequenceMatcher (proxy for semantics in MVP)
    sem = SequenceMatcher(None, s, t).ratio()

    final = 0.45*sem + 0.35*j + 0.20*style

    # simhash on word 3-grams
    def word_ngrams(x, n=3):
        w = x.split()
        return [' '.join(w[i:i+n]) for i in range(max(0, len(w)-n+1))]
    h1 = simhash(word_ngrams(s))
    h2 = simhash(word_ngrams(t))
    ham = hamming(h1, h2)  # lower is closer

    return {
        "overlap": round(j, 3),
        "semantic_proxy": round(sem, 3),
        "style": round(style, 3),
        "simhash_hamming": ham,
        "final_score": round(final, 3)
    }

if __name__ == "__main__":
    src = """<paste original post text here>"""
    sus = """<paste suspected copy text here>"""
    print(compare(src, sus))
