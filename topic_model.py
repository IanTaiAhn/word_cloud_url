from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class SimpleTFIDFTopicModel:
    def __init__(self, n_clusters=5, max_features=100):
        self.n_clusters = n_clusters
        self.max_features = max_features
        self.vectorizer = TfidfVectorizer(
            max_features=max_features, 
            stop_words='english',
            ngram_range=(1, 2)  # Include bigrams for better topics
        )
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.topics_ = {}
        self.embeddings_ = None
        self.labels_ = None
        
    def fit_transform(self, docs, embeddings=None):
        """
        Fit the model and return topic assignments and embeddings
        
        Args:
            docs: List of documents
            embeddings: Ignored (for compatibility with bertopic)
            
        Returns:
            topics: Array of topic assignments for each document
            embeddings: TF-IDF matrix (dense format for compatibility)
        """
        # Generate TF-IDF embeddings
        self.embeddings_ = self.vectorizer.fit_transform(docs)
        
        # Cluster documents
        self.labels_ = self.kmeans.fit_predict(self.embeddings_)
        
        # Generate topics dictionary
        self._generate_topics()
        
        # Return dense embeddings for compatibility
        embeddings_dense = self.embeddings_.toarray()
        
        return self.labels_, embeddings_dense
    
    def _generate_topics(self):
        """Generate topics dictionary similar to bertopic format"""
        feature_names = self.vectorizer.get_feature_names_out()
        
        for i in range(self.n_clusters):
            cluster_center = self.kmeans.cluster_centers_[i]
            top_indices = cluster_center.argsort()[-10:][::-1]
            
            # Format similar to bertopic: [(word, score), ...]
            topic_words = []
            for idx in top_indices:
                word = feature_names[idx]
                score = cluster_center[idx]
                topic_words.append((word, score))
            
            self.topics_[i] = topic_words
    
    def get_topics(self):
        """Return topics dictionary (compatible with bertopic)"""
        return self.topics_

def model_topics(docs, n_clusters=5):
    """
    Drop-in replacement for your original model_topics function
    
    Args:
        docs: List of documents to cluster
        n_clusters: Number of topics/clusters to create
        
    Returns:
        topics: Dictionary of topics {topic_id: [(word, score), ...]}
        embeddings: TF-IDF embeddings matrix
    """
    topic_model = SimpleTFIDFTopicModel(n_clusters=n_clusters)
    topics, embeddings = topic_model.fit_transform(docs)
    return topic_model.get_topics(), embeddings

# # Example usage:
# if __name__ == "__main__":
#     # Sample documents
#     docs = [
#         "Python programming is great for data science and machine learning",
#         "JavaScript is essential for web development and frontend applications",
#         "Machine learning algorithms require lots of data preprocessing",
#         "Web developers use HTML CSS and JavaScript for building websites",
#         "Data scientists use Python pandas and numpy for data analysis",
#         "React and Vue are popular JavaScript frameworks for web apps"
#     ]
    
#     # Use exactly like your original function
#     topics, embeddings = model_topics(docs, n_clusters=3)
    
#     # Print topics
#     for topic_id, words in topics.items():
#         print(f"Topic {topic_id}:")
#         for word, score in words:
#             print(f"  {word}: {score:.3f}")
#         print()