from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
# model = SentenceTransformer('./ml_models/all-MiniLM-L6-v2')
topic_model = BERTopic()

def model_topics(docs):
    embeddings = model.encode(docs, show_progress_bar=False)
    topics, _ = topic_model.fit_transform(docs, embeddings)
    return topic_model.get_topics(), embeddings