"""
🤖 FEATURE 8: AI Chatbot (NLP-based Q&A)
- Uses simple pattern matching + TF-IDF for Q&A
- Answers questions about water quality, health risks, and system usage
- Free & Open Source (scikit-learn, pandas)
"""

import json
import numpy as np
from datetime import datetime                          # ✅ FIX 1: use datetime instead of pandas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class HealthAdvisorChatbot:
    """
    Simple NLP-based chatbot for health and water quality queries
    """

    def __init__(self):
        self.knowledge_base = self._build_knowledge_base()
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        self._train_vectorizer()

    def _build_knowledge_base(self):
        """Build Q&A knowledge base"""
        return [
            {
                'questions': [
                    'what is water pollution',
                    'define water pollution',
                    'what causes water pollution'
                ],
                'answer': 'Water pollution is the contamination of water bodies by harmful substances. '
                          'It can be caused by industrial discharge, sewage, agricultural runoff, and natural events. '
                          'Our system monitors key parameters like pH, turbidity, and microbiological contaminants.'
            },
            {
                'questions': [
                    'what are water-borne diseases',
                    'diseases from water',
                    'water borne illness'
                ],
                'answer': 'Water-borne diseases are illnesses transmitted through contaminated water. '
                          'Common ones include cholera, typhoid, dysentery, and hepatitis A. '
                          'They can be prevented through clean water access and good hygiene.'
            },
            {
                'questions': [
                    'how do i report health issues',
                    'submit health report',
                    'report symptoms'
                ],
                'answer': 'You can report health issues through our community health reporting system. '
                          'Simply enter your symptoms, location, and date. '
                          'This helps us identify early disease patterns.'
            },
            {
                'questions': [
                    'what is pH in water',
                    'explain pH',
                    'pH meaning'
                ],
                'answer': 'pH measures water acidity (0-14 scale). Neutral pH is 7. '
                          'Safe drinking water typically has pH 6.5-8.5. '
                          'Too acidic or alkaline water can indicate contamination.'
            },
            {
                'questions': [
                    'what is turbidity',
                    'explain turbidity',
                    'turbidity meaning'
                ],
                'answer': 'Turbidity measures water cloudiness caused by suspended particles. '
                          'High turbidity (>5 NTU) indicates potential contamination and can shield harmful bacteria. '
                          'Clear water is generally safer.'
            },
            {
                'questions': [
                    'how to prevent water-borne diseases',
                    'water safety tips',
                    'stay healthy water'
                ],
                'answer': '✅ Key Prevention Steps:\n'
                          '1. Drink clean, treated water\n'
                          '2. Maintain proper hygiene\n'
                          '3. Wash hands regularly\n'
                          '4. Boil water if uncertain\n'
                          '5. Use public sanitation facilities\n'
                          '6. Report contamination immediately'
            },
            {
                'questions': [
                    'what does your system do',
                    'how does system work',
                    'project overview'
                ],
                'answer': 'Our Water-Borne Disease Detection System uses machine learning to:\n'
                          '1. Monitor water quality in real-time\n'
                          '2. Predict disease outbreaks\n'
                          '3. Analyze community health reports\n'
                          '4. Generate public health alerts\n'
                          '5. Support early intervention'
            },
            {
                'questions': [
                    'i have diarrhea',
                    'loose motions',
                    'digestive issue'
                ],
                'answer': '⚠️ If you have diarrhea:\n'
                          '1. Stay hydrated with clean water\n'
                          '2. Avoid contaminated food/water\n'
                          '3. Practice good hygiene\n'
                          '4. See doctor if severe or prolonged\n'
                          '5. Report to health authorities if part of outbreak'
            },
            {
                'questions': [
                    'is my water safe',
                    'check water quality',
                    'water safe to drink'
                ],
                'answer': 'You can check if your water is safe by:\n'
                          '1. Checking local water quality reports\n'
                          '2. Using our system to test water parameters\n'
                          '3. Looking for visible contamination\n'
                          '4. Contacting local water authority\n'
                          '5. In doubt, boil or use filtered water'
            },
            # ✅ Extra entries to improve match coverage
            {
                'questions': [
                    'hello',
                    'hi',
                    'hey',
                    'good morning',
                    'good evening'
                ],
                'answer': '👋 Hello! I am your Water Health Advisor. You can ask me about water quality, '
                          'waterborne diseases, health symptoms, or how to use this system.'
            },
            {
                'questions': [
                    'cholera symptoms',
                    'what is cholera',
                    'cholera treatment'
                ],
                'answer': 'Cholera is an acute diarrheal infection caused by contaminated water. '
                          'Symptoms include profuse watery diarrhea, vomiting, and dehydration. '
                          'Treatment: ORS immediately, seek urgent medical care.'
            },
            {
                'questions': [
                    'typhoid symptoms',
                    'what is typhoid',
                    'typhoid fever'
                ],
                'answer': 'Typhoid is a bacterial infection spread through contaminated water/food. '
                          'Symptoms include sustained high fever, fatigue, and abdominal pain. '
                          'See a doctor if fever persists beyond 3 days.'
            },
            {
                'questions': [
                    'boil water',
                    'how to purify water',
                    'make water safe'
                ],
                'answer': '🔥 To make water safe:\n'
                          '1. Boil for at least 1 minute (3 min at high altitude)\n'
                          '2. Use a certified water filter\n'
                          '3. Add water purification tablets\n'
                          '4. Use RO/UV purifier if available\n'
                          '5. Let boiled water cool before drinking'
            },
        ]

    def _train_vectorizer(self):
        """Train TF-IDF vectorizer on all questions"""
        all_questions = []
        for qa in self.knowledge_base:
            all_questions.extend(qa['questions'])
        self.vectorizer.fit(all_questions)

    def find_best_answer(self, user_question, threshold=0.2):   # ✅ FIX 2: lowered threshold 0.3→0.2 for better matching
        """
        Find best matching answer for user question

        Args:
            user_question (str): User's question
            threshold (float): Similarity threshold (0-1)

        Returns:
            dict: Answer and confidence
        """
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
            return {
                'answer': "I'm not sure about that. Try asking about water quality, health symptoms, or disease prevention. 💧",
                'confidence': 0.0,
                'found': False
            }

        return {
            'answer': self.knowledge_base[best_match_idx]['answer'],
            'confidence': float(best_similarity),
            'found': True
        }

    def chat(self, user_message):
        """
        Main chat function

        Args:
            user_message (str): User's message

        Returns:
            dict: Chatbot response
        """
        user_message = user_message.strip().lower()

        if not user_message:
            return {
                'bot_response': 'Please ask a question about water quality or health.',
                'confidence': 0.0,
                'timestamp': datetime.now().isoformat()   # ✅ FIX 3: was pd.Timestamp.now() — crashed outside __main__
            }

        result = self.find_best_answer(user_message)

        return {
            'user_message': user_message,
            'bot_response': result['answer'],
            'confidence': result['confidence'],
            'timestamp': datetime.now().isoformat()       # ✅ FIX 3: same fix here
        }


# ── Example usage (run this file directly to test) ───────
if __name__ == "__main__":
    bot = HealthAdvisorChatbot()

    test_questions = [
        "What is water pollution?",
        "I have diarrhea",
        "How to prevent disease?",
        "Is my water safe?",
        "Tell me about your system",
        "What is pH?",
        "Hello",
        "How to boil water?",
    ]

    print("\n🤖 Chatbot Responses:")
    for question in test_questions:
        response = bot.chat(question)
        print(f"\n👤 User: {response['user_message']}")
        print(f"🤖 Bot: {response['bot_response']}")
        print(f"   Confidence: {response['confidence']:.2%}")