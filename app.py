from flask import Flask, request, jsonify, render_template
from textblob import TextBlob
import re

app = Flask(__name__)

def clean_text(text):
    """Clean and preprocess text"""
    # Remove special characters and extra spaces
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def analyze_sentiment(text):
    """Analyze sentiment using TextBlob"""
    cleaned_text = clean_text(text)
    blob = TextBlob(cleaned_text)
    
    # Get polarity (-1 to 1) and subjectivity (0 to 1)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    # Determine sentiment category
    if polarity > 0.1:
        sentiment = 'Positive'
        emoji = '😊'
    elif polarity < -0.1:
        sentiment = 'Negative'
        emoji = '😞'
    else:
        sentiment = 'Neutral'
        emoji = '😐'
    
    return {
        'sentiment': sentiment,
        'emoji': emoji,
        'polarity': round(polarity, 3),
        'subjectivity': round(subjectivity, 3),
        'confidence': round(abs(polarity) * 100, 1)
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text or len(text.strip()) == 0:
            return jsonify({'error': 'Please provide text to analyze'}), 400
        
        if len(text) > 5000:
            return jsonify({'error': 'Text too long. Maximum 5000 characters'}), 400
        
        result = analyze_sentiment(text)
        result['text'] = text
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        
        if not texts or not isinstance(texts, list):
            return jsonify({'error': 'Please provide a list of texts'}), 400
        
        if len(texts) > 100:
            return jsonify({'error': 'Maximum 100 texts per batch'}), 400
        
        results = []
        for text in texts:
            if text and len(text.strip()) > 0:
                result = analyze_sentiment(text)
                result['text'] = text[:100] + '...' if len(text) > 100 else text
                results.append(result)
        
        return jsonify({'results': results, 'count': len(results)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('Starting Sentiment Analyzer...')
    print('Visit http://localhost:5000 to use the app')
    app.run(debug=True, port=5000)
