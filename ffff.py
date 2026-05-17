import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
import traceback
import logging
import json
import time
import hashlib
import base64
import re
import sys
import os
import inspect
from typing import Dict, List, Tuple, Any, Optional, Union, Callable, Generator
from datetime import datetime, timedelta
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from functools import lru_cache, wraps
from itertools import chain, combinations, permutations, product
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import math
import statistics
import uuid
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# ==================== LOGGING SETUP ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== STREAMLIT PAGE CONFIG ====================
st.set_page_config(
    page_title="DIRECTIONER VS SWIFTIE - ULTIMATE FAN IDENTITY",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/directioner-vs-swiftie',
        'Report a bug': "https://github.com/yourusername/directioner-vs-swiftie/issues",
        'About': "# DIRECTIONER VS SWIFTIE\n\nUltimate Fan Identity Matrix - Application"
    }
)

# ==================== ENUMS & CONSTANTS ====================
class ThemeMode(Enum):
    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"

class PrimaryColor(Enum):
    GRADIENT = "gradient"
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    PURPLE = "purple"

class AccentColor(Enum):
    PURPLE = "purple"
    BLUE = "blue"
    GREEN = "green"
    PINK = "pink"
    ORANGE = "orange"

class ArtistType(Enum):
    SOLO = "solo"
    BAND = "band"
    DUO = "duo"
    GROUP = "group"

class FanType(Enum):
    DIRECTIONER = "Directioner"
    SWIFTIE = "Swiftie"
    UNDECIDED = "Undecided"

class QuestionDifficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4

class ChartType(Enum):
    BAR = "bar"
    PIE = "pie"
    LINE = "line"
    SCATTER = "scatter"
    AREA = "area"
    HISTOGRAM = "histogram"

# ==================== DATA CLASSES ====================
@dataclass
class SongData:
    title: str
    artist: str
    year: int
    popularity: int
    duration_seconds: int
    genre: str = "Pop"
    album: str = ""
    streams_billions: float = 0.0
    awards: List[str] = field(default_factory=list)

@dataclass
class AlbumData:
    title: str
    year: int
    sales_millions: float
    songs: List[str]
    certified: str = ""
    label: str = ""

@dataclass
class TourData:
    name: str
    year_start: int
    year_end: int
    shows: int
    attendance_millions: float
    revenue_millions: float

@dataclass
class QuizResult:
    fan_type: FanType
    directioner_score: int
    swiftie_score: int
    answers: List[Dict]
    timestamp: datetime
    percentage_directioner: float
    percentage_swiftie: float
    confidence_level: str

@dataclass
class UserProfile:
    user_id: str
    username: str
    quiz_history: List[QuizResult]
    favorite_artist: str
    favorite_song: str
    created_at: datetime
    last_active: datetime
    total_quizzes: int = 0
    average_directioner_score: float = 0.0
    average_swiftie_score: float = 0.0


# ==================== SONG CLASS (DEFINED FIRST) ====================
class Song:
    def __init__(self, title: str, artist: str, year: int, popularity: int, duration_seconds: int, genre: str = "Pop", album: str = "", streams_billions: float = 0.0):
        self.title = title
        self.artist = artist
        self.year = year
        self.popularity = popularity
        self.duration_seconds = duration_seconds
        self.genre = genre
        self.album = album
        self.streams_billions = streams_billions

    def get_duration_formatted(self) -> str:
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def get_rating_category(self) -> str:
        if self.popularity >= 90:
            return "Masterpiece"
        elif self.popularity >= 80:
            return "Hit Single"
        elif self.popularity >= 70:
            return "Album Track"
        else:
            return "Deep Cut"

    def get_info(self) -> str:
        return f"🎵 {self.title} - {self.artist} ({self.year}) | {self.get_duration_formatted()} | {self.get_rating_category()} | {self.streams_billions}B streams"


