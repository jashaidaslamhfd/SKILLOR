from groq import Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_script(niche):
    prompt = f"""
    Act as a Baby Psychologist. Write a {niche} YouTube Short script.
    RULES FOR ANTI-SPAM + HIGH RETENTION:
    1. Duration: 40-55 seconds only.
    2. Hook Line 1: Start with a shocking question. Ex: "Your baby forgets your face in 2 seconds?"
    3. No Emoji. No CAPS SPAM. Sound 100% human.
    4. End with CTA: "Comment if this happened. Subscribe for Part 2."
    5. Break into 9-11 short scenes for images.
    Return JSON: {{"title": "...", "duration": 48, "scenes": ["scene1", "scene2"], "voiceover": "full text"}}
    """
    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], response_format={"type":"json_object"})
    return json.loads(resp.choices[0].message.content)
