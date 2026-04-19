import requests
import json

# Test multiple queries
test_queries = [
    'what diseases can you detect',
    'how to prevent waterborne diseases',
    'what is turbidity',
    'hello there',
    'symptoms of cholera'
]

print("Testing improved chatbot responses:")
print("=" * 50)

for query in test_queries:
    url = 'http://127.0.0.1:5000/api/chat'
    data = {'message': query}

    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f'Query: "{query}"')
        print(f'Response: {result["bot_response"][:120]}...' if len(result["bot_response"]) > 120 else f'Response: {result["bot_response"]}')
        print(f'Confidence: {result["confidence"]:.2f}')
        print('---')
    except Exception as e:
        print(f'Error with "{query}": {e}')