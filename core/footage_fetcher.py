import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Swap Rate killer prompts - 0-3s me hook
SYSTEM_PROMPT = """You are a viral YouTube Shorts scriptwriter. Your ONLY job: 0-3 second retention.

RULES:
1. First line = Pattern interrupt. NO "Did you know", "Have you ever", "Welcome".
   Use: "Stop.", "Wait.", "They lied to you.", "This will be deleted..."
2. Total script: 26-28 seconds only. 65-70 words max.
3. Every 3 seconds = new hook. Use: "But here's the crazy part...", "Wait, it gets worse...", "Part 2?"
4. Last line = Comment bait: "Comment 'PART2' if you want the secret" OR "Tag someone who does this"
5. Write for 12 year old. Simple words. Short sentences.
6. Output JSON only.

JSON Format:
{
  "title": "Curiosity gap, 40-50 chars",
  "script": "Full script 65-70 words",
  "thumbnail_text": "3 words max",
  "search_terms": ["term1", "term2", "term3"],
  "hook_score": 8-10,
  "comment_bait": "Exact line to say at end"
}
"""

NICHE_PROMPTS = {
    'mystery': """
Niche: Unsolved mysteries, government secrets, creepy facts
Hook examples: "The FBI deleted this video...", "Stop scrolling. This is illegal to know...", "They don't want you to see part 2..."
Tone: Whisper, suspense, conspiracy
""",
    'science': """
Niche: Mind-blowing science, space, physics that breaks brain
Hook examples: "Your teacher lied about this...", "Scientists are hiding this...", "This breaks physics..."
Tone: Excited, fast, "no way" moments
""",
    'human_behaviour': """
Niche: Psychology, why we do weird things, social hacks
Hook examples: "You do this daily but why?", "Tag someone who does this", "Psychology says you're..."
Tone: Relatable, "omg that's me", conversational
"""
}

def generate_script(topic, hook_data, niche='human_behaviour'):
    niche_context = NICHE_PROMPTS.get(niche, NICHE_PROMPTS['human_behaviour'])

    user_prompt = f"""
Topic: {topic}
Hook to use: {hook_data['hook']}
Niche rules: {niche_context}

Write the full 28-second script now. Make sure:
1. First 3 words = hook_data['hook']
2. 10 second mark = "But here's the crazy part..."
3. 20 second mark = "Wait, there's more..."
4. 27 second mark = comment_bait
5. Total 65-70 words only. Count them.

Give JSON only.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Best for creativity
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.9, # High creativity for hooks
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        # Validation - Swap rate fix
        words = data['script'].split()
        if len(words) > 75:
            data['script'] = ' '.join(words[:70]) # Hard cut at 70 words

        # Force comment bait agar missing hai
        if 'comment_bait' not in data:
            data['comment_bait'] = "Comment 'PART2' for the secret"

        # Script ke end me comment bait jod do
        if data['comment_bait'] not in data['script']:
            data['script'] = data['script'].rstrip('.') + f"... {data['comment_bait']}"

        data['topic'] = topic
        data['niche'] = niche
        data['hook_score'] = data.get('hook_score', 9)

        print(f"[Content] ✅ Script: {len(words)} words | Hook: {data['hook_score']}/10")
        return data

    except Exception as e:
        print(f"[Content] Groq failed: {e}")
        # Fallback template - Swap rate proof
        fallback = {
            'mystery': {
                "title": "The FBI Hid This From You",
                "script": "Stop. The FBI deleted this video in 24 hours. In 1997, they found something in Area 51. But here's the crazy part... it was alive. Wait, there's more... they still hide it today. Comment 'PART2' if you want the truth.",
                "thumbnail_text": "FBI HID THIS",
                "search_terms": ["dark fbi", "area 51", "classified"],
                "hook_score": 9,
                "comment_bait": "Comment 'PART2' if you want the truth"
            },
            'science': {
                "title": "Your Teacher Lied About Space",
                "script": "Wait. Your teacher lied about space. It's not empty. NASA found sound in space. But here's the crazy part... it screams. Wait, there's more... black holes sing. Tag someone who needs to know this.",
                "thumbnail_text": "SPACE SCREAMS",
                "search_terms": ["space nasa", "black hole", "galaxy"],
                "hook_score": 9,
                "comment_bait": "Tag someone who needs to know this"
            },
            'human_behaviour': {
                "title": "Why You Check Phone 144 Times",
                "script": "Stop. You check your phone 144 times daily. But why? Psychology says it's dopamine addiction. But here's the crazy part... it's worse than cigarettes. Wait, there's more... your brain is rewired. Comment 'ME' if this is you.",
                "thumbnail_text": "144 TIMES",
                "search_terms": ["phone addiction", "brain dopamine", "people"],
                "hook_score": 10,
                "comment_bait": "Comment 'ME' if this is you"
            }
        }
        result = fallback.get(niche, fallback['human_behaviour'])
        result['topic'] = topic
        result['niche'] = niche
        return result
