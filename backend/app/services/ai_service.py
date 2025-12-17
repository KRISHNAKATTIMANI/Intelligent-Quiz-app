import openai
from anthropic import Anthropic
import json
from typing import List, Dict, Optional
from flask import current_app
from better_profanity import profanity
import re


class LLMService:
    """Service for interacting with Large Language Models"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
    def _get_openai_client(self):
        """Lazy initialization of OpenAI client"""
        if not self.openai_client:
            api_key = current_app.config.get('OPENAI_API_KEY')
            current_app.logger.info(f"OpenAI API Key configured: {'Yes' if api_key else 'No'}")
            if api_key:
                current_app.logger.info(f"API Key starts with: {api_key[:20]}...")
                openai.api_key = api_key
                self.openai_client = openai
            else:
                current_app.logger.error("OpenAI API Key not found in configuration!")
        return self.openai_client
    
    def _get_anthropic_client(self):
        """Lazy initialization of Anthropic client"""
        if not self.anthropic_client:
            api_key = current_app.config.get('ANTHROPIC_API_KEY')
            if api_key:
                self.anthropic_client = Anthropic(api_key=api_key)
        return self.anthropic_client
    
    def generate_quiz_questions(
        self,
        topic: str,
        num_questions: int = 10,
        difficulty: str = 'Medium',
        question_type: str = 'MCQ',
        context: Optional[str] = None
    ) -> tuple[List[Dict], float]:
        """
        Generate quiz questions using LLM
        
        Args:
            topic: The topic to generate questions about
            num_questions: Number of questions to generate
            difficulty: Easy, Medium, or Hard
            question_type: MCQ, True/False, or Fill-in-the-Blank
            context: Optional context text from file upload
            
        Returns:
            (questions_list, confidence_score)
        """
        prompt = self._build_question_generation_prompt(
            topic, num_questions, difficulty, question_type, context
        )
        
        try:
            # Try OpenAI first
            response = self._call_openai(prompt)
            if response:
                return self._parse_question_response(response, question_type)
            
            # Fallback to Anthropic
            response = self._call_anthropic(prompt)
            if response:
                return self._parse_question_response(response, question_type)
            
            return [], 0.0
            
        except Exception as e:
            current_app.logger.error(f"LLM generation error: {str(e)}")
            return [], 0.0
    
    def _build_question_generation_prompt(
        self,
        topic: str,
        num_questions: int,
        difficulty: str,
        question_type: str,
        context: Optional[str]
    ) -> str:
        """Build the prompt for question generation"""
        
        base_prompt = f"""You are an expert educator creating high-quality quiz questions.

Topic: {topic}
Difficulty Level: {difficulty}
Question Type: {question_type}
Number of Questions: {num_questions}

"""
        
        if context:
            base_prompt += f"""Context Material:
{context[:3000]}  # Limit context to avoid token limits

"""
        
        if question_type == 'MCQ':
            base_prompt += """Generate multiple-choice questions with 4 options each. Exactly ONE option should be correct.

Format your response as a JSON array:
[
  {
    "question_text": "What is the question?",
    "choices": [
      {"text": "Option A", "is_correct": false},
      {"text": "Option B", "is_correct": true},
      {"text": "Option C", "is_correct": false},
      {"text": "Option D", "is_correct": false}
    ],
    "explanation": "Why the correct answer is right",
    "confidence": 0.95
  }
]
"""
        elif question_type == 'True/False':
            base_prompt += """Generate True/False questions.

Format your response as a JSON array:
[
  {
    "question_text": "Statement to evaluate",
    "choices": [
      {"text": "True", "is_correct": false},
      {"text": "False", "is_correct": true}
    ],
    "explanation": "Why this is true/false",
    "confidence": 0.90
  }
]
"""
        else:  # Fill-in-the-Blank
            base_prompt += """Generate fill-in-the-blank questions. Use [BLANK] to mark where the answer goes.

Format your response as a JSON array:
[
  {
    "question_text": "The capital of France is [BLANK].",
    "correct_answer": "Paris",
    "explanation": "Paris is the capital and largest city of France",
    "confidence": 0.95
  }
]
"""
        
        base_prompt += f"""

