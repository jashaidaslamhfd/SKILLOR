import os
import json
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_script(topic: str) -> dict:
    """
    Groq API se USA audience ke liye English script banata hai
    """
    if not os.environ.get("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY missing hai. GitHub Secrets check karo.")

    prompt = f"""
    You are a viral YouTube Shorts scriptwriter for a USA audience.
    Topic: "{topic}".
    Write a 50-60 second, high-retention, fast-paced script in ENGLISH ONLY.
    Use a strong hook in the first 3 seconds.
    Output ONLY valid JSON: {{"title": "...", "voiceover": "...", "scenes": ["...", "...", "..."]}}
    Make 6-9 scenes for 9 images.
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-20b",
        response_format={"type": "json_object"},
        max_tokens=400
    )
    return json.loads(chat_completion.choices[0].message.content)
