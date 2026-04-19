"""
🤖 FEATURE 8: AI Chatbot (NLP-based Q&A)
- Uses simple pattern matching + TF-IDF for Q&A
- Answers questions about water quality, health risks, and system usage
- Free & Open Source (scikit-learn, pandas)
"""

import json
import numpy as np
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
                'answer': 'Water pollution is the contamination of water bodies by harmful substances. It can be caused by industrial discharge, sewage, agricultural runoff, and natural events. Our system monitors key parameters like pH, turbidity, and microbiological contaminants.'
            },
            {
                'questions': [
                    'what are water-borne diseases',
                    'diseases from water',
                    'water borne illness'
                ],
                'answer': 'Water-borne diseases are illnesses transmitted through contaminated water. Common ones include cholera, typhoid, dysentery, and hepatitis A. They can be prevented through clean water access and good hygiene.'
            },
            {
                'questions': [
                    'how do i report health issues',
                    'submit health report',
                    'report symptoms'
                ],
                'answer': 'You can report health issues through our community health reporting system. Simply enter your symptoms, location, and date. This helps us identify early disease patterns.'
            },
            {
                'questions': [
                    'what is pH in water',
                    'explain pH',
                    'pH meaning'
                ],
                'answer': 'pH measures water acidity (0-14 scale). Neutral pH is 7. Safe drinking water typically has pH 6.5-8.5. Too acidic or alkaline water can indicate contamination.'
            },
            {
                'questions': [
                    'what is turbidity',
                    'explain turbidity',
                    'turbidity meaning'
                ],
                'answer': 'Turbidity measures water cloudiness caused by suspended particles. High turbidity (>5 NTU) indicates potential contamination and can shield harmful bacteria. Clear water is generally safer.'
            },
            {
                'questions': [
                    'how to prevent water-borne diseases',
                    'water safety tips',
                    'stay healthy water'
                ],
                'answer': '✅ Key Prevention Steps:\n1. Drink clean, treated water\n2. Maintain proper hygiene\n3. Wash hands regularly\n4. Boil water if uncertain\n5. Use public sanitation facilities\n6. Report contamination immediately'
            },
            {
                'questions': [
                    'what does your system do',
                    'how does system work',
                    'project overview'
                ],
                'answer': 'Our Water-Borne Disease Detection System uses machine learning to:\n1. Monitor water quality in real-time\n2. Predict disease outbreaks\n3. Analyze community health reports\n4. Generate public health alerts\n5. Support early intervention'
            },
            {
                'questions': [
                    'i have diarrhea',
                    'loose motions',
                    'digestive issue'
                ],
                'answer': '⚠️ If you have diarrhea:\n1. Stay hydrated with clean water\n2. Avoid contaminated food/water\n3. Practice good hygiene\n4. See doctor if severe or prolonged\n5. Report to health authorities if part of outbreak'
            },
            {
                'questions': [
                    'is my water safe',
                    'check water quality',
                    'water safe to drink'
                ],
                'answer': 'You can check if your water is safe by:\n1. Checking local water quality reports\n2. Using our system to test water parameters\n3. Looking for visible contamination\n4. Contacting local water authority\n5. In doubt, boil or use filtered water'
            }
        ]
    
    def _train_vectorizer(self):
        """Train TF-IDF vectorizer on all questions"""
        all_questions = []
        for qa in self.knowledge_base:
            all_questions.extend(qa['questions'])
        
        self.vectorizer.fit(all_questions)
    
    def find_best_answer(self, user_question, threshold=0.3):
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
        
        # Find best matching question in knowledge base
        for idx, qa in enumerate(self.knowledge_base):
            for question in qa['questions']:
                q_vec = self.vectorizer.transform([question])
                similarity = cosine_similarity(user_vec, q_vec)[0][0]
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_idx = idx
        
        if best_match_idx == -1:
            return {
                'answer': "I'm not sure about that. Could you please ask about water quality, health symptoms, or disease prevention?",
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
            return {'response': 'Please ask a question about water quality or health.'}
        
        result = self.find_best_answer(user_message)
        
        return {
            'user_message': user_message,
            'bot_response': result['answer'],
            'confidence': result['confidence'],
            'timestamp': pd.Timestamp.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    import pandas as pd
    
    chatbot = HealthAdvisorChatbot()
    
    # Test conversations
    test_questions = [
        "What is water pollution?",
        "I have diarrhea",
        "How to prevent disease?",
        "Is my water safe?",
        "Tell me about your system",
        "What is pH?"
    ]
    
    print("\n🤖 Chatbot Responses:")
    for question in test_questions:
        response = chatbot.chat(question)
        print(f"\n👤 User: {response['user_message']}")
        print(f"🤖 Bot: {response['bot_response']}")
        print(f"   Confidence: {response['confidence']:.2%}")