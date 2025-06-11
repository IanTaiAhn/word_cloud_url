from wordcloud import WordCloud
import base64
from io import BytesIO

# Alternative: Return HTML word clouds instead of images
def generate_wordclouds_html(topics):
    """
    Generate simple HTML word clouds (lighter weight than images)
    """
    html_clouds = {}
    
    for topic_id, word_scores in topics.items():
        # Create HTML with scaled font sizes
        html_words = []
        max_score = max(score for word, score in word_scores) if word_scores else 1
        
        for word, score in word_scores[:20]:  # Top 20 words
            # Scale font size based on score
            font_size = int(12 + (score / max_score) * 24)  # 12px to 36px
            opacity = 0.6 + (score / max_score) * 0.4  # 0.6 to 1.0
            
            html_words.append(
                f'<span style="font-size: {font_size}px; opacity: {opacity}; '
                f'margin: 2px; color: hsl({hash(word) % 360}, 70%, 50%);">{word}</span>'
            )
        
        html_clouds[f'topic_{topic_id}'] = f'<div style="line-height: 1.8;">{" ".join(html_words)}</div>'
    
    return html_clouds
def generate_full_html_page(url, wordclouds, topics, num_documents):
    """
    Generate complete HTML page with embedded word clouds
    """
    # Create topic cards HTML
    topic_cards = ""
    for topic_key, wordcloud_html in wordclouds.items():
        topic_id = topic_key.split('_')[1]  # Extract number from 'topic_0'
        
        # Get top 3 words for title
        topic_words = topics.get(int(topic_id), [])
        top_words = [word for word, score in topic_words[:3]]
        title = " • ".join(top_words) if top_words else f"Topic {topic_id}"
        
        topic_cards += f"""
        <div class="topic-card">
            <h3>Topic {topic_id}: {title}</h3>
            <div class="wordcloud">
                {wordcloud_html}
            </div>
        </div>
        """
    
    # Complete HTML page
    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Topic Analysis Results - {url}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                backdrop-filter: blur(10px);
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 2px solid #eee;
            }}
            
            .header h1 {{
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 2.5em;
                font-weight: 300;
            }}
            
            .url-info {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                border-left: 4px solid #667eea;
            }}
            
            .url-info strong {{
                color: #495057;
            }}
            
            .stats {{
                display: flex;
                justify-content: center;
                gap: 30px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }}
            
            .stat-item {{
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 15px 25px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            
            .stat-number {{
                font-size: 2em;
                font-weight: bold;
                display: block;
            }}
            
            .topics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 25px;
                margin-top: 30px;
            }}
            
            .topic-card {{
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                border: 1px solid #e9ecef;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            
            .topic-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            }}
            
            .topic-card h3 {{
                color: #2c3e50;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #667eea;
                font-size: 1.3em;
            }}
            
            .wordcloud {{
                text-align: center;
                padding: 20px;
                background: linear-gradient(45deg, #f8f9fa, #e9ecef);
                border-radius: 8px;
                min-height: 120px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-wrap: wrap;
            }}
            
            .wordcloud span {{
                display: inline-block;
                padding: 2px 6px;
                margin: 2px;
                border-radius: 4px;
                background: rgba(255, 255, 255, 0.8);
                transition: all 0.3s ease;
                cursor: default;
            }}
            
            .wordcloud span:hover {{
                transform: scale(1.1);
                background: rgba(255, 255, 255, 1);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #6c757d;
            }}
            
            .new-analysis {{
                text-align: center;
                margin-top: 30px;
            }}
            
            .btn {{
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 25px;
                font-size: 1.1em;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }}
            
            @media (max-width: 768px) {{
                .topics-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .container {{
                    padding: 20px;
                    margin: 10px;
                }}
                
                .stats {{
                    flex-direction: column;
                    align-items: center;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Topic Analysis Results</h1>
            </div>
            
            <div class="url-info">
                <strong>Analyzed URL:</strong> <a href="{url}" target="_blank">{url}</a>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{len(wordclouds)}</span>
                    <span>Topics Found</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{num_documents}</span>
                    <span>Text Segments</span>
                </div>
            </div>
            
            <div class="topics-grid">
                {topic_cards}
            </div>
            
            <div class="new-analysis">
                <a href="/" class="btn">🔍 Analyze Another URL</a>
            </div>
            
            <div class="footer">
                <p>Generated with lightweight topic modeling • FastAPI + TF-IDF + K-means</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_page