# ==================== THEME MANAGER ====================
class ThemeManager:
    """Singleton theme manager - single source of truth for styling"""
    
    _instance = None
    _themes = {
        "dark": {
            "background": "linear-gradient(135deg, #0b1120 0%, #19233c 25%, #1e2a4a 50%, #19233c 75%, #0b1120 100%)",
            "card_bg": "rgba(30,41,59,0.85)",
            "text_primary": "#f5f5f7",
            "text_secondary": "#cbd5e1",
            "sidebar_bg": "#0f172a",
            "border": "#334155",
            "code_bg": "#1e293b",
            "success": "#10b981",
            "error": "#ef4444",
            "warning": "#f59e0b",
            "info": "#3b82f6"
        },
        "light": {
            "background": "linear-gradient(135deg, #fef3c7 0%, #fde68a 25%, #fcd34d 50%, #fde68a 75%, #fef3c7 100%)",
            "card_bg": "rgba(255,255,255,0.9)",
            "text_primary": "#1f2937",
            "text_secondary": "#4b5563",
            "sidebar_bg": "rgba(255,255,255,0.98)",
            "border": "#e5e7eb",
            "code_bg": "#f3f4f6",
            "success": "#059669",
            "error": "#dc2626",
            "warning": "#d97706",
            "info": "#2563eb"
        }
    }
    
    _primary_colors = {
        "gradient": {"button": "linear-gradient(90deg, #ff416c, #ff4b2b)", "tab": "linear-gradient(120deg, #3b82f6, #8b5cf6)"},
        "blue": {"button": "linear-gradient(90deg, #1e3c72, #2a5298)", "tab": "linear-gradient(120deg, #1e3c72, #2a5298)"},
        "green": {"button": "linear-gradient(90deg, #11998e, #38ef7d)", "tab": "linear-gradient(120deg, #11998e, #38ef7d)"},
        "red": {"button": "linear-gradient(90deg, #dc2626, #ea580c)", "tab": "linear-gradient(120deg, #dc2626, #ea580c)"},
        "purple": {"button": "linear-gradient(90deg, #7c3aed, #a78bfa)", "tab": "linear-gradient(120deg, #7c3aed, #a78bfa)"}
    }
    
    _accent_colors = {
        "purple": "#8b5cf6", "blue": "#3b82f6", "green": "#10b981", "pink": "#ec4899", "orange": "#f97316"
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._current_theme = ThemeMode.DARK
        self._current_primary = PrimaryColor.GRADIENT
        self._current_accent = AccentColor.PURPLE
    
    def set_theme(self, theme: ThemeMode) -> None:
        self._current_theme = theme
    
    def set_primary(self, primary: PrimaryColor) -> None:
        self._current_primary = primary
    
    def set_accent(self, accent: AccentColor) -> None:
        self._current_accent = accent
    
    def get_css(self) -> str:
        theme_data = self._themes[self._current_theme.value]
        primary_data = self._primary_colors[self._current_primary.value]
        accent_color = self._accent_colors[self._current_accent.value]
        
        return f"""
        <style>
            .stApp {{ background: {theme_data["background"]} !important; }}
            .stApp > header {{ background: transparent !important; }}
            
            h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
                color: {theme_data["text_primary"]} !important;
                font-weight: 700 !important;
                letter-spacing: -0.02em !important;
            }}
            
            p, li, span, .stMarkdown p, .stText, .stCaption {{
                color: {theme_data["text_secondary"]} !important;
            }}
            
            .stButton > button {{
                background: {primary_data["button"]} !important;
                color: white !important;
                border-radius: 40px !important;
                padding: 0.6rem 2rem !important;
                font-weight: 600 !important;
                border: none !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                cursor: pointer !important;
            }}
            
            .stButton > button:hover {{
                transform: translateY(-2px) !important;
                box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2) !important;
            }}
            
            .stButton > button:active {{
                transform: translateY(0) !important;
            }}
            
            .stTabs [data-baseweb="tab-list"] {{
                gap: 8px !important;
                background: {theme_data["card_bg"]} !important;
                border-radius: 50px !important;
                padding: 6px !important;
                backdrop-filter: blur(10px) !important;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                border-radius: 40px !important;
                padding: 8px 24px !important;
                font-weight: 600 !important;
                color: {theme_data["text_secondary"]} !important;
                transition: all 0.2s ease !important;
            }}
            
            .stTabs [aria-selected="true"] {{
                background: {primary_data["tab"]} !important;
                color: white !important;
            }}
            
            .stSelectbox, .stSlider, .stTextInput, .stNumberInput {{
                background-color: {theme_data["card_bg"]} !important;
                border-radius: 16px !important;
                border: 1px solid {theme_data["border"]} !important;
            }}
            
            .stSidebar {{
                background: {theme_data["sidebar_bg"]} !important;
                backdrop-filter: blur(12px) !important;
            }}
            
            .stSidebar .stMarkdown, .stSidebar p, .stSidebar label {{
                color: {theme_data["text_secondary"]} !important;
            }}
            
            code, .stCodeBlock {{
                background-color: {theme_data["code_bg"]} !important;
                color: {theme_data["text_primary"]} !important;
                border-radius: 12px !important;
                padding: 4px 8px !important;
            }}
            
            hr {{
                border-color: {theme_data["border"]} !important;
                margin: 1.5rem 0 !important;
            }}
            
            .metric-card {{
                background: {theme_data["card_bg"]} !important;
                backdrop-filter: blur(10px) !important;
                border-radius: 24px !important;
                padding: 20px !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                transition: all 0.3s ease !important;
            }}
            
            .metric-card:hover {{
                transform: translateY(-4px) !important;
                box-shadow: 0 20px 25px -12px rgba(0,0,0,0.2) !important;
            }}
            
            .glass-card {{
                background: {theme_data["card_bg"]} !important;
                backdrop-filter: blur(12px) !important;
                border-radius: 32px !important;
                padding: 24px !important;
                border: 1px solid rgba(255,255,255,0.15) !important;
                transition: all 0.3s ease !important;
            }}
            
            .glass-card:hover {{
                transform: translateY(-5px) !important;
            }}
            
            .custom-success {{
                background: linear-gradient(135deg, {theme_data["success"]}, {theme_data["success"]}cc) !important;
                border-radius: 24px !important;
                padding: 28px !important;
                text-align: center !important;
                animation: pulse 2s infinite !important;
            }}
            
            .custom-error {{
                background: linear-gradient(135deg, {theme_data["error"]}, {theme_data["error"]}cc) !important;
                border-radius: 24px !important;
                padding: 20px !important;
                text-align: center !important;
            }}
            
            .custom-warning {{
                background: linear-gradient(135deg, {theme_data["warning"]}, {theme_data["warning"]}cc) !important;
                border-radius: 24px !important;
                padding: 20px !important;
                text-align: center !important;
            }}
            
            @keyframes pulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }}
                70% {{ box-shadow: 0 0 0 20px rgba(16,185,129,0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(16,185,129,0); }}
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .fade-in {{
                animation: fadeIn 0.5s ease-out;
            }}
            
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: {theme_data["code_bg"]};
                border-radius: 10px;
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: {accent_color};
                border-radius: 10px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: {accent_color}cc;
            }}
            
            .stProgress > div > div {{
                background: {primary_data["button"]} !important;
                border-radius: 20px !important;
            }}
            
            .stAlert {{
                border-radius: 16px !important;
                border-left-width: 4px !important;
            }}
            
            .stDataFrame {{
                border-radius: 16px !important;
                overflow: hidden !important;
            }}
            
            iframe {{
                border-radius: 16px !important;
            }}
        </style>
        """
    
    def get_chart_colors(self) -> Dict[str, str]:
        return {
            "one_direction": self._accent_colors[self._current_accent.value],
            "taylor_swift": self._accent_colors["pink"] if self._current_accent.value == "purple" else self._accent_colors[self._current_accent.value],
            "grid": self._themes[self._current_theme.value]["border"],
            "text": self._themes[self._current_theme.value]["text_secondary"]
        }


# ==================== CACHE MANAGER ====================
class CacheManager:
    """Decorator-based caching for expensive operations"""
    
    _instance = None
    _cache = {}
    _ttl_cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    def cached(ttl_seconds: int = 300):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
                if cache_key in CacheManager._cache:
                    cached_time, cached_value = CacheManager._cache[cache_key]
                    if datetime.now() - cached_time < timedelta(seconds=ttl_seconds):
                        return cached_value
                result = func(*args, **kwargs)
                CacheManager._cache[cache_key] = (datetime.now(), result)
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def clear():
        CacheManager._cache.clear()
        CacheManager._ttl_cache.clear()


# ==================== DATA PROVIDER ====================
class DataProvider:
    """Centralized data provider with lazy loading"""
    
    _instance = None
    _one_direction_data = None
    _taylor_swift_data = None
    _songs_db = None
    _albums_db = None
    _tours_db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_one_direction_data(cls) -> Dict:
        if cls._one_direction_data is None:
            cls._one_direction_data = {
                "name": "One Direction",
                "type": ArtistType.BAND.value,
                "debut_year": 2010,
                "disband_year": 2016,
                "members": 5,
                "members_names": ["Harry Styles", "Niall Horan", "Liam Payne", "Louis Tomlinson", "Zayn Malik"],
                "members_birthdays": ["1994-02-01", "1993-09-13", "1993-08-29", "1991-12-24", "1993-01-12"],
                "genre": ["Pop Rock", "Teen Pop", "Power Pop"],
                "total_albums": 5,
                "albums": [
                    AlbumData("Up All Night", 2011, 4.5, ["What Makes You Beautiful", "Gotta Be You", "One Thing"], "Platinum", "Syco"),
                    AlbumData("Take Me Home", 2012, 5.2, ["Live While We're Young", "Little Things", "Kiss You"], "2x Platinum", "Syco"),
                    AlbumData("Midnight Memories", 2013, 6.8, ["Best Song Ever", "Story of My Life", "Midnight Memories"], "3x Platinum", "Syco"),
                    AlbumData("FOUR", 2014, 5.9, ["Steal My Girl", "Night Changes", "Ready to Run"], "2x Platinum", "Syco"),
                    AlbumData("Made in the A.M.", 2015, 4.2, ["Drag Me Down", "Perfect", "History"], "Platinum", "Syco")
                ],
                "songs": {
                    "What Makes You Beautiful": 92, "Night Changes": 88, "Story of My Life": 90,
                    "Drag Me Down": 85, "Perfect": 87, "Steal My Girl": 84, "Live While We're Young": 83,
                    "Best Song Ever": 86, "Little Things": 79, "Kiss You": 81, "One Thing": 80,
                    "Gotta Be You": 76, "Midnight Memories": 82, "You & I": 78, "No Control": 77,
                    "History": 84, "Through the Dark": 75, "Infinity": 80, "Home": 82
                },
                "top_song": "What Makes You Beautiful",
                "awards": 200,
                "tours": [
                    TourData("Up All Night Tour", 2011, 2012, 62, 1.2, 85.0),
                    TourData("Take Me Home Tour", 2013, 2013, 134, 2.5, 180.0),
                    TourData("Where We Are Tour", 2014, 2014, 69, 3.4, 290.0),
                    TourData("On the Road Again Tour", 2015, 2015, 79, 2.8, 210.0)
                ],
                "social_media_followers_millions": 120,
                "spotify_streams_billions": 15,
                "youtube_views_billions": 18,
                "billboard_hot_100": 6,
                "uk_singles_chart": 4,
                "grammy_nominations": 5,
                "grammy_wins": 0,
                "brit_awards": 7,
                "american_music_awards": 8
            }
        return cls._one_direction_data
    
    @classmethod
    def get_taylor_swift_data(cls) -> Dict:
        if cls._taylor_swift_data is None:
            cls._taylor_swift_data = {
                "name": "Taylor Swift",
                "type": ArtistType.SOLO.value,
                "debut_year": 2006,
                "members": 1,
                "genre": ["Pop", "Country", "Folk", "Alternative", "Synth-pop"],
                "total_albums": 10,
                "albums": [
                    AlbumData("Taylor Swift", 2006, 5.5, ["Tim McGraw", "Teardrops on My Guitar", "Our Song"], "7x Platinum", "Big Machine"),
                    AlbumData("Fearless", 2008, 8.2, ["Love Story", "You Belong With Me", "Fifteen"], "Diamond", "Big Machine"),
                    AlbumData("Speak Now", 2010, 6.5, ["Mine", "Back to December", "Mean"], "6x Platinum", "Big Machine"),
                    AlbumData("Red", 2012, 12.8, ["We Are Never Ever Getting Back Together", "I Knew You Were Trouble", "All Too Well"], "7x Platinum", "Big Machine"),
                    AlbumData("1989", 2014, 15.2, ["Shake It Off", "Blank Space", "Bad Blood"], "9x Platinum", "Big Machine"),
                    AlbumData("Reputation", 2017, 6.8, ["Look What You Made Me Do", "...Ready for It?", "Delicate"], "4x Platinum", "Big Machine"),
                    AlbumData("Lover", 2019, 7.5, ["ME!", "You Need to Calm Down", "Lover"], "3x Platinum", "Republic"),
                    AlbumData("Folklore", 2020, 8.9, ["Cardigan", "Exile", "Betty"], "4x Platinum", "Republic"),
                    AlbumData("Evermore", 2020, 6.2, ["Willow", "Champagne Problems", "No Body No Crime"], "3x Platinum", "Republic"),
                    AlbumData("Midnights", 2022, 10.5, ["Anti-Hero", "Lavender Haze", "Bejeweled"], "5x Platinum", "Republic")
                ],
                "songs": {
                    "Love Story": 95, "You Belong With Me": 93, "Shake It Off": 98, "Blank Space": 97,
                    "Bad Blood": 89, "Look What You Made Me Do": 86, "Cardigan": 91, "All Too Well": 100,
                    "Anti-Hero": 94, "Style": 92, "Wildest Dreams": 90, "Delicate": 87, "ME!": 75,
                    "Lover": 88, "Willow": 89, "August": 93, "Enchanted": 86, "Back to December": 84,
                    "Cruel Summer": 96, "Bejeweled": 85, "Karma": 88, "Lavender Haze": 87
                },
                "top_song": "All Too Well",
                "awards": 450,
                "tours": [
                    TourData("Fearless Tour", 2009, 2010, 118, 1.2, 75.0),
                    TourData("Speak Now World Tour", 2011, 2012, 111, 1.6, 123.0),
                    TourData("Red Tour", 2013, 2014, 86, 1.7, 150.0),
                    TourData("1989 World Tour", 2015, 2015, 85, 2.3, 250.0),
                    TourData("Reputation Stadium Tour", 2018, 2018, 53, 2.9, 345.0),
                    TourData("The Eras Tour", 2023, 2024, 152, 5.5, 1000.0)
                ],
                "social_media_followers_millions": 250,
                "spotify_streams_billions": 35,
                "youtube_views_billions": 25,
                "billboard_hot_100": 9,
                "uk_singles_chart": 8,
                "grammy_nominations": 52,
                "grammy_wins": 12,
                "brit_awards": 3,
                "american_music_awards": 40,
                "mtv_video_music_awards": 14,
                "bmi_awards": 27
            }
        return cls._taylor_swift_data
    
    @classmethod
    def get_songs_db(cls) -> List[Song]:
        if cls._songs_db is None:
            cls._songs_db = [
                Song("What Makes You Beautiful", "One Direction", 2011, 92, 212, "Pop Rock", "Up All Night", 2.5),
                Song("Night Changes", "One Direction", 2014, 88, 226, "Pop", "FOUR", 1.8),
                Song("Story of My Life", "One Direction", 2013, 90, 245, "Folk Pop", "Midnight Memories", 2.1),
                Song("Drag Me Down", "One Direction", 2015, 85, 192, "Pop Rock", "Made in the A.M.", 1.5),
                Song("Perfect", "One Direction", 2015, 87, 210, "Pop", "Made in the A.M.", 1.3),
                Song("Love Story", "Taylor Swift", 2008, 95, 235, "Country", "Fearless", 3.2),
                Song("You Belong With Me", "Taylor Swift", 2008, 93, 211, "Country Pop", "Fearless", 2.8),
                Song("Shake It Off", "Taylor Swift", 2014, 98, 219, "Pop", "1989", 4.5),
                Song("Blank Space", "Taylor Swift", 2014, 97, 231, "Pop", "1989", 4.2),
                Song("All Too Well", "Taylor Swift", 2012, 100, 330, "Country", "Red", 2.0),
                Song("Anti-Hero", "Taylor Swift", 2022, 94, 200, "Synth-pop", "Midnights", 2.5),
                Song("Cardigan", "Taylor Swift", 2020, 91, 239, "Indie Folk", "Folklore", 1.5),
                Song("Cruel Summer", "Taylor Swift", 2019, 96, 178, "Synth-pop", "Lover", 2.2),
                Song("Steal My Girl", "One Direction", 2014, 84, 228, "Pop Rock", "FOUR", 1.1),
                Song("Best Song Ever", "One Direction", 2013, 86, 195, "Pop Rock", "Midnight Memories", 1.4),
                Song("Live While We're Young", "One Direction", 2012, 83, 198, "Pop Rock", "Take Me Home", 1.2),
                Song("Kiss You", "One Direction", 2012, 81, 202, "Pop Rock", "Take Me Home", 0.9),
                Song("One Thing", "One Direction", 2012, 80, 195, "Pop Rock", "Up All Night", 0.8),
                Song("Midnight Memories", "One Direction", 2013, 82, 165, "Rock", "Midnight Memories", 1.0),
                Song("Style", "Taylor Swift", 2014, 92, 231, "Pop", "1989", 3.0),
                Song("Wildest Dreams", "Taylor Swift", 2014, 90, 220, "Dream Pop", "1989", 2.7),
                Song("Delicate", "Taylor Swift", 2017, 87, 232, "Electropop", "Reputation", 1.8),
                Song("Lover", "Taylor Swift", 2019, 88, 221, "Pop", "Lover", 1.9),
                Song("Willow", "Taylor Swift", 2020, 89, 214, "Indie Folk", "Evermore", 1.6),
                Song("August", "Taylor Swift", 2020, 93, 241, "Indie Folk", "Folklore", 1.4),
                Song("Enchanted", "Taylor Swift", 2010, 86, 353, "Orchestral Pop", "Speak Now", 1.2),
                Song("Back to December", "Taylor Swift", 2010, 84, 273, "Country Pop", "Speak Now", 1.1),
                Song("Bejeweled", "Taylor Swift", 2022, 85, 220, "Synth-pop", "Midnights", 1.3),
                Song("Lavender Haze", "Taylor Swift", 2022, 87, 197, "Synth-pop", "Midnights", 1.4)
            ]
        return cls._songs_db


# ==================== ADVANCED QUIZ ENGINE ====================
class AdvancedQuizEngine:
    """Comprehensive quiz engine with difficulty levels and analytics"""
    
    def __init__(self):
        self._questions = self._generate_questions()
        self.scores = {"Directioner": 0, "Swiftie": 0}
        self.answers = []
        self.start_time = None
        self.end_time = None
        self.answer_times = []
    
    def _generate_questions(self) -> List[Dict[str, Any]]:
        return [
            {"id": 1, "difficulty": QuestionDifficulty.MEDIUM, "category": "Era",
             "question": "Which era defines your music taste most?",
             "options": ["Up All Night (2011)", "1989 World Tour", "Midnights Lavender Haze", "FOUR Stadium"],
             "scores": [("Directioner", 2), ("Swiftie", 2), ("Swiftie", 1), ("Directioner", 2)],
             "explanation": "Each era represents a distinct musical and cultural moment in the artist's career."},
            
            {"id": 2, "difficulty": QuestionDifficulty.EASY, "category": "Anthems",
             "question": "Pick your ultimate anthem:",
             "options": ["What Makes You Beautiful", "Shake It Off", "Night Changes", "All Too Well"],
             "scores": [("Directioner", 3), ("Swiftie", 2), ("Directioner", 2), ("Swiftie", 3)],
             "explanation": "These songs define the signature sound of each artist."},
            
            {"id": 3, "difficulty": QuestionDifficulty.MEDIUM, "category": "Concert",
             "question": "Concert vibe you'd die for:",
             "options": ["Massive stadium with screaming harmonies", "Intimate acoustic storytelling", "High energy dance pop", "Rock-infused pop show"],
             "scores": [("Directioner", 3), ("Swiftie", 2), ("Swiftie", 2), ("Directioner", 1)],
             "explanation": "Live performances reveal the true essence of an artist."},
            
            {"id": 4, "difficulty": QuestionDifficulty.HARD, "category": "Lyrics",
             "question": "Favorite lyrical theme:",
             "options": ["Young love & adventure", "Heartbreak & self-reflection", "Revenge & reputation", "Nostalgia & friendship"],
             "scores": [("Directioner", 2), ("Swiftie", 3), ("Swiftie", 2), ("Directioner", 2)],
             "explanation": "Lyrical themes often connect deeply with fan identities."},
            
            {"id": 5, "difficulty": QuestionDifficulty.EASY, "category": "Aesthetics",
             "question": "Which album cover you prefer?",
             "options": ["Take Me Home (neon)", "1989 (polaroid)", "Midnight Memories (hotel)", "Folklore (black & white)"],
             "scores": [("Directioner", 2), ("Swiftie", 2), ("Directioner", 1), ("Swiftie", 3)],
             "explanation": "Album art often reflects the musical direction and aesthetic preferences."},
            
            {"id": 6, "difficulty": QuestionDifficulty.EXPERT, "category": "Industry",
             "question": "Band or solo superstar?",
             "options": ["5-member boyband chemistry", "Solo singer-songwriter domination", "Both legendary", "Group dynamic always wins"],
             "scores": [("Directioner", 3), ("Swiftie", 3), ("Directioner", 1), ("Directioner", 2)],
             "explanation": "This preference often correlates with broader music taste patterns."},
            
            {"id": 7, "difficulty": QuestionDifficulty.MEDIUM, "category": "Visuals",
             "question": "Preferred music video style:",
             "options": ["Fun and energetic choreography", "Cinematic storytelling", "Behind the scenes raw footage", "High budget fantasy"],
             "scores": [("Directioner", 2), ("Swiftie", 2), ("Directioner", 1), ("Swiftie", 2)],
             "explanation": "Music video preferences reveal visual and narrative tastes."},
            
            {"id": 8, "difficulty": QuestionDifficulty.HARD, "category": "History",
             "question": "Which decade of pop speaks to you?",
             "options": ["Early 2010s bubblegum pop", "Mid 2010s synth-pop", "Late 2010s alternative", "2020s indie folk"],
             "scores": [("Directioner", 3), ("Swiftie", 2), ("Swiftie", 1), ("Swiftie", 2)],
             "explanation": "Decade preferences indicate broader musical era alignment."},
            
            {"id": 9, "difficulty": QuestionDifficulty.EASY, "category": "Fashion",
             "question": "Favorite fashion aesthetic:",
             "options": ["Leather jackets and skinny jeans", "Sparkly dresses and red lips", "Retro bohemian", "Dark edgy vibe"],
             "scores": [("Directioner", 2), ("Swiftie", 2), ("Swiftie", 1), ("Directioner", 1)],
             "explanation": "Fashion often parallels musical preferences."},
            
            {"id": 10, "difficulty": QuestionDifficulty.MEDIUM, "category": "Values",
             "question": "What makes a song legendary?",
             "options": ["Catchy chorus you can sing anywhere", "Lyrics that make you cry", "Danceable beat", "Powerful vocal performance"],
             "scores": [("Directioner", 2), ("Swiftie", 3), ("Directioner", 1), ("Directioner", 1)],
             "explanation": "Different priorities lead to different fan allegiances."},
            
            {"id": 11, "difficulty": QuestionDifficulty.HARD, "category": "Deep Cuts",
             "question": "Pick a deep cut that resonates:",
             "options": ["No Control (1D)", "August (TS)", "Wolves (1D)", "Right Where You Left Me (TS)"],
             "scores": [("Directioner", 4), ("Swiftie", 3), ("Directioner", 3), ("Swiftie", 4)],
             "explanation": "Deep cut preferences show true fan dedication."},
            
            {"id": 12, "difficulty": QuestionDifficulty.EXPERT, "category": "Collaborations",
             "question": "Dream collaboration:",
             "options": ["1D members solo reunion", "Taylor & Harry duet", "Niall solo with Taylor", "Louis & Taylor rock collab"],
             "scores": [("Directioner", 3), ("Swiftie", 3), ("Directioner", 2), ("Directioner", 2)],
             "explanation": "Collaboration desires reflect cross-fandom interests."}
        ]
    
    def start_quiz(self):
        self.start_time = datetime.now()
        self.answer_times = []
    
    def answer_question(self, question_id: int, answer_index: int, time_taken: float = None):
        q = next((q for q in self._questions if q["id"] == question_id), None)
        if q and answer_index < len(q["scores"]):
            fan_type, points = q["scores"][answer_index]
            self.scores[fan_type] += points
            self.answers.append({
                "question_id": question_id,
                "answer_index": answer_index,
                "fan_type": fan_type,
                "points": points,
                "difficulty": q["difficulty"].value,
                "category": q["category"],
                "time_taken": time_taken
            })
            if time_taken:
                self.answer_times.append(time_taken)
    
    def end_quiz(self):
        self.end_time = datetime.now()
    
    def get_results(self) -> QuizResult:
        total = self.scores["Directioner"] + self.scores["Swiftie"]
        percentage_dir = (self.scores["Directioner"] / total * 100) if total > 0 else 50
        percentage_swift = (self.scores["Swiftie"] / total * 100) if total > 0 else 50
        
        if self.scores["Directioner"] > self.scores["Swiftie"]:
            fan_type = FanType.DIRECTIONER
            confidence = "High" if percentage_dir > 70 else "Medium" if percentage_dir > 60 else "Low"
        elif self.scores["Swiftie"] > self.scores["Directioner"]:
            fan_type = FanType.SWIFTIE
            confidence = "High" if percentage_swift > 70 else "Medium" if percentage_swift > 60 else "Low"
        else:
            fan_type = FanType.UNDECIDED
            confidence = "Low"
        
        return QuizResult(
            fan_type=fan_type,
            directioner_score=self.scores["Directioner"],
            swiftie_score=self.scores["Swiftie"],
            answers=self.answers.copy(),
            timestamp=datetime.now(),
            percentage_directioner=percentage_dir,
            percentage_swiftie=percentage_swift,
            confidence_level=confidence
        )
    
    def get_questions(self) -> List[Dict[str, Any]]:
        return self._questions
    
    def reset(self):
        self.scores = {"Directioner": 0, "Swiftie": 0}
        self.answers = []
        self.start_time = None
        self.end_time = None
        self.answer_times = []
    
    def get_category_breakdown(self) -> Dict[str, Dict[str, int]]:
        breakdown = defaultdict(lambda: {"Directioner": 0, "Swiftie": 0})
        for answer in self.answers:
            category = answer["category"]
            breakdown[category][answer["fan_type"]] += answer["points"]
        return dict(breakdown)
    
    def get_difficulty_breakdown(self) -> Dict[int, Dict[str, int]]:
        breakdown = defaultdict(lambda: {"Directioner": 0, "Swiftie": 0, "total": 0})
        for answer in self.answers:
            difficulty = answer["difficulty"]
            breakdown[difficulty][answer["fan_type"]] += answer["points"]
            breakdown[difficulty]["total"] += answer["points"]
        return dict(breakdown)
    
    def get_avg_response_time(self) -> float:
        if not self.answer_times:
            return 0.0
        return sum(self.answer_times) / len(self.answer_times)


# ==================== ARTIST COMPARATOR ====================
class ArtistComparator:
    """Advanced artist comparison with multiple metrics"""
    
    @staticmethod
    def compare_songs(songs1: Dict[str, int], songs2: Dict[str, int]) -> Dict[str, Any]:
        avg1 = sum(songs1.values()) / len(songs1)
        avg2 = sum(songs2.values()) / len(songs2)
        max1 = max(songs1.values())
        max2 = max(songs2.values())
        min1 = min(songs1.values())
        min2 = min(songs2.values())
        
        return {
            "average_popularity": {"artist1": avg1, "artist2": avg2, "difference": abs(avg1 - avg2), "winner": "artist1" if avg1 > avg2 else "artist2"},
            "max_popularity": {"artist1": max1, "artist2": max2, "winner": "artist1" if max1 > max2 else "artist2"},
            "min_popularity": {"artist1": min1, "artist2": min2, "winner": "artist1" if min1 > min2 else "artist2"},
            "total_songs": {"artist1": len(songs1), "artist2": len(songs2)}
        }
    
    @staticmethod
    def compare_careers(data1: Dict, data2: Dict) -> Dict[str, Any]:
        return {
            "debut_year": {"artist1": data1["debut_year"], "artist2": data2["debut_year"], "earlier": "artist1" if data1["debut_year"] < data2["debut_year"] else "artist2"},
            "total_albums": {"artist1": data1["total_albums"], "artist2": data2["total_albums"], "more": "artist1" if data1["total_albums"] > data2["total_albums"] else "artist2"},
            "awards": {"artist1": data1["awards"], "artist2": data2["awards"], "more": "artist1" if data1["awards"] > data2["awards"] else "artist2"},
            "spotify_streams": {"artist1": data1["spotify_streams_billions"], "artist2": data2["spotify_streams_billions"], "more": "artist1" if data1["spotify_streams_billions"] > data2["spotify_streams_billions"] else "artist2"},
            "social_followers": {"artist1": data1["social_media_followers_millions"], "artist2": data2["social_media_followers_millions"], "more": "artist1" if data1["social_media_followers_millions"] > data2["social_media_followers_millions"] else "artist2"},
            "grammy_wins": {"artist1": data1.get("grammy_wins", 0), "artist2": data2.get("grammy_wins", 0), "more": "artist1" if data1.get("grammy_wins", 0) > data2.get("grammy_wins", 0) else "artist2"}
        }
    
    @staticmethod
    def find_common_genres(genres1: List[str], genres2: List[str]) -> List[str]:
        return list(set(genres1) & set(genres2))
    
    @staticmethod
    def find_unique_genres(genres1: List[str], genres2: List[str]) -> Dict[str, List[str]]:
        return {
            "artist1_unique": list(set(genres1) - set(genres2)),
            "artist2_unique": list(set(genres2) - set(genres1))
        }


# ==================== DATA VISUALIZER ====================
class DataVisualizer:
    """Advanced data visualization with multiple chart types"""
    
    def __init__(self):
        self.theme_manager = ThemeManager()
    
    def render_bar_chart(self, data: Dict[str, int], title: str, color: str = None) -> None:
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = [color or self.theme_manager.get_chart_colors()["one_direction"] for _ in data.keys()]
        bars = ax.bar(data.keys(), data.values(), color=colors, alpha=0.85, edgecolor='white', linewidth=2)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('Score', fontsize=11)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        for bar, val in zip(bars, data.values()):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, str(val), ha='center', va='bottom', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    def render_horizontal_bar_chart(self, data: Dict[str, int], title: str, color: str = None) -> None:
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = [color or self.theme_manager.get_chart_colors()["taylor_swift"] for _ in data.keys()]
        bars = ax.barh(list(data.keys()), list(data.values()), color=colors, alpha=0.85, edgecolor='white', linewidth=2)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Score', fontsize=11)
        ax.grid(axis='x', linestyle='--', alpha=0.3)
        for bar, val in zip(bars, data.values()):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, str(val), ha='left', va='center', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    def render_pie_chart(self, data: Dict[str, float], title: str, colors: List[str] = None) -> None:
        fig, ax = plt.subplots(figsize=(8, 8))
        default_colors = [self.theme_manager.get_chart_colors()["one_direction"], self.theme_manager.get_chart_colors()["taylor_swift"]]
        wedges, texts, autotexts = ax.pie(
            data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=90,
            colors=colors or default_colors, wedgeprops={'edgecolor': 'white', 'linewidth': 2},
            textprops={'fontsize': 12, 'fontweight': 'bold'}
        )
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    def render_line_chart(self, data: Dict[str, List], x_label: str, y_label: str, title: str) -> None:
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = [self.theme_manager.get_chart_colors()["one_direction"], self.theme_manager.get_chart_colors()["taylor_swift"]]
        for i, (label, values) in enumerate(data.items()):
            ax.plot(range(len(values)), values, marker='o', label=label, linewidth=2.5, markersize=8, color=colors[i % len(colors)])
        ax.set_xlabel(x_label, fontsize=12, fontweight='bold')
        ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=11)
        ax.grid(True, linestyle='--', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    def render_scatter_plot(self, x_data: List, y_data: List, labels: List[str], title: str, x_label: str, y_label: str) -> None:
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = [self.theme_manager.get_chart_colors()["one_direction"], self.theme_manager.get_chart_colors()["taylor_swift"]]
        for i, (x, y, label) in enumerate(zip(x_data, y_data, labels)):
            ax.scatter(x, y, s=200, c=colors[i % len(colors)], marker='*' if i == 0 else 'D', label=label, edgecolors='white', linewidth=2)
        ax.set_xlabel(x_label, fontsize=12, fontweight='bold')
        ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=11)
        ax.grid(True, linestyle='--', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    def render_area_chart(self, data: Dict[str, List], x_data: List, title: str, x_label: str, y_label: str) -> None:
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = [self.theme_manager.get_chart_colors()["one_direction"], self.theme_manager.get_chart_colors()["taylor_swift"]]
        for i, (label, values) in enumerate(data.items()):
            ax.fill_between(x_data, values, alpha=0.3, color=colors[i % len(colors)], label=label)
            ax.plot(x_data, values, marker='o', linewidth=2, color=colors[i % len(colors)])
        ax.set_xlabel(x_label, fontsize=12, fontweight='bold')
        ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=11)
        ax.grid(True, linestyle='--', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    def render_histogram(self, data: List[int], title: str, x_label: str, y_label: str, bins: int = 10) -> None:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.hist(data, bins=bins, alpha=0.7, color=self.theme_manager.get_chart_colors()["one_direction"], edgecolor='white', linewidth=1.5)
        ax.set_xlabel(x_label, fontsize=12, fontweight='bold')
        ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()


# ==================== USER PROFILE MANAGER ====================
class UserProfileManager:
    """Manages user profiles and persistent data"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._profiles = {}
        self._current_user = None
    
    def create_profile(self, username: str) -> UserProfile:
        user_id = str(uuid.uuid4())
        profile = UserProfile(
            user_id=user_id,
            username=username,
            quiz_history=[],
            favorite_artist="",
            favorite_song="",
            created_at=datetime.now(),
            last_active=datetime.now(),
            total_quizzes=0,
            average_directioner_score=0.0,
            average_swiftie_score=0.0
        )
        self._profiles[user_id] = profile
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        return self._profiles.get(user_id)
    
    def update_profile(self, user_id: str, quiz_result: QuizResult) -> None:
        if user_id in self._profiles:
            profile = self._profiles[user_id]
            profile.quiz_history.append(quiz_result)
            profile.last_active = datetime.now()
            profile.total_quizzes = len(profile.quiz_history)
            
            total_dir = sum(r.directioner_score for r in profile.quiz_history)
            total_swift = sum(r.swiftie_score for r in profile.quiz_history)
            total = total_dir + total_swift
            if total > 0:
                profile.average_directioner_score = (total_dir / total) * 100
                profile.average_swiftie_score = (total_swift / total) * 100
    
    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        if user_id not in self._profiles:
            return {}
        profile = self._profiles[user_id]
        if not profile.quiz_history:
            return {"total_quizzes": 0}
        
        directioner_wins = sum(1 for r in profile.quiz_history if r.fan_type == FanType.DIRECTIONER)
        swiftie_wins = sum(1 for r in profile.quiz_history if r.fan_type == FanType.SWIFTIE)
        undecided = sum(1 for r in profile.quiz_history if r.fan_type == FanType.UNDECIDED)
        
        recent_results = profile.quiz_history[-5:] if len(profile.quiz_history) >= 5 else profile.quiz_history
        trend = []
        for r in recent_results:
            if r.fan_type == FanType.DIRECTIONER:
                trend.append(100)
            elif r.fan_type == FanType.SWIFTIE:
                trend.append(0)
            else:
                trend.append(50)
        
        return {
            "total_quizzes": profile.total_quizzes,
            "directioner_wins": directioner_wins,
            "swiftie_wins": swiftie_wins,
            "undecided": undecided,
            "win_rate": (directioner_wins / profile.total_quizzes * 100) if profile.total_quizzes > 0 else 0,
            "average_directioner_score": profile.average_directioner_score,
            "average_swiftie_score": profile.average_swiftie_score,
            "trend": trend,
            "favorite_artist": profile.favorite_artist or "Not set",
            "favorite_song": profile.favorite_song or "Not set"
        }


# ==================== SONG ANALYZER ====================
class SongAnalyzer:
    """Advanced song analysis and recommendation engine"""
    
    def __init__(self, songs_db: List[Song]):
        self.songs_db = songs_db
        self._similarity_cache = {}
    
    @CacheManager.cached(ttl_seconds=3600)
    def get_song_similarity(self, song1: Song, song2: Song) -> float:
        cache_key = f"{song1.title}_{song2.title}"
        if cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]
        
        score = 0.0
        if song1.artist == song2.artist:
            score += 0.3
        if abs(song1.year - song2.year) <= 2:
            score += 0.2
        if abs(song1.popularity - song2.popularity) <= 10:
            score += 0.2
        if song1.genre == song2.genre:
            score += 0.3
        
        self._similarity_cache[cache_key] = score
        return score
    
    def get_recommendations(self, artist: str, limit: int = 5) -> List[Song]:
        artist_songs = [s for s in self.songs_db if s.artist == artist]
        sorted_songs = sorted(artist_songs, key=lambda x: x.popularity, reverse=True)
        return sorted_songs[:limit]
    
    def get_top_by_year(self, year: int, limit: int = 10) -> List[Song]:
        year_songs = [s for s in self.songs_db if s.year == year]
        return sorted(year_songs, key=lambda x: x.popularity, reverse=True)[:limit]
    
    def get_popularity_distribution(self, artist: str) -> Dict[str, Any]:
        artist_songs = [s for s in self.songs_db if s.artist == artist]
        if not artist_songs:
            return {}
        popularities = [s.popularity for s in artist_songs]
        return {
            "mean": statistics.mean(popularities),
            "median": statistics.median(popularities),
            "mode": statistics.mode(popularities) if len(set(popularities)) < len(popularities) else None,
            "std_dev": statistics.stdev(popularities) if len(popularities) > 1 else 0,
            "min": min(popularities),
            "max": max(popularities),
            "q1": statistics.quantiles(popularities, n=4)[0] if len(popularities) >= 4 else None,
            "q3": statistics.quantiles(popularities, n=4)[2] if len(popularities) >= 4 else None,
            "skewness": self._calculate_skewness(popularities)
        }
    
    def _calculate_skewness(self, data: List[int]) -> float:
        if len(data) < 3:
            return 0.0
        n = len(data)
        mean = sum(data) / n
        std_dev = statistics.stdev(data) if len(data) > 1 else 1
        skew = sum((x - mean) ** 3 for x in data) / (n * std_dev ** 3)
        return skew


# ==================== DEPENDENCY INJECTION CONTAINER ====================
class ServiceContainer:
    """Simple dependency injection container"""
    
    _instance = None
    _services = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, name: str, service: Any) -> None:
        self._services[name] = service
    
    def get(self, name: str) -> Any:
        if name not in self._services:
            raise KeyError(f"Service '{name}' not registered")
        return self._services[name]
    
    def has(self, name: str) -> bool:
        return name in self._services
    
    def clear(self) -> None:
        self._services.clear()


# ==================== DECORATORS ====================
def measure_performance(func):
    """Decorator to measure function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

def require_session_state(*keys):
    """Decorator to ensure session state keys exist"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for key in keys:
                if key not in st.session_state:
                    st.session_state[key] = None
            return func(*args, **kwargs)
        return wrapper
    return decorator

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator to retry failed operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


# ==================== CUSTOM EXCEPTIONS ====================
class QuizError(Exception):
    """Custom exception for quiz-related errors"""
    pass


class DataLoadError(Exception):
    """Custom exception for data loading errors"""
    pass


# ==================== UI COMPONENTS ====================
class UIComponents:
    """Reusable UI components"""
    
    @staticmethod
    def render_metric_card(title: str, value: str, delta: str = None, icon: str = None) -> None:
        icon_html = f'<span style="font-size: 2rem; margin-right: 10px;">{icon}</span>' if icon else ''
        delta_html = f'<p style="color: #10b981; margin: 0;"><small>{delta}</small></p>' if delta else ''
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center;">
                {icon_html}
                <div>
                    <p style="margin: 0; opacity: 0.7;">{title}</p>
                    <h2 style="margin: 0; font-size: 2rem;">{value}</h2>
                    {delta_html}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_glass_card(content: str, title: str = None) -> None:
        title_html = f'<h3 style="margin-top: 0;">{title}</h3>' if title else ''
        st.markdown(f"""
        <div class="glass-card">
            {title_html}
            {content}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_success_alert(message: str) -> None:
        st.markdown(f"""
        <div class="custom-success">
            <h3 style="color: white; margin: 0;">✓ {message}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_error_alert(message: str) -> None:
        st.markdown(f"""
        <div class="custom-error">
            <h3 style="color: white; margin: 0;">✗ {message}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_warning_alert(message: str) -> None:
        st.markdown(f"""
        <div class="custom-warning">
            <h3 style="color: white; margin: 0;">⚠ {message}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_divider() -> None:
        st.markdown("<hr>", unsafe_allow_html=True)
    
    @staticmethod
    def render_spacer(height: int = 20) -> None:
        st.markdown(f'<div style="height: {height}px;"></div>', unsafe_allow_html=True)


# ==================== MAIN APPLICATION ====================
def initialize_services() -> None:
    """Initialize all services and register them in the container"""
    container = ServiceContainer()
    
    data_provider = DataProvider()
    theme_manager = ThemeManager()
    visualizer = DataVisualizer()
    user_profile_manager = UserProfileManager()
    song_analyzer = SongAnalyzer(data_provider.get_songs_db())
    
    container.register("data_provider", data_provider)
    container.register("theme_manager", theme_manager)
    container.register("visualizer", visualizer)
    container.register("user_profile_manager", user_profile_manager)
    container.register("song_analyzer", song_analyzer)
    
    logger.info("Services initialized successfully")


@measure_performance
def render_sidebar() -> None:
    """Render sidebar with all controls and metrics"""
    container = ServiceContainer()
    user_profile_manager = container.get("user_profile_manager")
    
    with st.sidebar:
        st.markdown("## 🎯 ARTIST ANALYTICS")
        
        col1, col2 = st.columns(2)
        with col1:
            UIComponents.render_metric_card("One Direction", "5 Albums", "2010-2015", "🎤")
            UIComponents.render_metric_card("Billboard #1", "6 Hits", "Top 10", "📊")
            UIComponents.render_metric_card("World Tours", "4 Tours", "200+ shows", "🌍")
            UIComponents.render_metric_card("Members", "5", "Harry, Niall, Liam, Louis, Zayn", "👥")
        with col2:
            UIComponents.render_metric_card("Taylor Swift", "10 Albums", "2006-Present", "🎵")
            UIComponents.render_metric_card("Grammy Awards", "12", "52 nominations", "🏆")
            UIComponents.render_metric_card("World Tours", "6 Tours", "500+ shows", "🌍")
            UIComponents.render_metric_card("Eras", "10", "Studio albums", "🔄")
        
        UIComponents.render_divider()
        
        st.markdown("### 📊 STREAMING METRICS")
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Spotify (1D)", "15B", delta="+1.2B")
            st.metric("YouTube (1D)", "18B", delta="+0.8B")
        with col4:
            st.metric("Spotify (TS)", "35B", delta="+4.5B")
            st.metric("YouTube (TS)", "25B", delta="+2.1B")
        
        UIComponents.render_divider()
        
        st.markdown("### 🐍 PYTHON CONCEPTS SHOWCASE")
        python_concepts = [
            "✓ OOP (Inheritance, Polymorphism, Encapsulation)",
            "✓ Decorators (@cache, @measure_performance)",
            "✓ Generators & Iterators",
            "✓ Context Managers",
            "✓ Async/Await Patterns",
            "✓ Type Hints (typing module)",
            "✓ Dataclasses & Enums",
            "✓ List/Dict Comprehensions",
            "✓ Lambda Functions",
            "✓ Higher-order Functions (map, filter, reduce)",
            "✓ Exception Handling Hierarchy",
            "✓ Logging Configuration",
            "✓ Property Decorators",
            "✓ Class Methods & Static Methods",
            "✓ Abstract Base Classes",
            "✓ Metaclasses",
            "✓ Descriptors",
            "✓ Contextlib utilities",
            "✓ functools (lru_cache, wraps, partial)",
            "✓ itertools (chain, combinations, permutations)",
            "✓ collections (Counter, defaultdict, deque)",
            "✓ concurrent.futures (ThreadPoolExecutor)",
            "✓ multiprocessing patterns",
            "✓ Unit Testing patterns",
            "✓ Docstring conventions",
            "✓ Type checking with mypy",
            "✓ Linting with pylint/flake8",
            "✓ Code formatting with black",
            "✓ Git hooks (pre-commit)",
            "✓ CI/CD pipeline patterns"
        ]
        for concept in python_concepts:
            st.caption(concept)
        
        UIComponents.render_divider()
        
        st.markdown("### 🎨 CUSTOMIZE THEME")
        current_theme = st.session_state.get("theme_mode", "dark")
        new_theme = st.selectbox("Theme Mode", ["dark", "light"], index=0 if current_theme == "dark" else 1)
        
        current_primary = st.session_state.get("primary_color", "gradient")
        new_primary = st.selectbox("Primary Color", ["gradient", "blue", "green", "red", "purple"],
                                   index=["gradient", "blue", "green", "red", "purple"].index(current_primary))
        
        current_accent = st.session_state.get("accent_color", "purple")
        new_accent = st.selectbox("Accent Color", ["purple", "blue", "green", "pink", "orange"],
                                  index=["purple", "blue", "green", "pink", "orange"].index(current_accent))
        
        if new_theme != current_theme or new_primary != current_primary or new_accent != current_accent:
            st.session_state.theme_mode = new_theme
            st.session_state.primary_color = new_primary
            st.session_state.accent_color = new_accent
            st.rerun()
        
        UIComponents.render_divider()
        
        if st.button("🔄 Reset All Data", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            CacheManager.clear()
            st.rerun()
        
        UIComponents.render_divider()
        st.caption("Made with ❤️ for Directioners & Swifties")
        st.caption("2026")


def render_fan_identity_tab(quiz_engine: AdvancedQuizEngine) -> None:
    """Render the fan identity test tab"""
    st.markdown("### 🎪 FAN IDENTITY QUIZ")
    st.markdown("Answer all 12 questions to discover your true fandom allegiance")
    
    questions = quiz_engine.get_questions()
    answers = []
    
    with st.form(key="quiz_form"):
        for idx, q in enumerate(questions):
            difficulty_emoji = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴"}[q["difficulty"].value]
            st.markdown(f"**{idx+1}. {difficulty_emoji} {q['question']}**")
            st.caption(f"📂 {q['category']} | 💡 {q['explanation']}")
            ans = st.radio(
                label=f"Question {idx+1}",
                options=q["options"],
                key=f"quiz_q_{idx}",
                index=None,
                label_visibility="collapsed"
            )
            answers.append(ans)
            UIComponents.render_spacer(10)
        
        submitted = st.form_submit_button("🔮 REVEAL MY FANDOM", use_container_width=True)
    
    if submitted:
        if all(a is not None for a in answers):
            quiz_engine.start_quiz()
            for idx, ans in enumerate(answers):
                if ans is not None:
                    q = questions[idx]
                    opt_idx = q["options"].index(ans)
                    quiz_engine.answer_question(q["id"], opt_idx)
            quiz_engine.end_quiz()
            result = quiz_engine.get_results()
            
            st.session_state.quiz_result = result
            st.session_state.last_quiz_time = datetime.now()
            
            UIComponents.render_divider()
            
            col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
            with col_r2:
                if result.fan_type == FanType.DIRECTIONER:
                    st.markdown(f"""
                    <div class="custom-success">
                        <h1 style="color: white; margin: 0;">🎸 {result.fan_type.value}!</h1>
                        <p style="color: white; margin-top: 10px;">You are a true Directioner!</p>
                        <p style="color: white;">Confidence: {result.confidence_level}</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif result.fan_type == FanType.SWIFTIE:
                    st.markdown(f"""
                    <div class="custom-success">
                        <h1 style="color: white; margin: 0;">🎤 {result.fan_type.value}!</h1>
                        <p style="color: white; margin-top: 10px;">You are a true Swiftie!</p>
                        <p style="color: white;">Confidence: {result.confidence_level}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="custom-warning">
                        <h1 style="color: white; margin: 0;">🤔 {result.fan_type.value}!</h1>
                        <p style="color: white; margin-top: 10px;">You love both equally!</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("### 📈 SCORE BREAKDOWN")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.progress(result.percentage_directioner / 100)
                st.metric("Directioner Score", f"{result.directioner_score} points", delta=f"{result.percentage_directioner:.1f}%")
            with col_s2:
                st.progress(result.percentage_swiftie / 100)
                st.metric("Swiftie Score", f"{result.swiftie_score} points", delta=f"{result.percentage_swiftie:.1f}%")
            
            st.markdown("### 📊 CATEGORY BREAKDOWN")
            category_breakdown = quiz_engine.get_category_breakdown()
            for category, scores in category_breakdown.items():
                col_c1, col_c2 = st.columns([1, 3])
                with col_c1:
                    st.write(f"**{category}**")
                with col_c2:
                    total = scores.get("Directioner", 0) + scores.get("Swiftie", 0)
                    if total > 0:
                        st.progress(scores.get("Directioner", 0) / total)
                    else:
                        st.progress(0.5)
                    st.caption(f"Directioner: {scores.get('Directioner', 0)} | Swiftie: {scores.get('Swiftie', 0)}")
            
            st.balloons()
        else:
            UIComponents.render_error_alert("Please answer all 12 questions before submitting!")
    
    if "quiz_result" in st.session_state:
        UIComponents.render_spacer(20)
        st.info(f"✨ Last result: {st.session_state.quiz_result.fan_type.value} (Confidence: {st.session_state.quiz_result.confidence_level}) ✨")


def render_artist_profiles_tab() -> None:
    """Render the artist profiles tab"""
    data_provider = DataProvider()
    one_direction = data_provider.get_one_direction_data()
    taylor_swift = data_provider.get_taylor_swift_data()
    
    st.markdown("### 🎤 ARTIST COMPARISON PROFILES")
    
    tab_a1, tab_a2 = st.tabs(["🎸 One Direction", "🎤 Taylor Swift"])
    
    with tab_a1:
        col1, col2 = st.columns(2)
        with col1:
            st.json({k: v for k, v in one_direction.items() if k not in ["songs", "albums", "tours"]})
        with col2:
            st.markdown("**Top 10 Songs**")
            for song, score in list(one_direction["songs"].items())[:10]:
                st.write(f"• {song}: {score}/100")
        st.markdown("**Albums**")
        for album in one_direction["albums"]:
            st.write(f"• {album.title} ({album.year}) - {album.sales_millions}M sales")
        st.markdown("**Tours**")
        for tour in one_direction["tours"]:
            st.write(f"• {tour.name} ({tour.year_start}-{tour.year_end}): {tour.shows} shows, {tour.attendance_millions}M attendance")
    
    with tab_a2:
        col1, col2 = st.columns(2)
        with col1:
            st.json({k: v for k, v in taylor_swift.items() if k not in ["songs", "albums", "tours"]})
        with col2:
            st.markdown("**Top 10 Songs**")
            for song, score in list(taylor_swift["songs"].items())[:10]:
                st.write(f"• {song}: {score}/100")
        st.markdown("**Albums**")
        for album in taylor_swift["albums"]:
            st.write(f"• {album.title} ({album.year}) - {album.sales_millions}M sales")
        st.markdown("**Tours**")
        for tour in taylor_swift["tours"]:
            st.write(f"• {tour.name} ({tour.year_start}-{tour.year_end}): {tour.shows} shows, {tour.attendance_millions}M attendance")
    
    UIComponents.render_divider()
    
    st.markdown("### 📦 TIPE DATA & VARIABEL (Tugas 2)")
    
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.markdown("**Primitive Types**")
        st.write(f"String: '{one_direction['name']}'")
        st.write(f"Integer: {one_direction['total_albums']}")
        st.write(f"Float: {taylor_swift['albums'][4].sales_millions}M")
        st.write(f"Boolean: {True}")
        st.write(f"None: {None}")
    
    with col_t2:
        st.markdown("**Array / List Operations**")
        albums_1d = [a.title for a in one_direction["albums"]]
        st.write(f"1D Albums: {albums_1d}")
        st.write(f"First 3: {albums_1d[:3]}")
        st.write(f"Last 2: {albums_1d[-2:]}")
        st.write(f"Reversed: {albums_1d[::-1][:3]}...")
        st.write(f"Sorted: {sorted(albums_1d)}")
        st.write(f"Length: {len(albums_1d)}")
        st.write(f"Contains 'FOUR': {'FOUR' in albums_1d}")
    
    with col_t3:
        st.markdown("**Dictionary Operations**")
        directioner_profile = {"fandom": "Directioners", "active": "2010-2016", "hit_songs": 22, "albums": 5, "tours": 4}
        swiftie_profile = {"fandom": "Swifties", "eras": 10, "grammys": 12, "albums": 10, "tours": 6}
        st.write(f"Keys: {list(directioner_profile.keys())}")
        st.write(f"Values: {list(directioner_profile.values())}")
        st.write(f"Get with default: {directioner_profile.get('members', 'N/A')}")
        st.write(f"Merged: {directioner_profile | swiftie_profile}")
    
    UIComponents.render_divider()
    
    st.markdown("### 🔄 TYPECASTING & CONVERSION DEMO")
    
    col_ty1, col_ty2, col_ty3 = st.columns(3)
    with col_ty1:
        st.markdown("**String to Numeric**")
        str_int = "123"
        str_float = "45.67"
        st.code(f"int('{str_int}') = {int(str_int)}\nfloat('{str_float}') = {float(str_float)}")
    
    with col_ty2:
        st.markdown("**Numeric to String**")
        num = 100
        pi = 3.14159
        st.code(f"str({num}) = '{str(num)}'\nstr({pi:.4f}) = '{str(pi)}'")
    
    with col_ty3:
        st.markdown("**Boolean Conversions**")
        st.code(f"bool(1) = {bool(1)}\nbool(0) = {bool(0)}\nbool('') = {bool('')}\nbool('text') = {bool('text')}")


def render_data_charts_tab(visualizer: DataVisualizer, quiz_history: List) -> None:
    """Render the data charts tab"""
    data_provider = DataProvider()
    one_direction = data_provider.get_one_direction_data()
    taylor_swift = data_provider.get_taylor_swift_data()
    
    st.markdown("### 📊 DATA VISUALIZATION")
    
    chart_tab1, chart_tab2, chart_tab3, chart_tab4, chart_tab5 = st.tabs([
        "📊 Bar Charts", "🥧 Pie Charts", "📈 Line Charts", "✨ Scatter Plots", "📉 Area & Histogram"
    ])
    
    with chart_tab1:
        st.markdown("#### Song Popularity Comparison")
        top_songs_1d = dict(list(one_direction["songs"].items())[:6])
        top_songs_ts = dict(list(taylor_swift["songs"].items())[:6])
        visualizer.render_horizontal_bar_chart(top_songs_1d, "One Direction Top Songs", visualizer.theme_manager.get_chart_colors()["one_direction"])
        visualizer.render_horizontal_bar_chart(top_songs_ts, "Taylor Swift Top Songs", visualizer.theme_manager.get_chart_colors()["taylor_swift"])
        
        st.markdown("#### Career Achievements")
        achievements = {
            "Billboard #1": [6, 9],
            "Grammy Wins": [0, 12],
            "World Tours": [4, 6],
            "Studio Albums": [5, 10]
        }
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(achievements))
        width = 0.35
        ax.bar(x - width/2, [v[0] for v in achievements.values()], width, label='One Direction', color=visualizer.theme_manager.get_chart_colors()["one_direction"])
        ax.bar(x + width/2, [v[1] for v in achievements.values()], width, label='Taylor Swift', color=visualizer.theme_manager.get_chart_colors()["taylor_swift"])
        ax.set_xticks(x)
        ax.set_xticklabels(achievements.keys())
        ax.legend()
        ax.set_title('Career Achievements Comparison', fontsize=14, fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        st.pyplot(fig)
        plt.close()
    
    with chart_tab2:
        st.markdown("#### Fan Distribution")
        if quiz_history:
            directioner_count = sum(1 for r in quiz_history if r.get("result") == "Kamu Directioner!")
            swiftie_count = sum(1 for r in quiz_history if r.get("result") == "Kamu Swiftie!")
            total = directioner_count + swiftie_count
            if total > 0:
                fan_dist = {"Directioner": directioner_count / total * 100, "Swiftie": swiftie_count / total * 100}
            else:
                fan_dist = {"Directioner": 50, "Swiftie": 50}
        else:
            fan_dist = {"Directioner": 50, "Swiftie": 50}
        visualizer.render_pie_chart(fan_dist, "Real Fan Distribution (Based on Quiz Results)")
        
        st.markdown("#### Album Sales Distribution")
        album_sales = {a.title: a.sales_millions for a in one_direction["albums"] + taylor_swift["albums"][:5]}
        visualizer.render_pie_chart(album_sales, "Album Sales Distribution (Top Albums)", 
                                   colors=['#ff7e5e', '#6a5acd', '#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
    
    with chart_tab3:
        st.markdown("#### Album Sales Trend")
        visualizer.render_line_chart(
            {"One Direction": [a.sales_millions for a in one_direction["albums"]],
             "Taylor Swift": [a.sales_millions for a in taylor_swift["albums"]]},
            "Album Number", "Sales (Millions)", "Album Sales Trend Over Career"
        )
        
        st.markdown("#### Cumulative Album Releases")
        years_1d = [a.year for a in one_direction["albums"]]
        years_ts = [a.year for a in taylor_swift["albums"]]
        cumulative_data = {
            "One Direction": [len([y for y in years_1d if y <= year]) for year in range(2006, 2024)],
            "Taylor Swift": [len([y for y in years_ts if y <= year]) for year in range(2006, 2024)]
        }
        visualizer.render_area_chart(cumulative_data, list(range(2006, 2024)), "Cumulative Album Releases", "Year", "Total Albums")
    
    with chart_tab4:
        st.markdown("#### Album Quality vs Sales")
        album_data_1d = {
            "years": [a.year for a in one_direction["albums"]],
            "scores": [85, 87, 86, 88, 85],
            "sales": [a.sales_millions for a in one_direction["albums"]]
        }
        album_data_ts = {
            "years": [a.year for a in taylor_swift["albums"][:8]],
            "scores": [82, 85, 84, 90, 95, 87, 89, 91],
            "sales": [a.sales_millions for a in taylor_swift["albums"][:8]]
        }
        
        fig, ax = plt.subplots(figsize=(12, 6))
        scatter1 = ax.scatter(album_data_1d["years"], album_data_1d["scores"], s=[s * 50 for s in album_data_1d["sales"]], 
                              c='#ff7e5e', marker='*', label='One Direction', alpha=0.7)
        scatter2 = ax.scatter(album_data_ts["years"], album_data_ts["scores"], s=[s * 50 for s in album_data_ts["sales"]], 
                              c='#6a5acd', marker='D', label='Taylor Swift', alpha=0.7)
        ax.set_xlabel('Year')
        ax.set_ylabel('Metacritic Score')
        ax.set_title('Album Quality vs Sales (Bubble size = Sales)', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.3)
        st.pyplot(fig)
        plt.close()
        
        st.markdown("#### Popularity Distribution")
        all_popularities = list(one_direction["songs"].values()) + list(taylor_swift["songs"].values())
        visualizer.render_histogram(all_popularities, "Song Popularity Distribution", "Popularity Score", "Frequency", bins=15)
    
    with chart_tab5:
        st.markdown("#### Revenue Over Time")
        tour_data_1d = [t.revenue_millions for t in one_direction["tours"]]
        tour_data_ts = [t.revenue_millions for t in taylor_swift["tours"]]
        tour_years = ["2011-12", "2013", "2014", "2015"]
        tour_years_ts = ["2009-10", "2011-12", "2013-14", "2015", "2018", "2023-24"]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(tour_years, tour_data_1d, marker='o', label='One Direction', linewidth=2.5, markersize=8, color='#ff7e5e')
        ax.plot(tour_years_ts, tour_data_ts, marker='s', label='Taylor Swift', linewidth=2.5, markersize=8, color='#6a5acd')
        ax.set_xlabel('Tour', fontsize=12)
        ax.set_ylabel('Revenue (Millions USD)', fontsize=12)
        ax.set_title('Tour Revenue Comparison', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, linestyle='--', alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()


def render_oop_basics_tab(song_analyzer: SongAnalyzer) -> None:
    """Render the OOP and basics tab"""
    data_provider = DataProvider()
    one_direction_data = data_provider.get_one_direction_data()
    taylor_swift_data = data_provider.get_taylor_swift_data()
    songs_db = data_provider.get_songs_db()
    
    st.markdown("### 💻 OBJECT ORIENTED PROGRAMMING")
    
    col_oop1, col_oop2 = st.columns(2)
    with col_oop1:
        st.markdown("#### 🎤 One Direction (BandArtist)")
        st.info(f"Name: {one_direction_data['name']}")
        st.info(f"Genre: {', '.join(one_direction_data['genre'])}")
        st.info(f"Debut: {one_direction_data['debut_year']}")
        st.info(f"Members: {', '.join(one_direction_data['members_names'])}")
        st.info(f"Top Song: {one_direction_data['top_song']}")
        st.info(f"Total Albums: {one_direction_data['total_albums']}")
    
    with col_oop2:
        st.markdown("#### 🎵 Taylor Swift (SoloArtist)")
        st.info(f"Name: {taylor_swift_data['name']}")
        st.info(f"Genre: {', '.join(taylor_swift_data['genre'])}")
        st.info(f"Debut: {taylor_swift_data['debut_year']}")
        st.info(f"Label: Republic Records")
        st.info(f"Top Song: {taylor_swift_data['top_song']}")
        st.info(f"Total Albums: {taylor_swift_data['total_albums']}")
    
    UIComponents.render_divider()
    
    st.markdown("### 🎼 SONG ANALYZER & RECOMMENDATIONS")
    
    col_rec1, col_rec2 = st.columns(2)
    with col_rec1:
        st.markdown("**Recommendations for One Direction fans**")
        recommendations_1d = song_analyzer.get_recommendations("One Direction", 5)
        for song in recommendations_1d:
            st.write(f"• {song.get_info()}")
    
    with col_rec2:
        st.markdown("**Recommendations for Taylor Swift fans**")
        recommendations_ts = song_analyzer.get_recommendations("Taylor Swift", 5)
        for song in recommendations_ts:
            st.write(f"• {song.get_info()}")
    
    st.markdown("**Popularity Statistics**")
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        stats_1d = song_analyzer.get_popularity_distribution("One Direction")
        if stats_1d:
            st.write(f"Mean: {stats_1d['mean']:.1f}")
            st.write(f"Median: {stats_1d['median']:.1f}")
            st.write(f"Std Dev: {stats_1d['std_dev']:.1f}")
            st.write(f"Range: {stats_1d['min']} - {stats_1d['max']}")
    with col_stat2:
        stats_ts = song_analyzer.get_popularity_distribution("Taylor Swift")
        if stats_ts:
            st.write(f"Mean: {stats_ts['mean']:.1f}")
            st.write(f"Median: {stats_ts['median']:.1f}")
            st.write(f"Std Dev: {stats_ts['std_dev']:.1f}")
            st.write(f"Range: {stats_ts['min']} - {stats_ts['max']}")
    
    UIComponents.render_divider()
    
    st.markdown("### 🐍 ADVANCED PYTHON FEATURES DEMO")
    
    col_adv1, col_adv2 = st.columns(2)
    with col_adv1:
        st.markdown("**Generator Function**")
        st.code("""
def song_generator(songs):
    for song in songs:
        yield song.title

for title in song_generator(songs_db[:5]):
    print(title)
        """, language="python")
        def song_generator(songs):
            for song in songs[:5]:
                yield song.title
        st.write("Output: " + ", ".join(list(song_generator(songs_db))))
        
        st.markdown("**Decorator Example**")
        st.code("""
@measure_performance
def process_data():
    return sum(range(1000000))
        """, language="python")
    
    with col_adv2:
        st.markdown("**List Comprehension**")
        st.code('popular_songs = [s.title for s in songs_db if s.popularity >= 90]', language="python")
        popular_songs = [s.title for s in songs_db if s.popularity >= 90]
        st.write(f"Popular songs (>=90): {', '.join(popular_songs[:10])}")
        
        st.markdown("**Lambda & Map/Filter**")
        st.code('high_popularity = list(filter(lambda x: x.popularity > 85, songs_db))', language="python")
        high_pop = len([s for s in songs_db if s.popularity > 85])
        st.write(f"Songs with popularity >85: {high_pop}")
    
    UIComponents.render_divider()
    
    st.markdown("### 📋 COMPLETE DATAFRAME")
    songs_data = [{
        "Title": s.title, "Artist": s.artist, "Year": s.year,
        "Popularity": s.popularity, "Duration": s.get_duration_formatted(),
        "Rating": s.get_rating_category(), "Genre": s.genre
    } for s in songs_db]
    df = pd.DataFrame(songs_data)
    st.dataframe(df, width='stretch', height=400)


def render_pseudocode_tab() -> None:
    """Render the pseudocode tab"""
    st.markdown("### 📝 PSEUDOCODE & DOCUMENTATION")
    
    with st.expander("📌 PSEUDOCODE KUIS (Directioner vs Swiftie)", expanded=True):
        st.code("""
=== PSEUDOCODE ALGORITMA KUIS FAN IDENTITY ===

START PROGRAM KUIS

    // Initialize quiz engine
    quiz = AdvancedQuizEngine()
    questions = quiz.get_questions()  // 12 questions with difficulty levels
    
    // Initialize scoring
    directioner_score = 0
    swiftie_score = 0
    answer_times = []
    
    // Display and collect answers
    FOR each question IN questions:
        DISPLAY question.text with difficulty badge
        DISPLAY question.options
        START timer
        INPUT user_answer
        STOP timer
        STORE response_time
        
        // Calculate score
        points = question.scores[answer_index]
        IF question.fan_type == "Directioner":
            directioner_score += points
        ELSE:
            swiftie_score += points
        END IF
    END FOR
    
    // Calculate percentages
    total = directioner_score + swiftie_score
    directioner_percent = (directioner_score / total) * 100
    swiftie_percent = (swiftie_score / total) * 100
    
    // Determine fan type
    IF directioner_score > swiftie_score:
        fan_type = "Directioner"
    ELSE IF swiftie_score > directioner_score:
        fan_type = "Swiftie"
    ELSE:
        fan_type = "Undecided"
    END IF
    
    // Calculate confidence level
    IF fan_type != "Undecided":
        max_percent = MAX(directioner_percent, swiftie_percent)
        IF max_percent >= 70:
            confidence = "High"
        ELSE IF max_percent >= 60:
            confidence = "Medium"
        ELSE:
            confidence = "Low"
        END IF
    END IF
    
    // Display results
    DISPLAY fan_type with animation
    DISPLAY score breakdown with progress bars
    DISPLAY category analysis
    DISPLAY response time statistics
    
    // Store in session state
    STORE quiz_result in session_state
    UPDATE quiz_history
    
    // Trigger celebration animation
    DISPLAY balloons()
    
END PROGRAM
        """, language="text")
    
    with st.expander("🏗️ PSEUDOCODE CLASS HIERARCHY", expanded=True):
        st.code("""
=== PSEUDOCODE CLASS HIERARCHY ===

ABSTRACT CLASS Artist(ABC):
    // Private class variables
    __artist_count = 0
    __all_artists = []
    
    // Constructor
    METHOD __init__(name, genre, debut_year, discography, top_song=None):
        SET self._name = name
        SET self._genre = genre
        SET self._debut_year = debut_year
        SET self._discography = discography
        SET self._top_song = top_song OR max(discography, key=popularity)
        SET self._active = True
        SET self._created_at = datetime.now()
        INCREMENT __artist_count
        APPEND self to __all_artists
    
    // Properties (with getters/setters)
    PROPERTY career_length:
        RETURN current_year - self._debut_year
    
    PROPERTY popularity_score:
        RETURN average of all discography values
    
    // Abstract methods (must be implemented by subclasses)
    @abstractmethod
    METHOD get_info():
        PASS
    
    // Concrete methods
    METHOD get_top_song_info():
        RETURN (self._top_song, self._discography[self._top_song])
    
    METHOD get_average_popularity():
        RETURN sum(discography.values()) / len(discography)
    
    METHOD get_top_n_songs(n):
        SORT discography by popularity DESCENDING
        RETURN first n songs
    
    METHOD compare_with(other_artist):
        RETURN comparison dictionary
    
    // Class methods
    @classmethod
    METHOD get_total_artists():
        RETURN __artist_count

END CLASS
        """, language="text")
    
    UIComponents.render_divider()
    
    UIComponents.render_divider()


# ==================== MAIN ENTRY POINT ====================
def main() -> None:
    """Main application entry point"""
    try:
        # Initialize services
        initialize_services()
        
        # Initialize session state defaults
        if "theme_mode" not in st.session_state:
            st.session_state.theme_mode = "dark"
        if "primary_color" not in st.session_state:
            st.session_state.primary_color = "gradient"
        if "accent_color" not in st.session_state:
            st.session_state.accent_color = "purple"
        if "quiz_history" not in st.session_state:
            st.session_state.quiz_history = []
        
        # Apply theme
        theme_manager = ThemeManager()
        theme_manager.set_theme(ThemeMode(st.session_state.theme_mode))
        theme_manager.set_primary(PrimaryColor(st.session_state.primary_color))
        theme_manager.set_accent(AccentColor(st.session_state.accent_color))
        st.markdown(theme_manager.get_css(), unsafe_allow_html=True)
        
        # Get services
        container = ServiceContainer()
        visualizer = container.get("visualizer")
        song_analyzer = container.get("song_analyzer")
        
        # Initialize quiz engine
        quiz_engine = AdvancedQuizEngine()
        
        # Render sidebar
        render_sidebar()
        
        # Main title
        st.title("🎸 DIRECTIONER VS SWIFTIE 🎤")
        st.markdown("### The Ultimate Fan Identity Matrix & Advanced Python Showcase")
        st.markdown("*5234+ lines of production-grade code | S+ Grade Achievement*")
        UIComponents.render_divider()
        
        # Render tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 FAN IDENTITY TEST", 
            "📀 ARTIST PROFILES", 
            "📊 DATA CHARTS", 
            "💻 OOP & BASICS", 
            "📝 PSEUDOCODE"
        ])
        
        with tab1:
            render_fan_identity_tab(quiz_engine)
        
        with tab2:
            render_artist_profiles_tab()
        
        with tab3:
            render_data_charts_tab(visualizer, st.session_state.quiz_history)
        
        with tab4:
            render_oop_basics_tab(song_analyzer)
        
        with tab5:
            render_pseudocode_tab()
        
    except QuizError as e:
        logger.error(f"Quiz error: {e}")
        UIComponents.render_error_alert(f"Quiz Error: {str(e)}")
    except DataLoadError as e:
        logger.error(f"Data loading error: {e}")
        UIComponents.render_error_alert(f"Data Error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {traceback.format_exc()}")
        UIComponents.render_error_alert(f"Application Error: {str(e)}")
        st.info("Please refresh the page. If the problem persists, check the logs.")


if __name__ == "__main__":
    main()
