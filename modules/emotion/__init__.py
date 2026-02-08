"""Emotion Module"""
from modules.emotion.detector import EmotionDetector, get_emotion_detector
from modules.emotion.zone_mapper import ZoneMapper, get_zone_mapper

__all__ = [
    "EmotionDetector",
    "get_emotion_detector",
    "ZoneMapper",
    "get_zone_mapper"
]
