import logging
import re
from typing import Dict, List
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QualityChecker:
    """Comprehensive quality checking system to reduce swap rate."""
    
    def __init__(self):
        self.hook_threshold = 0.8
        self.engagement_threshold = 0.75
        self.pacing_threshold = 0.8
    
    def check_script_quality(self, script_data: Dict) -> Dict:
        """
        Comprehensive script quality check.
        
        Returns dict with scores for different aspects.
        """
        scores = {}
        issues = []
        
        # 1. Hook effectiveness (0-100)
        hook_score = self._score_hook(script_data.get('hook', ''))
        scores['hook_score'] = hook_score
        if hook_score < 70:
            issues.append(f"❌ Weak hook ({hook_score}/100) - Add urgency in first 3 seconds")
        
        # 2. Engagement potential (0-100)
        engagement_score = self._score_engagement(script_data.get('voiceover', ''))
        scores['engagement_score'] = engagement_score
        if engagement_score < 65:
            issues.append(f"⚠️ Low engagement potential ({engagement_score}/100) - Add more emotional triggers")
        
        # 3. Pacing analysis
        pacing_score, pacing_issues = self._analyze_pacing(script_data.get('voiceover', ''))
        scores['pacing_score'] = pacing_score
        issues.extend(pacing_issues)
        
        # 4. CTA effectiveness
        cta_score = self._score_cta(script_data.get('voiceover', ''))
        scores['cta_score'] = cta_score
        if cta_score < 60:
            issues.append(f"⚠️ Weak CTA ({cta_score}/100) - Add clear call-to-action")
        
        # 5. Keyword diversity (anti-spam)
        keyword_score = self._check_keyword_diversity(script_data)
        scores['keyword_diversity'] = keyword_score
        
        # 6. Overall quality score
        overall_score = sum(scores.values()) / len(scores)
        scores['overall_quality'] = overall_score
        
        return {
            'scores': scores,
            'issues': issues,
            'approved': overall_score >= 75,
            'recommendation': self._get_recommendation(overall_score, issues)
        }
    
    def _score_hook(self, hook: str) -> float:
        """Score hook effectiveness (0-100)."""
        if not hook or len(hook) < 10:
            return 0
        
        score = 50  # Base score
        
        # Check for question (powerful hook)
        if '?' in hook:
            score += 15
        
        # Check for curiosity gap
        curiosity_triggers = [
            'don\'t know', 'doesn\'t know', 'myth', 'truth', 'shocking', 
            'secret', 'discovered', 'most people', 'never knew'
        ]
        if any(trigger in hook.lower() for trigger in curiosity_triggers):
            score += 20
        
        # Check for power words
        power_words = [
            'proven', 'science', 'expert', 'revealed', 'breakthrough',
            'hidden', 'trick', 'hack', 'amazing', 'incredible'
        ]
        if any(word in hook.lower() for word in power_words):
            score += 15
        
        # Check length (ideal: 8-15 words)
        word_count = len(hook.split())
        if 8 <= word_count <= 15:
            score += 10
        elif word_count < 8:
            score -= 10
        
        return min(score, 100)
    
    def _score_engagement(self, voiceover: str) -> float:
        """Score engagement potential (0-100)."""
        if not voiceover:
            return 0
        
        score = 50  # Base score
        text_lower = voiceover.lower()
        
        # Emotional triggers
        emotional_words = [
            'worried', 'concerned', 'discovered', 'amazing', 'shocking',
            'surprised', 'important', 'critical', 'develop', 'healthy'
        ]
        emotional_count = sum(1 for word in emotional_words if word in text_lower)
        score += min(emotional_count * 3, 25)
        
        # Action words (verbs)
        action_words = ['discover', 'learn', 'try', 'implement', 'follow', 'watch']
        action_count = sum(1 for word in action_words if word in text_lower)
        score += min(action_count * 2, 15)
        
        # Numbers and specificity
        numbers = re.findall(r'\d+', voiceover)
        if len(numbers) >= 2:
            score += 10
        
        # Questions
        questions = voiceover.count('?')
        if questions >= 1:
            score += 5
        
        return min(score, 100)
    
    def _analyze_pacing(self, voiceover: str) -> tuple:
        """Analyze script pacing - target video length is now 40-55 seconds
        (matches video_editor.py's TARGET_MIN_SEC/TARGET_MAX_SEC)."""
        if not voiceover:
            return 0, []
        
        issues = []
        
        # Rough estimate: average speaking rate ~150 words/min = 2.5 words/sec
        word_count = len(voiceover.split())
        estimated_duration = word_count / 2.5
        
        score = 100
        
        if estimated_duration < 35:
            score -= 20
            issues.append(f"❌ Script too short ({estimated_duration:.0f}s) - Expand with more details")
        elif estimated_duration > 60:
            score -= 20
            issues.append(f"⚠️ Script too long ({estimated_duration:.0f}s) - Edit down to 40-55s")
        elif estimated_duration < 40:
            score -= 10
            issues.append(f"⚠️ Script slightly short ({estimated_duration:.0f}s) - Add depth")
        elif estimated_duration > 55:
            score -= 10
            issues.append(f"⚠️ Script slightly long ({estimated_duration:.0f}s) - Trim a bit")
        
        return score, issues
    
    def _score_cta(self, voiceover: str) -> float:
        """Score call-to-action strength (0-100)."""
        if not voiceover:
            return 0
        
        score = 40  # Base score
        text_lower = voiceover.lower()
        
        # Strong CTAs
        strong_ctas = [
            'subscribe', 'comment', 'share', 'like', 'follow',
            'save this', 'tag someone', 'send to'
        ]
        if any(cta in text_lower for cta in strong_ctas):
            score += 40
        
        # Urgency
        urgency_words = ['now', 'today', 'immediately', 'don\'t miss', 'limited']
        if any(word in text_lower for word in urgency_words):
            score += 10
        
        # Question-based CTA
        if '?' in voiceover[-50:]:
            score += 10
        
        return min(score, 100)
    
    def _check_keyword_diversity(self, script_data: Dict) -> float:
        """Check keyword diversity to prevent spam flagging (0-100)."""
        text = (script_data.get('title', '') + ' ' + 
                script_data.get('voiceover', '')).lower()
        
        # Get all words
        words = re.findall(r'\b\w+\b', text)
        total_words = len(words)
        
        if total_words == 0:
            return 0
        
        # Count unique words
        unique_words = len(set(words))
        diversity = (unique_words / total_words) * 100
        
        # Look for repetitive keywords
        word_counts = Counter(words)
        most_common = word_counts.most_common(5)
        
        # Flag if any word appears too often
        for word, count in most_common:
            if len(word) > 4 and count > total_words * 0.15:
                # Word appears too frequently
                diversity -= 15
        
        return max(min(diversity, 100), 0)
    
    def _get_recommendation(self, overall_score: float, issues: List[str]) -> str:
        """Get overall recommendation based on quality score."""
        if overall_score >= 85:
            return "🟢 APPROVED - Ready to publish"
        elif overall_score >= 75:
            return "🟡 APPROVED WITH NOTES - Minor improvements suggested"
        elif overall_score >= 65:
            return "🟡 NEEDS REVISION - Address issues before publishing"
        else:
            return "🔴 REJECTED - Significant improvements needed"
    
    def check_for_plagiarism(self, current_script: Dict, previous_scripts: List[Dict]) -> Dict:
        """
        Simple plagiarism detection by comparing with previous scripts.
        """
        if not previous_scripts:
            return {'plagiarism_risk': 'low', 'similarity_score': 0}
        
        current_title = current_script.get('title', '').lower()
        current_voiceover = current_script.get('voiceover', '').lower()
        
        max_similarity = 0
        
        for prev_script in previous_scripts[-5:]:  # Check last 5 videos
            prev_title = prev_script.get('title', '').lower()
            prev_voiceover = prev_script.get('voiceover', '').lower()
            
            # Title similarity
            title_similarity = self._calculate_similarity(current_title, prev_title)
            
            # Content similarity
            content_similarity = self._calculate_similarity(current_voiceover, prev_voiceover)
            
            overall_similarity = (title_similarity * 0.3) + (content_similarity * 0.7)
            max_similarity = max(max_similarity, overall_similarity)
        
        risk = 'high' if max_similarity > 0.7 else ('medium' if max_similarity > 0.5 else 'low')
        
        return {
            'plagiarism_risk': risk,
            'similarity_score': max_similarity,
            'recommendation': 'Rewrite sections' if risk == 'high' else ('Minor changes' if risk == 'medium' else 'Ready')
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple word overlap."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0


if __name__ == "__main__":
    checker = QualityChecker()
    
    # Test script
    test_script = {
        'title': 'Why Babies Need Crawling',
        'hook': 'Most parents don\'t know this shocking truth about crawling',
        'voiceover': '''Scientists discovered something amazing about baby crawling. 
        Babies who crawl develop 30% stronger neural connections. Here\'s why: 
        crawling activates both sides of the brain simultaneously. This creates 
        better coordination and cognitive skills. If your baby skips crawling, 
        they might struggle later. Today, we\'ll show you how to encourage crawling. 
        Save this video - you\'ll need it!'''
    }
    
    result = checker.check_script_quality(test_script)
    print("Quality Check Results:")
    print(json.dumps(result, indent=2))
