import os
import json
from groq import Groq
import torch
from kokoro import KPipeline
import subprocess

# Config load
with open('config/prompts.json') as f:
    PROMPTS = json.load(f)
with open('output/topic.json') as f:
    TOPIC_DATA = json.load(f)

client = Groq(api_key=os.environ['GROQ_API_KEY'])

# Kokoro init with am_adam - repo_id fix for your warning
pipeline = KPipeline(
    lang_code='a',
    repo_id='hexgrad/Kokoro-82M' # Ye warning fix karta hai
)

def generate_script():
    """Groq se 40-55s script banao with timing markers"""
    
    prompt = PROMPTS['script_prompt'].format(
        topic=TOPIC_DATA['topic'],
        hook=TOPIC_DATA['hook'],
        twist=TOPIC_DATA['twist']
    )
    
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    script_text = response.choices[0].message.content.strip()
    return script_text

def generate_voice_with_timing(script):
    """am_adam se voice + word timestamps - retention ke liye critical"""
    
    segments = []
    word_timings = []
    current_time = 0.0
    
    # Script ko segments me todo for emotion control
    sentences = script.replace('[PAUSE]', '|').split('|')
    
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Dynamic speed/pitch for USA retention
        if i == 0: # Hook
            speed, pitch = 1.15, +3
        elif 'scientists' in sentence.lower() or 'study' in sentence.lower():
            speed, pitch = 1.05, +1 # Science slow for trust
        elif sentence.startswith('But') or 'twist' in sentence.lower():
            speed, pitch = 1.2, +4 # Twist energetic
        else:
            speed, pitch = 1.12, +2 # Default
        
        # Kokoro generate with timestamps
        generator = pipeline(
            sentence, 
            voice='am_adam',
            speed=speed
        )
        
        for gs, ps, audio in generator:
            # Save audio segment
            segment_path = f'output/voice_seg_{i}.wav'
            torch.save(audio, segment_path)
            
            # Word timing nikal lo for caption sync
            for word in ps:
                word_timings.append({
                    'word': word['word'],
                    'start': current_time + word['start'],
                    'end': current_time + word['end']
                })
            
            duration = audio.shape[-1] / 24000 # 24khz sample rate
            segments.append(segment_path)
            current_time += duration + 0.05 # 0.05s gap, not 0.1s
    
    # Sare segments jodo
    concat_file = 'output/voice_list.txt'
    with open(concat_file, 'w') as f:
        for seg in segments:
            f.write(f"file '{seg}'\n")
    
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_file, '-c', 'copy', 'output/voice_final.wav'
    ])
    
    # Save timings for captions
    with open('output/word_timings.json', 'w') as f:
        json.dump(word_timings, f, indent=2)
    
    return 'output/voice_final.wav', word_timings, current_time

def generate_captions(word_timings):
    """Karaoke ASS captions - word by word highlight"""
    
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: BrainMystery,Arial Black,28,&H00FFFFFF,&H0000FFFF,&H00000000,&H99000000,-1,0,0,0,100,100,0,0,1,3,2,2,10,10,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    ass_events = []
    # Group words into lines - 3-4 words per line max
    lines = []
    current_line = []
    line_start = 0
    
    for i, word_data in enumerate(word_timings):
        if not current_line:
            line_start = word_data['start']
        
        current_line.append(word_data)
        
        # Line break logic: 4 words ya 1.5s ho gaye
        if len(current_line) >= 4 or word_data['end'] - line_start > 1.5:
            line_end = word_data['end']
            lines.append({'words': current_line, 'start': line_start, 'end': line_end})
            current_line = []
    
    if current_line: # Last line
        lines.append({'words': current_line, 'start': line_start, 'end': current_line[-1]['end']})
    
    # Karaoke effect - har word highlight
    for line in lines:
        text = ""
        for word in line['words']:
            duration_cs = int((word['end'] - word['start']) * 100) # centiseconds
            text += f"{{\\k{duration_cs}}}{word['word']} "
        
        start_time = format_ass_time(line['start'])
        end_time = format_ass_time(line['end'])
        ass_events.append(f"Dialogue: 0,{start_time},{end_time},BrainMystery,,0,0,0,,{text.strip()}")
    
    with open('output/captions.ass', 'w') as f:
        f.write(ass_header + '\n'.join(ass_events))
    
    return 'output/captions.ass'

def format_ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

if __name__ == "__main__":
    print("Generating script...")
    script = generate_script()
    
    with open('output/script.txt', 'w') as f:
        f.write(script)
    
    print("Generating am_adam voice with timing...")
    voice_path, timings, duration = generate_voice_with_timing(script)
    
    print(f"✅ Voice done: {duration:.1f}s")
    print("Generating karaoke captions...")
    captions_path = generate_captions(timings)
    
    # Save metadata
    metadata = {
        "script": script,
        "duration": duration,
        "voice": "am_adam",
        "timings_count": len(timings)
    }
    with open('output/script_meta.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("✅ File 2 complete")
