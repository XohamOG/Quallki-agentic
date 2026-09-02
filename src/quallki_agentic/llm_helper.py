from __future__ import annotations

import json
import os
from quallki_agentic.config import Settings

def invoke_gemini(prompt: str) -> dict[str, object] | None:
    settings = Settings.from_env()
    
    # Try NVIDIA first
    llm = None
    if os.getenv("NVIDIA_API_KEY"):
        try:
            from langchain_nvidia_ai_endpoints import ChatNVIDIA
            llm = ChatNVIDIA(
                model="nvidia/nemotron-3-ultra-550b-a55b",
                nvidia_api_key=os.environ["NVIDIA_API_KEY"],
                temperature=0.0
            )
        except Exception as e:
            print(f"Failed to load NVIDIA LLM: {e}")
            llm = None

    # Fallback to Gemini
    if not llm and settings.use_gemini and os.getenv("GEMINI_API_KEY"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=os.environ["GEMINI_API_KEY"],
                temperature=0.0,
            )
        except Exception as e:
            print(f"Failed to load Gemini LLM: {e}")
            llm = None
            
    if not llm:
        return None
        
    try:
        raw = str(llm.invoke(prompt).content).strip()
        start, end = raw.find("{"), raw.rfind("}")
        if start == -1 or end == -1:
            return None
            
        import ast
        try:
            parsed = json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(raw[start : end + 1])
            except (SyntaxError, ValueError):
                return None
                
        if isinstance(parsed, dict):
            return parsed
        return None
    except Exception as e:
        print(f"LLM extraction error: {e}")
        return None
