import nltk
from nltk.corpus import stopwords, wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# =========================
# DOWNLOAD NLTK DATA (SAFE CHECK)
# =========================
try:
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords", quiet=True)

try:
    wordnet.synsets("test")
except LookupError:
    nltk.download("wordnet", quiet=True)

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
# =========================
# STOPWORDS
# =========================
# STOPWORDS
# =========================
BASE_STOPWORDS = set(stopwords.words("english"))

CUSTOM_STOPWORDS = {
    "candidate", "candidates", "preferred", "required", "efficient",
    "job", "role", "responsibilities", "skills", "knowledge",
    "experience", "understanding", "ability", "looking", "seeking",
    "fresher", "years", "plus", "basic", "strong"
}

STOP_WORDS = BASE_STOPWORDS.union(CUSTOM_STOPWORDS)

# =========================
# SYNONYM MAP
# =========================
SYNONYM_MAP = {
    "github": "git",
    "debugging": "debug",
    "debug": "debug",
    "js": "javascript",
    "ecmascript": "javascript",
    "node": "nodejs",
    "oop": "object oriented programming",
    "oops": "object oriented programming",
    "mysql": "sql",
    "postgresql": "sql",
    "sqlite": "sql",
    "communication skills": "communication",
    "team collaboration": "teamwork",
    "rest api": "api",
    "backend api": "api"
}

# =========================
# TECH KEYWORDS
# =========================
TECH_KEYWORDS = {
    "python", "java", "javascript", "sql", "html", "css",
    "flask", "django", "fastapi", "react", "nodejs",
    "git", "github", "docker", "kubernetes", "aws",
    "azure", "gcp", "linux", "rest", "api", "rest api",
    "machine learning", "deep learning", "nlp", "opencv",
    "tensorflow", "pytorch", "scikit-learn", "pandas",
    "numpy", "matplotlib", "streamlit", "firebase",
    "mongodb", "postgresql", "mysql", "data analysis",
    "data structures", "algorithms", "oop",
    "problem solving", "communication", "teamwork",
    "leadership", "backend", "frontend"
}

# =========================
# ROLE-BASED WEIGHTS
# =========================
def get_role_weights(jd_text):
    jd_lower = jd_text.lower()

    weights = {
        "python": 3,
        "sql": 3,
        "javascript": 3,
        "api": 3,
        "git": 2,
        "html": 2,
        "css": 2,
        "flask": 2,
        "django": 2,
        "react": 2,
        "problem solving": 2,
        "communication": 2,
        "teamwork": 2
    }

    # Backend / Python
    if "python" in jd_lower or "backend" in jd_lower:
        weights.update({
            "python": 5,
            "flask": 4,
            "django": 4,
            "fastapi": 4,
            "api": 5,
            "sql": 4
        })

    # Frontend
    if "frontend" in jd_lower or "react" in jd_lower:
        weights.update({
            "javascript": 5,
            "react": 5,
            "html": 4,
            "css": 4
        })

    # Data
    if "data" in jd_lower or "machine learning" in jd_lower:
        weights.update({
            "python": 5,
            "pandas": 5,
            "numpy": 5,
            "sql": 4
        })

    return weights

# =========================
# CLEAN TEXT
# =========================
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# =========================
# NORMALIZE KEYWORD
# =========================
def normalize_keyword(word):
    return SYNONYM_MAP.get(word.lower(), word.lower())

# =========================
# SYNONYMS
# =========================
def get_synonyms(word):
    synonyms = set()

    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonym = lemma.name().replace("_", " ").lower()
            synonyms.add(synonym)

    return synonyms

# =========================
# DISABLED SPACY SAFE MODE
# =========================
def extract_spacy_keywords(text):
    return set()

# =========================
# EXTRACT TECH KEYWORDS
# =========================
def extract_tech_keywords(text):
    text_lower = clean_text(text)
    found = set()

    for keyword in TECH_KEYWORDS:
        if keyword in text_lower:
            found.add(normalize_keyword(keyword))

    return found

# =========================
# WEIGHTED SCORE
# =========================
def calculate_weighted_score(matched, jd_keywords, weights):
    matched_weight = sum(weights.get(word, 1) for word in matched)
    total_weight = sum(weights.get(word, 1) for word in jd_keywords)

    if total_weight == 0:
        return 0

    return (matched_weight / total_weight) * 100

# =========================
# FORMAT SCORE
# =========================
def calculate_format_score(resume_text):
    score = 100

    required_sections = ["skills", "projects", "education"]

    for section in required_sections:
        if section not in resume_text.lower():
            score -= 10

    if "linkedin" not in resume_text.lower():
        score -= 5

    if "github" not in resume_text.lower():
        score -= 5

    return max(score, 50)

# =========================
# MAIN MATCHER
# =========================
def match_resume(resume_text, jd_text):
    # Clean
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)

    # Dynamic weights
    keyword_weights = get_role_weights(jd_text)


    resume_tech = extract_tech_keywords(resume_text)
    jd_tech = extract_tech_keywords(jd_text)

    # =========================
    # TF-IDF
    # =========================
    vectorizer = TfidfVectorizer(stop_words="english")

    vectors = vectorizer.fit_transform([resume_clean, jd_clean])

    tfidf_score = cosine_similarity(
        vectors[0], vectors[1]
    )[0][0] * 100

    # =========================
    # TECH SCORE
    # =========================
    tech_matched = resume_tech & jd_tech
    tech_missing = jd_tech - resume_tech

    if jd_tech:
        tech_score = calculate_weighted_score(
            tech_matched,
            jd_tech,
            keyword_weights
        )
    else:
        tech_score = tfidf_score

    # =========================
    # FORMAT SCORE
    # =========================
    format_score = calculate_format_score(resume_text)

    # =========================
    # TRUST SCORE
    # =========================
    trust_score = round(
        (format_score * 0.7) +
        (100 if "linkedin" in resume_text.lower() else 70) * 0.15 +
        (100 if "github" in resume_text.lower() else 70) * 0.15,
        2
    )

    # =========================
    # SYNONYM CHECK
    # =========================
    final_missing = []

    for keyword in tech_missing:
        try:
            synonyms = get_synonyms(keyword)
        except Exception:
            synonyms = set()

        found_synonym = False

        for syn in synonyms:
            if syn in resume_clean:
                found_synonym = True
                break

        if not found_synonym:
            final_missing.append(keyword)

    # =========================
    # FINAL MATCHED / MISSING
    # =========================
    all_matched = sorted(list(tech_matched))
    all_missing = sorted(list(set(final_missing)))

    all_missing = [k for k in all_missing if k not in all_matched]

    # =========================
    # SMART SUGGESTIONS
    # =========================
    suggestions = []

    for keyword in all_missing[:5]:
        suggestions.append(f"Add {keyword} to skills or projects")

    # =========================
    # FINAL SCORE
    # Tech = 60%
    # TF-IDF = 25%
    # Format = 15%
    # =========================
    final_score = round(
        (tech_score * 0.60) +
        (tfidf_score * 0.25) +
        (format_score * 0.15),
        2
    )

    final_score = min(final_score, 100)

    return {
        "score": final_score,
        "matched": all_matched[:20],
        "missing": all_missing[:15],
        "tech_score": round(tech_score, 2),
        "tfidf_score": round(tfidf_score, 2),
        "format_score": round(format_score, 2),
        "suggestions": suggestions,
        "trust_score": trust_score
    }