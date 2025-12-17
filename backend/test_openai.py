"""Test OpenAI connection"""
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment
load_dotenv()

# Get API key
api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key found: {'Yes' if api_key else 'No'}")
print(f"API Key starts: {api_key[:30] if api_key else 'None'}...")

try:
    # Initialize client
    client = OpenAI(api_key=api_key)
    print("✓ Client initialized")
    
    # Test simple request
    print("\nTesting OpenAI API...")
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello World' in exactly 2 words."}
        ],
        max_tokens=10
    )
    
    print(f"✓ API Response: {response.choices[0].message.content}")
    print("✓ OpenAI connection successful!")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {str(e)}")
