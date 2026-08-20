from quallki_agentic.llm_helper import invoke_gemini

print("Testing Gemini...")
res = invoke_gemini("Return strict JSON with key 'test' and value 'hello'.")
print("Result:", res)
