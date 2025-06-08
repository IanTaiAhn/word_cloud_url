# Word cloud generation, plots
# app/visualization.py
from wordcloud import WordCloud
import base64
from io import BytesIO
from bertopic import BERTopic

# Use global instance from topic_model.py
from app.topic_model import topic_model

def generate_wordclouds(topics_dict):
    clouds = {}
    for topic_id, words in topics_dict.items():
        freq = {word[0]: word[1] for word in words}
        wc = WordCloud(width=600, height=400, background_color='white').generate_from_frequencies(freq)
        buf = BytesIO()
        wc.save(buf, format='PNG')
        encoded = base64.b64encode(buf.getvalue()).decode()
        clouds[topic_id] = encoded
    return clouds