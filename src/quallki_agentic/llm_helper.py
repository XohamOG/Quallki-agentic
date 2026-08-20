from __future__ import annotations

import json
import os
from quallki_agentic.config import Settings

def invoke_gemini(prompt: str) -> dict[str, object] | None:
    settings = Settings.from_env()
    
    if not settings.use_gemini or not os.getenv("GEMINI_API_KEY"):
        # For testing logs-only without GEMINI_API_KEY, we might want to return None
        # but the prompt assumes we use GEMINI. If it's disabled, we'll return None.
        # But wait, the user wants us to "ensure the respective agents can use my models".
        # We will assume GEMINI_API_KEY is provided or USE_GEMINI is true.
        return None
        
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=os.environ["GEMINI_API_KEY"],
            temperature=0,
        )
        
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
