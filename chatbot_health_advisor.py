"""
🤖 AI-Powered Health Advisor Chatbot
- Uses Groq API (Llama 3) for real AI responses
- Falls back to TF-IDF if Groq is unavailable
"""

import os
import json
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ── GROQ AI FUNCTION ─────────────────────────────────────

def get_groq_response(user_message, chat_history=None):
    """
    Call Groq API (Llama 3) for AI response.
    Returns response string or None if failed.
    """
    try:
        from groq import Groq

        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            return None

        client = Groq(api_key=api_key)

        # Build message history for context
        messages = [
            {
                "role": "system",
                "content": (
                    "You are AquaRisk AI, an expert health advisor specializing in waterborne diseases, "
                    "water quality analysis, and public health. You help users understand:\n"
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

        # Add recent chat history for context (last 6 messages)
        if chat_history:
            for msg in chat_history[-6:]:
                if msg['type'] == 'user':
                    messages.append({"role": "user", "content": msg['message']})
                elif msg['type'] == 'bot':
                    messages.append({"role": "assistant", "content": msg['message']})

        # Add current message
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


# ── FALLBACK TF-IDF CHATBOT ───────────────────────────────

class HealthAdvisorChatbot:
    """
    AI-powered chatbot using Groq (Llama 3).
    Falls back to TF-IDF pattern matching if Groq is unavailable.
    """

    def __init__(self):
        self.knowledge_base = self._build_knowledge_base()
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        self._train_vectorizer()

    def _build_knowledge_base(self):
        return [
            {
                'questions': ['what is water pollution', 'define water pollution', 'what causes water pollution'],
                'answer': 'Water pollution is the contamination of water bodies by harmful substances. It can be caused by industrial discharge, sewage, agricultural runoff, and natural events. Our system monitors key parameters like pH, turbidity, and microbiological contaminants.'
            },
            {
                'questions': ['what are water-borne diseases', 'diseases from water', 'water borne illness'],
                'answer': 'Water-borne diseases are illnesses transmitted through contaminated water. Common ones include cholera, typhoid, dysentery, and hepatitis A. They can be prevented through clean water access and good hygiene.'
            },
            {
                'questions': ['what is pH in water', 'explain pH', 'pH meaning'],
                'answer': 'pH measures water acidity (0-14 scale). Neutral pH is 7. Safe drinking water typically has pH 6.5-8.5. Too acidic or alkaline water can indicate contamination.'
            },
            {
                'questions': ['what is turbidity', 'explain turbidity', 'turbidity meaning'],
                'answer': 'Turbidity measures water cloudiness caused by suspended particles. High turbidity (>5 NTU) indicates potential contamination and can shield harmful bacteria. Clear water is generally safer.'
            },
            {
                'questions': ['how to prevent water-borne diseases', 'water safety tips', 'stay healthy water'],
                'answer': '✅ Key Prevention Steps:\n1. Drink clean, treated water\n2. Maintain proper hygiene\n3. Wash hands regularly\n4. Boil water if uncertain\n5. Use public sanitation facilities\n6. Report contamination immediately'
            },
            {
                'questions': ['what does your system do', 'how does system work', 'project overview'],
                'answer': 'Our Water-Borne Disease Detection System uses AI to:\n1. Monitor water quality in real-time\n2. Predict disease outbreaks\n3. Analyze community health reports\n4. Generate public health alerts\n5. Support early intervention'
            },
            {
                'questions': ['i have diarrhea', 'loose motions', 'digestive issue'],
                'answer': '⚠️ If you have diarrhea:\n1. Stay hydrated with clean water\n2. Avoid contaminated food/water\n3. Practice good hygiene\n4. See doctor if severe or prolonged\n5. Report to health authorities if part of outbreak'
            },
            {
                'questions': ['is my water safe', 'check water quality', 'water safe to drink'],
                'answer': 'You can check if your water is safe by:\n1. Using our Detailed Analysis tool\n2. Checking local water quality reports\n3. Looking for visible contamination\n4. Contacting local water authority\n5. In doubt, boil or use filtered water'
            },
            {
                'questions': ['hello', 'hi', 'hey', 'good morning', 'good evening'],
                'answer': '👋 Hello! I am AquaRisk AI, your water health advisor. Ask me anything about water quality, waterborne diseases, health symptoms, or disease prevention!'
            },
            {
                'questions': ['boil water', 'how to purify water', 'make water safe'],
                'answer': '🔥 To make water safe:\n1. Boil for at least 1 minute\n2. Use a certified water filter\n3. Add water purification tablets\n4. Use RO/UV purifier if available\n5. Let boiled water cool before drinking'
            },
        ]

    def _train_vectorizer(self):
        all_questions = []
        for qa in self.knowledge_base:
            all_questions.extend(qa['questions'])
        self.vectorizer.fit(all_questions)

    def _fallback_answer(self, user_question, threshold=0.2):
        user_vec = self.vectorizer.transform([user_question])
        best_match_idx = -1
        best_similarity = threshold

        for idx, qa in enumerate(self.knowledge_base):
            for question in qa['questions']:
                q_vec = self.vectorizer.transform([question])
                similarity = cosine_similarity(user_vec, q_vec)[0][0]
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_idx = idx

        if best_match_idx == -1:
            return "I'm not sure about that. Try asking about water quality, health symptoms, or disease prevention. 💧"

        return self.knowledge_base[best_match_idx]['answer']

    def chat(self, user_message, chat_history=None):
        """
        Main chat function — uses Groq AI first, falls back to TF-IDF.
        """
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
                'ai_powered': True   # ✅ Real AI response
            }

        # Fallback to TF-IDF if Groq fails
        fallback = self._fallback_answer(user_message_clean.lower())
        return {
            'user_message': user_message_clean,
            'bot_response': fallback,
            'confidence': 0.5,
            'timestamp': datetime.now().isoformat(),
            'ai_powered': False   # Fallback response
        }


# ── Test ──────────────────────────────────────────────────
if __name__ == "__main__":
    bot = HealthAdvisorChatbot()
    test_questions = [
        "What is water pollution?",
        "I have diarrhea and fever",
        "How to purify borewell water?",
        "What does high turbidity mean?",
        "Is pH 5 safe for drinking?",
    ]
    print("\n🤖 AquaRisk AI Responses:")
    for question in test_questions:
        response = bot.chat(question)
        print(f"\n👤 User: {question}")
        print(f"🤖 Bot: {response['bot_response']}")
        print(f"   AI Powered: {response['ai_powered']}")