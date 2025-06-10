import spacy
import re

nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    doc = nlp(text)
    return [' '.join([token.lemma_ for token in sent if not token.is_stop and token.is_alpha])
            for sent in doc.sents if len(sent) > 5]
