import os
import json
import requests
from datetime import datetime
from groq import Groq

# Config load karo
with open('config/prompts.json') as f:
    PROMPTS = json.load(f)
with open('config/usa_keywords.json') as f:
    KEYWORDS = json.load(f)

client = Groq(api_key=os.environ['GROQ_API_KEY'])

def check_topic_used(topic):
    """Purana topic dobara na aaye - anti spam"""
    try:
        with open('config/used_topics.json', 'r') as f:
            used = json.load(f)
        return topic.lower() in [t.lower() for t in used]
    except:
        return False

def save_topic(topic):
    """Topic save karo taake repeat na ho"""
    try:
        with open('config/used_topics.json', 'r') as f:
            used = json.load(f)
    except:
        used = []
    used.append(topic)
    with open('config/used_topics.json', 'w') as f:
        json.dump(used[-100:], f) # Last 100 yaad rakho

def generate_topic():
    """Groq se USA optimized topic + hook"""
    
    # Step 1: Topic generate
    topic_prompt = PROMPTS['topic_prompt'] + f"\nHigh CTR words to use: {KEYWORDS['high_ctr']}"
    
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": topic_prompt}],
        temperature=0.9 # Creative topics
    )
    topic = response.choices[0].message.content.strip().replace('"', '')
    
    # Anti-spam check
    if check_topic_used(topic):
        print(f"Topic repeated: {topic}. Generating new...")
        return generate_topic() # Retry
    
    # Step 2: 6-word hook generate
    hook_prompt = PROMPTS['hook_prompt'] + f"\nTopic: {topic}"
    
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": hook_prompt}],
        temperature=0.8
    )
    hook = response.choices[0].message.content.strip()
    
    # Step 3: Twist generate for 35s mark
    twist_prompt = f"For YouTube Short about '{topic}', write 1 shocking twist for parents. 8 words max. Start with 'But'"
    
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": twist_prompt}],
        temperature=0.9
    )
    twist = response.choices[0].message.content.strip()
    
    save_topic(topic)
    
    output = {
        "topic": topic,
        "hook": hook,
        "twist": twist,
        "timestamp": datetime.now().isoformat(),
        "target": "USA",
        "duration_target": "40-55s"
    }
    
    with open('output/topic.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Topic Generated: {topic}")
    print(f"✅ Hook: {hook}")
    print(f"✅ Twist: {twist}")
    return output

if __name__ == "__main__":
    os.makedirs('output', exist_ok=True)
    generate_topic()
