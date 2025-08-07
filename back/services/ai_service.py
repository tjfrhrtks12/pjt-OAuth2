import openai
import google.generativeai as genai
from typing import Dict, List
from config import (
    AI_PROVIDER, 
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE,
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_MAX_TOKENS, GEMINI_TEMPERATURE
)

class AIService:
    """AI 서비스 통합 관리 클래스"""
    
    def __init__(self):
        self.provider = AI_PROVIDER.lower()
        self._setup_clients()
    
    def _setup_clients(self):
        """AI 클라이언트 설정"""
        if self.provider == "openai":
            if not OPENAI_API_KEY:
                raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        elif self.provider == "gemini":
            if not GEMINI_API_KEY:
                raise ValueError("Gemini API 키가 설정되지 않았습니다.")
            genai.configure(api_key=GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel(GEMINI_MODEL)
        else:
            raise ValueError(f"지원하지 않는 AI 제공자입니다: {self.provider}")
    
    def get_response(self, system_prompt: str, user_message: str) -> str:
        """AI 응답 생성"""
        try:
            if self.provider == "openai":
                return self._get_openai_response(system_prompt, user_message)
            elif self.provider == "gemini":
                return self._get_gemini_response(system_prompt, user_message)
            else:
                return "지원하지 않는 AI 제공자입니다."
        except Exception as e:
            print(f"AI 응답 생성 오류: {e}")
            return "죄송합니다. AI 응답 생성 중 오류가 발생했습니다."
    
    def _get_openai_response(self, system_prompt: str, user_message: str) -> str:
        """OpenAI 응답 생성"""
        response = self.openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=OPENAI_MAX_TOKENS,
            temperature=OPENAI_TEMPERATURE
        )
        return response.choices[0].message.content
    
    def _get_gemini_response(self, system_prompt: str, user_message: str) -> str:
        """Gemini 응답 생성"""
        # Gemini는 system prompt를 지원하지 않으므로 user message에 포함
        full_prompt = f"{system_prompt}\n\n사용자 질문: {user_message}"
        
        response = self.gemini_model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=GEMINI_MAX_TOKENS,
                temperature=GEMINI_TEMPERATURE
            )
        )
        return response.text
    
    def get_provider_info(self) -> Dict:
        """현재 AI 제공자 정보 반환"""
        if self.provider == "openai":
            return {
                "provider": "OpenAI",
                "model": OPENAI_MODEL,
                "max_tokens": OPENAI_MAX_TOKENS,
                "temperature": OPENAI_TEMPERATURE
            }
        elif self.provider == "gemini":
            return {
                "provider": "Gemini",
                "model": GEMINI_MODEL,
                "max_tokens": GEMINI_MAX_TOKENS,
                "temperature": GEMINI_TEMPERATURE
            }
        else:
            return {"provider": "Unknown"}

# 전역 AI 서비스 인스턴스
ai_service = AIService() 