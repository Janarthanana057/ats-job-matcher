import spacy
import nltk
from nltk.corpus import stopwords, wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string
import re

# Load SpaCy model
nlp = spacy.load('en_core_web_sm')

# Download required NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)

STOP_WORDS = set(stopwords.words('english'))

# Important tech keywords - weighted higher
TECH_KEYWORDS = {
    'python', 'java', 'javascript', 'sql', 'html', 'css', 'flask',
    'django', 'fastapi', 'react', 'nodejs', 'git', 'github', 'docker',
    'kubernetes', 'aws', 'azure', 'gcp', 'linux', 'rest', 'api',
    'machine learning', 'deep learning', 'nlp', 'opencv', 'tensorflow',
    'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
    'streamlit', 'firebase', 'mongodb', 'postgresql', 'mysql',
    'data analysis', 'data structures', 'algorithms', 'oop',
    'agile', 'scrum', 'ci/cd', 'devops', 'microservices',
    'problem solving', 'communication', 'teamwork', 'leadership'
}

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonym = lemma.name().replace('_', ' ').lower()
            synonyms.add(synonym)
    return synonyms

def extract_spacy_keywords(text):
    doc = nlp(text)
    keywords = set()

    # Extract named entities
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'WORK_OF_ART']:
            keywords.add(ent.text.lower())

    # Extract noun chunks
    for chunk in doc.noun_chunks:
        clean = chunk.text.lower().strip()
        if len(clean) > 2 and clean not in STOP_WORDS:
            keywords.add(clean)

    # Extract important tokens
    for token in doc:
        if (not token.is_stop and
            not token.is_punct and
            not token.is_space and
            len(token.text) > 2 and
            token.pos_ in ['NOUN', 'PROPN', 'VERB', 'ADJ']):
            keywords.add(token.lemma_.lower())

    return keywords

def extract_tech_keywords(text):
    text_lower = text.lower()
    found = set()
    for keyword in TECH_KEYWORDS:
        if keyword in text_lower:
            found.add(keyword)
    return found

def match_resume(resume_text, jd_text):
    # Clean texts
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)

    # Extract keywords using SpaCy
    resume_spacy = extract_spacy_keywords(resume_text)
    jd_spacy = extract_spacy_keywords(jd_text)

    # Extract tech keywords
    resume_tech = extract_tech_keywords(resume_text)
    jd_tech = extract_tech_keywords(jd_text)

    # TF-IDF cosine similarity score
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_clean, jd_clean])
    tfidf_score = cosine_similarity(vectors[0], vectors[1])[0][0] * 100

    # Tech keyword match score (weighted higher)
    if jd_tech:
        tech_matched = resume_tech & jd_tech
        tech_score = (len(tech_matched) / len(jd_tech)) * 100
    else:
        tech_score = tfidf_score

    # Combined score - tech keywords weighted 60%, tfidf 40%
    final_score = round((tech_score * 0.6) + (tfidf_score * 0.4), 2)

    # Find matched and missing keywords
    # Tech keywords (most important)
    tech_matched = list(resume_tech & jd_tech)
    tech_missing = list(jd_tech - resume_tech)

    # SpaCy keywords (additional context)
    spacy_matched = list(resume_spacy & jd_spacy)
    spacy_missing = list(jd_spacy - resume_spacy)

    # Synonym check for missing keywords
    final_missing = []
    for keyword in tech_missing:
        synonyms = get_synonyms(keyword)
        found_synonym = False
        for syn in synonyms:
            if syn in resume_clean:
                found_synonym = True
                break
        if not found_synonym:
            final_missing.append(keyword)

    # Combine and deduplicate
    all_matched = list(set(tech_matched + spacy_matched[:10]))
    all_missing = list(set(final_missing + spacy_missing[:5]))

    # Remove matched from missing
    all_missing = [k for k in all_missing if k not in all_matched]

    return {
        'score': final_score,
        'matched': sorted(all_matched),
        'missing': sorted(all_missing[:15]),
        'tech_score': round(tech_score, 2),
        'tfidf_score': round(tfidf_score, 2)
    }