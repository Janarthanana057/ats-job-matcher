import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
from nltk.corpus import stopwords

def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    stop_words = set(stopwords.words('english'))
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return ' '.join(words)

def extract_keywords(text, top_n=20):
    vectorizer = TfidfVectorizer(max_features=top_n)
    vectorizer.fit([text])
    return list(vectorizer.vocabulary_.keys())

def match_resume(resume_text, jd_text):
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_clean, jd_clean])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]
    score_percent = round(score * 100, 2)

    jd_keywords = extract_keywords(jd_clean, top_n=25)
    resume_words = set(resume_clean.split())

    matched = [k for k in jd_keywords if k in resume_words]
    missing = [k for k in jd_keywords if k not in resume_words]

    return {
        "score": score_percent,
        "matched": matched,
        "missing": missing
    }