Requirements:
1. Questions must be clear, unambiguous, and at {difficulty} difficulty level
2. Avoid questions that are too easy or that can be guessed
3. Ensure factual accuracy
4. Provide helpful explanations
5. Include confidence score (0.0-1.0) for each question
6. Make questions educational and engaging

Return ONLY the JSON array, no additional text.
"""
        
        return base_prompt
    
    def _call_openai(self, prompt: str) -> Optional[str]:
        """Call OpenAI API"""
        try:
            client = self._get_openai_client()
            if not client:
                return None
            
            response = client.chat.completions.create(
                model=current_app.config.get('LLM_MODEL', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "You are an expert educator creating quiz questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=current_app.config.get('LLM_TEMPERATURE', 0.7),
                max_tokens=current_app.config.get('MAX_TOKENS', 2000)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            current_app.logger.error(f"OpenAI API error: {str(e)}")
            return None
    
    def _call_anthropic(self, prompt: str) -> Optional[str]:
        """Call Anthropic Claude API"""
        try:
            client = self._get_anthropic_client()
            if not client:
                return None
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=current_app.config.get('MAX_TOKENS', 2000),
                temperature=current_app.config.get('LLM_TEMPERATURE', 0.7),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            current_app.logger.error(f"Anthropic API error: {str(e)}")
            return None
    
    def _parse_question_response(self, response: str, question_type: str) -> tuple[List[Dict], float]:
        """Parse LLM response into structured questions"""
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON array directly
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = response
            
            questions = json.loads(json_str)
            
            # Calculate average confidence
            confidences = [q.get('confidence', 0.7) for q in questions]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.7
            
            return questions, avg_confidence
            
        except json.JSONDecodeError as e:
            current_app.logger.error(f"Failed to parse LLM response: {str(e)}")
            return [], 0.0
    
    def generate_explanation(self, question_text: str, correct_answer: str, topic: str) -> str:
        """Generate an explanation for a question"""
        prompt = f"""Provide a clear, concise explanation for the following quiz question:

Question: {question_text}
Correct Answer: {correct_answer}
Topic: {topic}

Explain why this is the correct answer in 2-3 sentences. Be educational and helpful.
"""
        
        try:
            response = self._call_openai(prompt)
            if response:
                return response.strip()
            
            response = self._call_anthropic(prompt)
            if response:
                return response.strip()
            
            return "Explanation not available."
            
        except Exception as e:
            current_app.logger.error(f"Explanation generation error: {str(e)}")
            return "Explanation not available."


class ContentModerator:
    """Service for content moderation"""
    
    def __init__(self):
        profanity.load_censor_words()
    
    def check_profanity(self, text: str) -> tuple[bool, List[str]]:
        """
        Check text for profanity
        Returns: (contains_profanity, profane_words)
        """
        contains = profanity.contains_profanity(text)
        if contains:
            # Find specific profane words
            words = text.split()
            profane_words = [word for word in words if profanity.contains_profanity(word)]
            return True, profane_words
        return False, []
    
    def check_pii(self, text: str) -> tuple[bool, List[str]]:
        """
        Check text for Personally Identifiable Information
        Returns: (contains_pii, pii_types)
        """
        pii_found = []
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, text):
            pii_found.append('email')
        
        # Phone pattern (US format)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        if re.search(phone_pattern, text):
            pii_found.append('phone')
        
        # SSN pattern
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        if re.search(ssn_pattern, text):
            pii_found.append('ssn')
        
        # Credit card pattern
        cc_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        if re.search(cc_pattern, text):
            pii_found.append('credit_card')
        
        return len(pii_found) > 0, pii_found
    
    def moderate_content(self, text: str) -> Dict:
        """
        Perform full content moderation
        Returns: dict with moderation results
        """
        has_profanity, profane_words = self.check_profanity(text)
        has_pii, pii_types = self.check_pii(text)
        
        return {
            'is_safe': not (has_profanity or has_pii),
            'has_profanity': has_profanity,
            'profane_words': profane_words,
            'has_pii': has_pii,
            'pii_types': pii_types
        }


# Global instances
llm_service = LLMService()
content_moderator = ContentModerator()
