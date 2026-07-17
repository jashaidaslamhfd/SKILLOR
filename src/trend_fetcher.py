"""Trend Fetcher Module for SKILLOR Pipeline
Fetches trending topics from Google Trends, YouTube, and Reddit.
"""
from __future__ import annotations

import os
import json
import time
import random
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta

import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

# High-performing niches for YouTube Shorts (2026)
HIGH_PERFORMING_NICHES = [
    "human_body", "brain", "health", "psychology", "science",
    "space", "technology", "history", "animals", "nature",
    "mystery", "crime", "finance", "motivation", "relationships"
]

# Trending topic templates (proven to get views)
TRENDING_TEMPLATES = {
    "human_body": [
        "Your {organ} is hiding a secret that doctors don't tell you",
        "What happens to your body when you {action} every day",
        "The terrifying truth about your {organ} that 99% don't know",
        "Scientists discovered something disturbing inside your {organ}",
        "Your body does this every night and you have no idea",
        "The hidden organ that controls everything in your body",
        "Why your {organ} is slowly killing you without symptoms",
        "Ancient humans had a {organ} feature we lost - here's why",
    ],
    "brain": [
        "Your brain lies to you every {time_period} and here's the proof",
        "Scientists found a switch in your brain that controls {thing}",
        "What happens to your brain when you don't sleep for {hours} hours",
        "The dark secret your brain keeps from your consciousness",
        "Your brain makes decisions before you even know it",
        "Why you can't stop thinking about {thing} at night",
        "The brain chemical that makes you addicted to {thing}",
        "Your brain has a second hidden brain inside it",
    ],
    "health": [
        "Doctors don't want you to know this about {thing}",
        "The {food} in your kitchen is secretly {effect}",
        "Why {common_habit} is destroying your health",
        "This 30-second trick fixes {health_issue} instantly",
        "The hidden danger of {common_item} in your home",
        "Ancient remedy for {health_issue} that actually works",
        "Why doctors are quitting {treatment} and switching to this",
        "The vitamin deficiency that causes {symptom}",
    ],
    "psychology": [
        "Why you can't stop scrolling (the dark psychology)",
        "The personality trait that predicts your success",
        "Why narcissists always win - the psychology explained",
        "Your childhood determines your {thing} in adulthood",
        "The dark triad trait hidden in your personality",
        "Why you attract toxic people (it's not your fault)",
        "The psychological trick that makes anyone like you",
        "Your phone addiction is a trauma response",
    ],
    "science": [
        "Scientists just discovered {thing} and it changes everything",
        "The experiment that was too dangerous to publish",
        "What happens when you {action} in space",
        "The scientific reason you feel {emotion} right now",
        "Scientists found a new {thing} that shouldn't exist",
        "The physics trick that makes {thing} possible",
        "Why time moves slower when you {action}",
        "The scientific explanation for {phenomenon}",
    ],
    "space": [
        "NASA just found something terrifying on {planet}",
        "What happens if you fall into a black hole",
        "The sound space makes will give you nightmares",
        "Why astronauts can't see stars in space",
        "The planet where it rains diamonds",
        "What's inside a black hole according to physics",
        "The space anomaly that breaks all laws of physics",
        "Why the sun is actually white not yellow",
    ],
    "technology": [
        "AI just did something that wasn't supposed to be possible",
        "The hidden feature in your phone that spies on you",
        "Why your smart TV is watching you right now",
        "The technology that will replace smartphones in {years} years",
        "What happens to your data after you delete it",
        "The secret code hidden in every {device}",
        "Why self-driving cars are afraid of {thing}",
        "The AI that can read your thoughts now",
    ],
    "history": [
        "The ancient civilization that had electricity",
        "What they don't teach you about {historical_event}",
        "The historical figure who was actually {surprising_fact}",
        "Ancient people knew about {modern_thing} before us",
        "The lost technology of {ancient_civilization}",
        "Why historians are hiding the truth about {thing}",
        "The ancient text that predicted {modern_event}",
        "What really happened to {historical_mystery}",
    ],
    "animals": [
        "The animal that can survive in space",
        "Why {animal} is actually smarter than humans",
        "The terrifying predator that lives in your {place}",
        "Animals that can predict {natural_disaster}",
        "The animal that never dies naturally",
        "Why {animal} is the most dangerous creature on Earth",
        "The extinct animal that scientists are bringing back",
        "Animals that have a sixth sense humans lost",
    ],
    "mystery": [
        "The unsolved mystery that even FBI can't crack",
        "What really happened at {mysterious_place}",
        "The disappearance that makes no sense",
        "The object found in {place} that shouldn't exist",
        "The mystery that scientists gave up trying to solve",
        "What the government is hiding about {thing}",
        "The ancient mystery that was just solved (terrifying)",
        "The phenomenon that breaks all logic",
    ],
}

