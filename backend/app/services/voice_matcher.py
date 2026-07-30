"""
StreamGuard AI - Voice Matching Engine
Matches streamer's spoken words to displayed super chat text.
"""
import difflib
import re
import time
from typing import Tuple
from app.core.logging import get_logger

logger = get_logger(__name__)


class VoiceMatcher:
    """Fuzzy matches voice transcripts against super chat text."""

    # Reduced default threshold: speech-to-text is never a perfect transcript,
    # so 0.50 gives a good balance between precision and recall.
    def __init__(self, threshold: float = 0.50, cooldown_seconds: int = 5):
        self.threshold = threshold
        self.cooldown_seconds = cooldown_seconds
        self._last_match_time: float = 0.0
        self._transcript_buffer: str = ""

    def match(self, transcript: str, target_text: str) -> Tuple[bool, float]:
        """Check if voice transcript matches the target super chat text."""
        now = time.time()
        if now - self._last_match_time < self.cooldown_seconds:
            return False, 0.0

        norm_transcript = self._normalize(transcript)
        norm_target = self._normalize(target_text)

        if not norm_transcript or not norm_target:
            return False, 0.0

        full_sim = difflib.SequenceMatcher(None, norm_transcript, norm_target).ratio()
        keyword_score = self._keyword_overlap(norm_transcript, norm_target)
        best_score = max(full_sim, keyword_score)
        is_match = best_score >= self.threshold

        logger.debug(
            f"🎤 Voice check | heard: '{norm_transcript[:60]}' | "
            f"target: '{norm_target[:60]}' | "
            f"seq={full_sim:.2f} kw={keyword_score:.2f} best={best_score:.2f} "
            f"threshold={self.threshold:.2f} match={is_match}"
        )

        if is_match:
            self._last_match_time = now
            self._transcript_buffer = ""
            logger.info(f"🎤 Voice match! Score: {best_score:.2f} (heard: '{norm_transcript[:60]}')"
                        f" against '{norm_target[:60]}'")
        else:
            # Accumulate partial speech into a rolling buffer and re-check
            self._transcript_buffer = (self._transcript_buffer + " " + transcript).strip()
            buf_norm = self._normalize(self._transcript_buffer)
            buf_score = difflib.SequenceMatcher(None, buf_norm, norm_target).ratio()
            buf_kw = self._keyword_overlap(buf_norm, norm_target)
            buf_best = max(buf_score, buf_kw)
            logger.debug(f"🎤 Buffer check | buf='{buf_norm[:60]}' | best={buf_best:.2f}")
            if buf_best >= self.threshold:
                self._last_match_time = now
                self._transcript_buffer = ""
                logger.info(f"🎤 Buffer voice match! Score: {buf_best:.2f}")
                return True, buf_best

        return is_match, best_score

    def reset_buffer(self):
        self._transcript_buffer = ""

    def update_settings(self, threshold: float = None, cooldown: int = None):
        if threshold is not None:
            self.threshold = max(0.0, min(1.0, threshold))
        if cooldown is not None:
            self.cooldown_seconds = max(1, cooldown)

    @staticmethod
    def _normalize(text: str) -> str:
        """Lowercase, strip punctuation, collapse whitespace."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", "", text)  # strip punctuation
        return " ".join(text.split())

    @staticmethod
    def _keyword_overlap(transcript: str, target: str) -> float:
        """Fraction of meaningful target words found in transcript."""
        stop = {
            "the", "a", "an", "is", "are", "was", "to", "of", "in",
            "for", "on", "and", "or", "i", "you", "it", "my", "your",
            "this", "that", "with", "at", "by", "from", "up", "about",
            "into", "through", "be", "been", "have", "has", "had",
            "do", "did", "but", "so", "if", "we", "they", "he", "she",
        }
        t_words = {w for w in target.split() if w not in stop and len(w) > 2}
        tr_words = {w for w in transcript.split() if w not in stop and len(w) > 2}
        if not t_words:
            return 0.0
        matched = len(t_words & tr_words)
        return matched / len(t_words)
