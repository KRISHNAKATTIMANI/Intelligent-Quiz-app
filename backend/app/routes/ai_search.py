from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import openai
import os

ai_search_bp = Blueprint('ai_search', __name__)

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY', '')

@ai_search_bp.route('/search', methods=['POST'])
@jwt_required()
def ai_search():
    """Handle AI-powered search queries using OpenAI"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        if not openai.api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Create a system message for educational context
        system_message = """You are an intelligent educational assistant for a quiz management system. 
        Help students understand concepts, explain topics, provide study tips, and answer academic questions.
        Keep responses concise, clear, and educational. Focus on helping students learn effectively."""
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": query}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        return jsonify({
            'response': ai_response,
            'query': query
        }), 200
        
    except openai.error.AuthenticationError:
        return jsonify({'error': 'Invalid OpenAI API key'}), 500
    except openai.error.RateLimitError:
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
    except openai.error.APIError as e:
        return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500
    except Exception as e:
        print(f"AI Search error: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500