# Fill-in values for templates
FILL_VALUES = {
    "organ": ["heart", "brain", "liver", "lungs", "stomach", "kidneys", "skin", "eyes"],
    "action": ["sleep", "eat", "drink water", "exercise", "scroll phone", "dream"],
    "thing": ["love", "money", "success", "happiness", "fear", "time", "memory"],
    "time_period": ["3 seconds", "5 seconds", "minute", "hour", "night"],
    "hours": ["24", "48", "72", "96"],
    "food": ["salt", "sugar", "honey", "milk", "bread", "rice"],
    "effect": ["poisonous", "healing", "addictive", "toxic", "miraculous"],
    "common_habit": ["sitting", "scrolling", "snoring", "cracking knuckles", "holding sneeze"],
    "health_issue": ["back pain", "headache", "anxiety", "insomnia", "fatigue"],
    "common_item": ["toothbrush", "pillow", "phone", "microwave", "plastic bottle"],
    "symptom": ["fatigue", "brain fog", "anxiety", "weight gain", "hair loss"],
    "emotion": ["anxious", "sad", "angry", "tired", "restless"],
    "phenomenon": ["deja vu", "aurora borealis", "ball lightning", "spontaneous combustion"],
    "planet": ["Mars", "Jupiter", "Saturn", "Venus", "Neptune"],
    "years": ["5", "10", "15", "20", "30"],
    "device": ["WiFi router", "smartwatch", "laptop", "car key", "credit card"],
    "historical_event": ["the Titanic", "the Moon Landing", "the Pyramids", "the Ice Age"],
    "surprising_fact": ["a woman", "a child", "from the future", "an alien"],
    "modern_thing": ["electricity", "flight", "computers", "surgery", "satellites"],
    "ancient_civilization": ["Egypt", "Atlantis", "Maya", "Rome", "Greece"],
    "historical_mystery": ["Atlantis", "the Loch Ness Monster", "Bigfoot", "the Bermuda Triangle"],
    "animal": ["octopus", "crow", "dolphin", "elephant", "ant", "jellyfish"],
    "place": ["backyard", "ocean", "desert", "forest", "attic"],
    "natural_disaster": ["earthquakes", "tsunamis", "volcanoes", "storms"],
    "mysterious_place": ["Bermuda Triangle", "Area 51", "the Mariana Trench", "Easter Island"],
}


def _fill_template(template: str) -> str:
    """Fill in template placeholders with random values."""
    result = template
    for key, values in FILL_VALUES.items():
        placeholder = "{" + key + "}"
        if placeholder in result:
            result = result.replace(placeholder, random.choice(values))
    return result


