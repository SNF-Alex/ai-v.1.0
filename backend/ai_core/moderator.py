"""
Content moderation and safety filtering
"""
import re
from typing import Tuple, List
from better_profanity import profanity
from ai_core.config import settings
from ai_core.logger import logger

# Initialize profanity filter
profanity.load_censor_words()


class ContentModerator:
    """Content moderation and safety checks"""
    
    def __init__(self):
        self.flagged_patterns = self._load_flagged_patterns()
    
    def _load_flagged_patterns(self) -> List[str]:
        """Load patterns of flagged content"""
        # Add patterns for harmful, illegal, or dangerous content
        patterns = [
            r'\b(how to (make|build|create) (bomb|weapon|explosive))\b',
            r'\b(illegal|drug|trafficking)\b',
            r'\b(hack|crack|steal)\b.*\b(password|account|data)\b',
            r'\b(child|minor).*\b(sexual|explicit|porn)\b',
        ]
        return patterns
    
    def check_content(self, text: str) -> Tuple[bool, str]:
        """
        Check if content should be flagged
        Returns: (is_flagged, reason)
        """
        if not settings.MODERATION_ENABLED:
            return False, ""
        
        text_lower = text.lower()
        
        # Check profanity
        if settings.PROFANITY_FILTER_ENABLED:
            if profanity.contains_profanity(text):
                logger.warning(f"Profanity detected in content")
                # Note: We may not want to flag for just profanity, just log it
                # return True, "Content contains inappropriate language"
        
        # Check dangerous patterns
        for pattern in self.flagged_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Flagged pattern detected: {pattern[:50]}")
                return True, "Content violates safety guidelines"
        
        # Length check
        if len(text) > 10000:
            return True, "Content too long"
        
        return False, ""
    
    def sanitize_content(self, text: str) -> str:
        """Sanitize content by removing profanity"""
        if settings.PROFANITY_FILTER_ENABLED:
            return profanity.censor(text)
        return text


# Singleton instance
moderator = ContentModerator()
