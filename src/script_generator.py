import os
import json
import time
from groq import Groq, BadRequestError

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_script(topic: str, max_retries: int = 3) -> dict:
    """
    Groq API se USA audience ke liye English script banata hai.
    Agar model invalid JSON de (reasoning models ke saath kabhi kabhi hota hai)
    ya request fail ho, to max_retries tak dobara try karta hai.
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

    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-20b",
                response_format={"type": "json_object"},
                reasoning_effort="low",
                max_tokens=1500,
            )
            content = chat_completion.choices[0].message.content
            script_data = json.loads(content)

            if not all(k in script_data for k in ("title", "voiceover", "scenes")):
                raise ValueError("Response mein title/voiceover/scenes missing hai")

            return script_data

        except (BadRequestError, json.JSONDecodeError, ValueError) as e:
            last_error = e
            print(f"Script generation attempt {attempt}/{max_retries} fail hui: {e}")
            if attempt < max_retries:
                time.sleep(3 * attempt)  # 3s, 6s, 9s... backoff
            continue

    raise RuntimeError(f"Script generation {max_retries} attempts ke baad bhi fail hui: {last_error}")
