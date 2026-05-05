"""
🤖 AquaRisk AI Chatbot
- Uses Groq API (Llama 3) for real AI responses
- No sklearn/numpy — lightweight for Render free plan
"""

import os
from datetime import datetime


def get_groq_response(user_message, chat_history=None):
    """Call Groq API (Llama 3) for AI response."""
    try:
        from groq import Groq

        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            return None

        client = Groq(api_key=api_key)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are AquaRisk AI, an expert health advisor specializing in waterborne diseases "
                    "and water quality analysis. You help users understand:\n"
                    "- Water quality parameters (pH, turbidity, TDS, nitrate, DO, BOD)\n"
                    "- Waterborne diseases (cholera, typhoid, dysentery, hepatitis A, giardia)\n"
                    "- Disease prevention and water purification methods\n"
                    "- Health symptoms related to contaminated water\n"
                    "- WHO water quality guidelines\n\n"
                    "Always give clear, helpful, medically accurate responses. "
                    "If someone describes serious symptoms, advise them to see a doctor. "
                    "Keep responses concise but informative. Use emojis occasionally to be friendly."
                )
            }
        ]

        # Add recent chat history for context
        if chat_history:
            for msg in chat_history[-6:]:
                if msg['type'] == 'user':
                    messages.append({"role": "user", "content": msg['message']})
                elif msg['type'] == 'bot':
                    messages.append({"role": "assistant", "content": msg['message']})

        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Groq API error: {e}")
        return None


def get_fallback_response(user_message):
    """Simple keyword-based fallback if Groq is unavailable."""
    msg = user_message.lower()

    if any(w in msg for w in ['hello', 'hi', 'hey']):
        return "👋 Hello! I am AquaRisk AI. Ask me about water quality, waterborne diseases, or health symptoms!"

    if any(w in msg for w in ['ph', 'acid', 'alkaline']):
        return "pH measures water acidity (0-14). Safe drinking water: pH 6.5–8.5. Below 6.5 is acidic, above 8.5 is alkaline — both can indicate contamination."

    if any(w in msg for w in ['turbidity', 'cloudy', 'clear']):
        return "Turbidity measures water cloudiness. Safe limit: below 5 NTU. High turbidity indicates suspended particles that can carry pathogens."

    if any(w in msg for w in ['cholera', 'typhoid', 'dysentery', 'hepatitis']):
        return "These are waterborne diseases spread through contaminated water. Symptoms vary but include diarrhea, fever, and vomiting. See a doctor immediately if you suspect infection."

    if any(w in msg for w in ['diarrhea', 'vomit', 'sick', 'ill', 'fever']):
        return "⚠️ If you are feeling unwell: Stay hydrated, avoid contaminated water/food, and see a doctor if symptoms are severe or prolonged."

    if any(w in msg for w in ['purify', 'boil', 'filter', 'safe']):
        return "🔥 To make water safe:\n1. Boil for at least 1 minute\n2. Use a certified filter\n3. Use RO/UV purifier\n4. Add purification tablets if needed"

    if any(w in msg for w in ['tds', 'dissolved']):
        return "TDS (Total Dissolved Solids) measures minerals in water. Safe limit: below 500 mg/L (BIS). Above 900 mg/L is unsafe for drinking."

    if any(w in msg for w in ['nitrate', 'nitrogen']):
        return "Nitrate in water above 50 mg/L is dangerous, especially for infants. It can cause blue baby syndrome. WHO limit is 50 mg/L."

    return "I'm here to help with water quality and health questions! Try asking about pH, turbidity, waterborne diseases, or water purification. 💧"


class HealthAdvisorChatbot:
    """
    AI-powered chatbot using Groq (Llama 3).
    Lightweight fallback if Groq is unavailable.
    No sklearn/numpy required.
    """

    def chat(self, user_message, chat_history=None):
        user_message_clean = user_message.strip()

        if not user_message_clean:
            return {
                'bot_response': 'Please ask a question about water quality or health.',
                'confidence': 0.0,
                'timestamp': datetime.now().isoformat(),
                'ai_powered': False
            }

        # ✅ Try Groq AI first
        ai_response = get_groq_response(user_message_clean, chat_history)

        if ai_response:
            return {
                'user_message': user_message_clean,
                'bot_response': ai_response,
                'confidence': 1.0,
                'timestamp': datetime.now().isoformat(),
                'ai_powered': True
            }

        # Lightweight fallback
        fallback = get_fallback_response(user_message_clean)
        return {
            'user_message': user_message_clean,
            'bot_response': fallback,
            'confidence': 0.5,
            'timestamp': datetime.now().isoformat(),
            'ai_powered': False
        }


if __name__ == "__main__":
    bot = HealthAdvisorChatbot()
    questions = [
        "What is water pollution?",
        "I have diarrhea and fever",
        "How to purify borewell water?",
        "What does high turbidity mean?",
    ]
    for q in questions:
        r = bot.chat(q)
        print(f"\n👤 {q}")
        print(f"🤖 {r['bot_response']}")
        print(f"   AI: {r['ai_powered']}")