def get_google_trends_topics() -> List[Dict]:
    """Fetch trending topics from Google Trends (via unofficial API)."""
    topics = []
    
    try:
        # Google Trends daily search trends (unofficial)
        url = "https://trends.google.com/trends/api/dailytrends"
        params = {
            "hl": "en-US",
            "tz": "-330",  # Pakistan timezone
            "geo": "PK",  # Pakistan (change to US for US trends)
            "ns": "15",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            # Parse the JSON response (Google Trends returns JSON with some prefix)
            text = response.text
            # Remove the first 6 characters which are ")]}',\n"
            if text.startswith(")]}"):
                text = text[6:]
            data = json.loads(text)
            
            for trend in data.get("default", {}).get("trendingSearchesDays", [{}])[0].get("trendingSearches", [])[:10]:
                title = trend.get("title", {}).get("query", "")
                if title:
                    topics.append({
                        "topic": title,
                        "source": "google_trends",
                        "title": title,
                    })
    except Exception as e:
        logger.warning(f"Google Trends fetch failed: {e}")
    
    return topics


def get_youtube_trending_topics() -> List[Dict]:
    """Fetch trending topics from YouTube (via unofficial endpoint)."""
    topics = []
    
    try:
        # YouTube trending page (unofficial)
        url = "https://www.youtube.com/feed/trending"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Extract video titles from the page
            titles = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"\}\]', response.text)
            for title in titles[:10]:
                # Clean up the title
                clean_title = title.replace("\\u0026", "&").replace("\\", "")
                if len(clean_title) > 10:
                    topics.append({
                        "topic": clean_title,
                        "source": "youtube_trending",
                        "title": clean_title,
                    })
    except Exception as e:
        logger.warning(f"YouTube trending fetch failed: {e}")
    
    return topics


def get_reddit_trending_topics() -> List[Dict]:
    """Fetch trending topics from Reddit (science, psychology, etc.)."""
    topics = []
    
    subreddits = ["science", "psychology", "technology", "space", "todayilearned"]
    
    for subreddit in subreddits:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json"
            headers = {
                "User-Agent": "SKILLOR-Bot/1.0"
            }
            params = {"limit": 5}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for post in data.get("data", {}).get("children", []):
                    title = post.get("data", {}).get("title", "")
                    if title and len(title) > 15:
                        topics.append({
                            "topic": title,
                            "source": f"reddit_r/{subreddit}",
                            "title": title,
                        })
        except Exception as e:
            logger.warning(f"Reddit r/{subreddit} fetch failed: {e}")
    
    return topics


def get_template_topics() -> List[Dict]:
    """Generate topics from proven templates."""
    topics = []
    
    for niche in HIGH_PERFORMING_NICHES:
        templates = TRENDING_TEMPLATES.get(niche, [])
        for template in random.sample(templates, min(2, len(templates))):
            filled = _fill_template(template)
            topics.append({
                "topic": filled,
                "source": f"template_{niche}",
                "title": filled,
            })
    
    return topics


def get_trending_topic(exclude: List[str] = None) -> str:
    """Get a trending topic from any available source.
    
    Priority:
    1. Google Trends (real-time data)
    2. YouTube Trending
    3. Reddit trending
    4. Template-based fallback
    """
    if exclude is None:
        exclude = []
    
    all_topics = []
    
    # Try Google Trends
    google_topics = get_google_trends_topics()
    all_topics.extend(google_topics)
    
    # Try YouTube Trending
    youtube_topics = get_youtube_trending_topics()
    all_topics.extend(youtube_topics)
    
    # Try Reddit
    reddit_topics = get_reddit_trending_topics()
    all_topics.extend(reddit_topics)
    
    # Always add template topics as backup
    template_topics = get_template_topics()
    all_topics.extend(template_topics)
    
    # Filter out excluded topics
    filtered = [t for t in all_topics if t["topic"] not in exclude]
    
    if not filtered:
        # Ultimate fallback
        fallback = random.choice(list(TRENDING_TEMPLATES.get("mystery", [])))
        return _fill_template(fallback)
    
    # Prefer real trends, but mix in templates for variety
    real_trends = [t for t in filtered if not t["source"].startswith("template")]
    
    if real_trends and random.random() < 0.6:
        # 60% chance to use real trend
        chosen = random.choice(real_trends)
    else:
        # 40% chance to use template
        chosen = random.choice(filtered)
    
    logger.info(f"Selected topic from {chosen['source']}: {chosen['topic']}")
    return chosen["topic"]


if __name__ == "__main__":
    # Test the trend fetcher
    print("Fetching trending topics...")
    topic = get_trending_topic()
    print(f"\nSelected topic: {topic}")
