from wordcloud import WordCloud
import base64
from io import BytesIO

def generate_wordclouds(topics_dict):
    """Generate word clouds for topics and return as base64 encoded images"""
    clouds = {}
    
    for topic_id, words in topics_dict.items():
        try:
            # Skip outlier topic (-1) if present
            if topic_id == -1:
                continue
            
            # Create frequency dictionary from topic words
            # Handle both formats: [(word, score), ...] or {word: score}
            if isinstance(words, list) and len(words) > 0:
                if isinstance(words[0], tuple):
                    freq = {word: score for word, score in words}
                else:
                    # If it's just a list of words, give them equal weight
                    freq = {word: 1.0 for word in words}
            elif isinstance(words, dict):
                freq = words
            else:
                print(f"Skipping topic {topic_id}: invalid format")
                continue
            
            # Skip if no words
            if not freq:
                print(f"Skipping topic {topic_id}: no words found")
                continue
            
            # Create WordCloud
            wc = WordCloud(
                width=600, 
                height=400, 
                background_color='white',
                max_words=50,
                relative_scaling=0.5,
                colormap='viridis'
            ).generate_from_frequencies(freq)
            
            # Convert to PIL Image
            image = wc.to_image()
            
            # Save to BytesIO buffer
            buf = BytesIO()
            image.save(buf, format='PNG')
            buf.seek(0)
            
            # Encode to base64
            encoded = base64.b64encode(buf.getvalue()).decode()
            clouds[topic_id] = encoded
            
        except Exception as e:
            print(f"Error generating wordcloud for topic {topic_id}: {e}")
            continue
    
    return clouds

def generate_wordclouds_html(topics_dict, output_file='wordclouds.html', title='Topic Word Clouds'):
    """Generate word clouds and embed them in HTML for web viewing"""
    import base64
    from io import BytesIO
    from wordcloud import WordCloud
    
    # Start building HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                text-align: center;
                color: #333;
                margin-bottom: 30px;
            }}
            .topic-section {{
                margin-bottom: 40px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #fafafa;
            }}
            .topic-title {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 15px;
                color: #2c3e50;
                text-align: center;
            }}
            .wordcloud-image {{
                display: block;
                margin: 0 auto;
                max-width: 100%;
                height: auto;
                border: 2px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            .no-topics {{
                text-align: center;
                color: #666;
                font-style: italic;
                padding: 40px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{title}</h1>
    """
    
    topics_processed = 0
    
    for topic_id, words in topics_dict.items():
        try:
            # Skip outlier topic (-1) if present
            if topic_id == -1:
                continue
            
            # Create frequency dictionary from topic words
            # Handle both formats: [(word, score), ...] or {word: score}
            if isinstance(words, list) and len(words) > 0:
                if isinstance(words[0], tuple):
                    freq = {word: score for word, score in words}
                else:
                    # If it's just a list of words, give them equal weight
                    freq = {word: 1.0 for word in words}
            elif isinstance(words, dict):
                freq = words
            else:
                print(f"Skipping topic {topic_id}: invalid format")
                continue
            
            # Skip if no words
            if not freq:
                print(f"Skipping topic {topic_id}: no words found")
                continue
            
            # Create WordCloud
            wc = WordCloud(
                width=800, 
                height=500, 
                background_color='white',
                max_words=50,
                relative_scaling=0.5,
                colormap='viridis',
                margin=10
            ).generate_from_frequencies(freq)
            
            # Convert to PIL Image
            image = wc.to_image()
            
            # Save to BytesIO buffer
            buf = BytesIO()
            image.save(buf, format='PNG')
            buf.seek(0)
            
            # Encode to base64
            encoded = base64.b64encode(buf.getvalue()).decode()
            
            # Add topic section to HTML
            html_content += f"""
            <div class="topic-section">
                <div class="topic-title">Topic {topic_id}</div>
                <img src="data:image/png;base64,{encoded}" 
                     alt="Word Cloud for Topic {topic_id}" 
                     class="wordcloud-image">
            </div>
            """
            
            topics_processed += 1
            
        except Exception as e:
            print(f"Error generating wordcloud for topic {topic_id}: {e}")
            continue
    
    # Handle case where no topics were processed
    if topics_processed == 0:
        html_content += """
        <div class="no-topics">
            <p>No word clouds could be generated from the provided topics.</p>
        </div>
        """
    
    # Close HTML
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Save HTML file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Word clouds saved to {output_file}")
        print(f"Successfully processed {topics_processed} topics")
        return output_file
    except Exception as e:
        print(f"Error saving HTML file: {e}")
        return None


# Example usage and testing
def test_wordcloud_generation():
    """Test function with sample data"""
    # Sample topics data in BERTopic format
    sample_topics = {
        0: [('machine', 0.5), ('learning', 0.4), ('algorithm', 0.3), ('data', 0.2)],
        1: [('python', 0.6), ('programming', 0.4), ('code', 0.3), ('software', 0.2)],
        2: [('analysis', 0.5), ('statistics', 0.4), ('research', 0.3), ('study', 0.2)]
    }
    
    try:
        clouds = generate_wordclouds(sample_topics)
        print(f"Successfully generated {len(clouds)} wordclouds")
        for topic_id in clouds:
            print(f"Topic {topic_id}: {len(clouds[topic_id])} characters (base64)")
        return clouds
    except Exception as e:
        print(f"Test failed: {e}")


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
        return None