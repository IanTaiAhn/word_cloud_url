# # app/topic_model.py
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

# model = SentenceTransformer("all-MiniLM-L6-v2")
model = SentenceTransformer('./ml_models/all-MiniLM-L6-v2')
topic_model = BERTopic()

def model_topics(docs):
    embeddings = model.encode(docs, show_progress_bar=False)
    topics, _ = topic_model.fit_transform(docs, embeddings)
    return topic_model.get_topics(), embeddings

# old
# BERTopic logic + embedding

# # app/topic_model.py
# from bertopic import BERTopic
# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer("all-MiniLM-L6-v2")
# topic_model = BERTopic()

# def model_topics(docs):
#     embeddings = model.encode(docs, show_progress_bar=False)
#     topics, _ = topic_model.fit_transform(docs, embeddings)
#     return topic_model.get_topics(), embeddings


# def generate_wordclouds(topics_dict):
#     clouds = {}
#     for topic_id, words in topics_dict.items():
#         freq = {word[0]: word[1] for word in words}
#         wc = WordCloud(width=600, height=400, background_color='white').generate_from_frequencies(freq)
#         buf = BytesIO()
#         wc.save(buf, format='PNG')
#         encoded = base64.b64encode(buf.getvalue()).decode()
#         clouds[topic_id] = encoded
#     return clouds


# Use global instance from topic_model.py
# from app.topic_model import topic_model



