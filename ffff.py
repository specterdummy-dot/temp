import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
import time
import json
import os
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from collections import Counter
import math

st.set_page_config(
    page_title="DIRECTIONER VS SWIFTIE",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== THEME SETTINGS ====================
def init_theme_state():
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"
    if "primary_color" not in st.session_state:
        st.session_state.primary_color = "gradient"
    if "accent_color" not in st.session_state:
        st.session_state.accent_color = "purple"

init_theme_state()

def get_theme_css():
    if st.session_state.theme_mode == "dark":
        base_bg = "linear-gradient(135deg, #0b1120 0%, #19233c 25%, #1e2a4a 50%, #19233c 75%, #0b1120 100%)"
        card_bg = "rgba(30,41,59,0.7)"
        text_color = "#f5f5f7"
        text_secondary = "#cbd5e1"
        sidebar_bg = "#0f172a"
        border_color = "#334155"
        code_bg = "#1e293b"
    else:
        base_bg = "linear-gradient(135deg, #fef3c7 0%, #fde68a 25%, #fcd34d 50%, #fde68a 75%, #fef3c7 100%)"
        card_bg = "rgba(255,255,255,0.85)"
        text_color = "#1f2937"
        text_secondary = "#374151"
        sidebar_bg = "rgba(255,255,255,0.95)"
        border_color = "#d1d5db"
        code_bg = "#f3f4f6"
    
    if st.session_state.primary_color == "gradient":
        button_bg = "linear-gradient(90deg, #ff416c, #ff4b2b)"
        button_hover = "linear-gradient(90deg, #ff4b2b, #ff416c)"
        tab_active = "linear-gradient(120deg, #3b82f6, #8b5cf6)"
    elif st.session_state.primary_color == "blue":
        button_bg = "linear-gradient(90deg, #1e3c72, #2a5298)"
        button_hover = "linear-gradient(90deg, #2a5298, #1e3c72)"
        tab_active = "linear-gradient(120deg, #1e3c72, #2a5298)"
    elif st.session_state.primary_color == "green":
        button_bg = "linear-gradient(90deg, #11998e, #38ef7d)"
        button_hover = "linear-gradient(90deg, #38ef7d, #11998e)"
        tab_active = "linear-gradient(120deg, #11998e, #38ef7d)"
    else:
        button_bg = "linear-gradient(90deg, #ff416c, #ff4b2b)"
        button_hover = "linear-gradient(90deg, #ff4b2b, #ff416c)"
        tab_active = "linear-gradient(120deg, #ff416c, #ff4b2b)"
    
    if st.session_state.accent_color == "purple":
        chart_color_1 = "#ff7e5e"
        chart_color_2 = "#6a5acd"
        chart_color_3 = "#8b5cf6"
    elif st.session_state.accent_color == "blue":
        chart_color_1 = "#3b82f6"
        chart_color_2 = "#1e3c72"
        chart_color_3 = "#60a5fa"
    elif st.session_state.accent_color == "green":
        chart_color_1 = "#10b981"
        chart_color_2 = "#059669"
        chart_color_3 = "#34d399"
    else:
        chart_color_1 = "#ff7e5e"
        chart_color_2 = "#6a5acd"
        chart_color_3 = "#8b5cf6"
    
    return f"""
    <style>
        .stApp {{
            background: {base_bg} !important;
        }}
        h1, h2, h3, h4, h5, h6, .stMarkdown, label, .stSelectbox label, .stSlider label {{
            color: {text_color} !important;
        }}
        .stMarkdown p, .stMarkdown li, .stMarkdown span, .stText, .stCaption {{
            color: {text_secondary} !important;
        }}
        .stButton > button {{
            background: {button_bg} !important;
            color: white !important;
            border-radius: 30px !important;
            padding: 0.5rem 2rem !important;
            font-weight: bold !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
            transition: transform 0.2s !important;
        }}
        .stButton > button:hover {{
            transform: scale(1.02) !important;
            background: {button_hover} !important;
        }}
        .stSelectbox, .stSlider, .stTextInput {{
            background-color: rgba(255,255,255,0.05) !important;
            border-radius: 12px !important;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 24px !important;
            background: rgba(15,23,42,0.6) !important;
            border-radius: 30px !important;
            padding: 8px 16px !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 30px !important;
            padding: 8px 24px !important;
            font-weight: 600 !important;
            color: {text_secondary} !important;
        }}
        .stTabs [aria-selected="true"] {{
            background: {tab_active} !important;
            color: white !important;
        }}
        .metric-card {{
            background: {card_bg} !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 24px !important;
            padding: 20px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
        }}
        hr {{
            margin: 1rem 0 !important;
            border-color: {border_color} !important;
        }}
        .stSidebar {{
            background: {sidebar_bg} !important;
        }}
        code, .stCodeBlock {{
            background-color: {code_bg} !important;
            color: {text_color} !important;
        }}
        .custom-success {{
            background: linear-gradient(135deg, #10b981, #059669) !important;
            border-radius: 20px !important;
            padding: 20px !important;
            text-align: center !important;
            animation: pulse 2s infinite !important;
        }}
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }}
            70% {{ box-shadow: 0 0 0 20px rgba(16,185,129,0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(16,185,129,0); }}
        }}
        .glass-card {{
            background: {card_bg} !important;
            backdrop-filter: blur(12px) !important;
            border-radius: 32px !important;
            padding: 24px !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            transition: all 0.3s ease !important;
        }}
        .glass-card:hover {{
            transform: translateY(-5px) !important;
            background: rgba(255,255,255,0.08) !important;
        }}
        .theme-selector {{
            background: {card_bg} !important;
            border-radius: 16px !important;
            padding: 12px !important;
            margin-bottom: 16px !important;
        }}
    </style>
    """

st.markdown(get_theme_css(), unsafe_allow_html=True)

ONE_DIRECTION_DATA = {
    "name": "One Direction",
    "type": "Boy Band",
    "debut_year": 2010,
    "members": 5,
    "members_names": ["Harry Styles", "Niall Horan", "Liam Payne", "Louis Tomlinson", "Zayn Malik"],
    "genre": "Pop Rock / Teen Pop",
    "total_albums": 5,
    "albums": ["Up All Night", "Take Me Home", "Midnight Memories", "FOUR", "Made in the A.M."],
    "album_release_years": [2011, 2012, 2013, 2014, 2015],
    "album_sales_millions": [4.5, 5.2, 6.8, 5.9, 4.2],
    "songs": {
        "What Makes You Beautiful": 92,
        "Night Changes": 88,
        "Story of My Life": 90,
        "Drag Me Down": 85,
        "Perfect": 87,
        "Steal My Girl": 84,
        "Live While We're Young": 83,
        "Best Song Ever": 86,
        "Little Things": 79,
        "Kiss You": 81,
        "One Thing": 80,
        "Gotta Be You": 76,
        "Midnight Memories": 82,
        "You & I": 78,
        "No Control": 77
    },
    "top_song": "What Makes You Beautiful",
    "awards": 200,
    "tours": ["Up All Night Tour", "Take Me Home Tour", "Where We Are Tour", "On the Road Again Tour"],
    "social_media_followers_millions": 120,
    "spotify_streams_billions": 15
}

TAYLOR_SWIFT_DATA = {
    "name": "Taylor Swift",
    "type": "Solo Artist",
    "debut_year": 2006,
    "members": 1,
    "genre": "Pop / Country / Folk / Alternative",
    "total_albums": 10,
    "albums": ["Taylor Swift", "Fearless", "Speak Now", "Red", "1989", "Reputation", "Lover", "Folklore", "Evermore", "Midnights"],
    "album_release_years": [2006, 2008, 2010, 2012, 2014, 2017, 2019, 2020, 2020, 2022],
    "album_sales_millions": [3.5, 8.2, 6.5, 12.8, 15.2, 6.8, 7.5, 8.9, 6.2, 10.5],
    "songs": {
        "Love Story": 95,
        "You Belong With Me": 93,
        "Shake It Off": 98,
        "Blank Space": 97,
        "Bad Blood": 89,
        "Look What You Made Me Do": 86,
        "Cardigan": 91,
        "All Too Well": 100,
        "Anti-Hero": 94,
        "Style": 92,
        "Wildest Dreams": 90,
        "Delicate": 87,
        "ME!": 75,
        "Lover": 88,
        "Willow": 89,
        "August": 93,
        "Enchanted": 86,
        "Back to December": 84
    },
    "top_song": "All Too Well",
    "awards": 450,
    "tours": ["Fearless Tour", "Speak Now World Tour", "Red Tour", "1989 World Tour", "Reputation Stadium Tour", "The Eras Tour"],
    "social_media_followers_millions": 250,
    "spotify_streams_billions": 35
}

class Artist:
    __artist_count = 0
    __all_artists = []

    def __init__(self, name: str, genre: str, debut_year: int, discography: Dict[str, int], top_song: str = None):
        self.name = name
        self.genre = genre
        self.debut_year = debut_year
        self.discography = discography
        self.top_song = top_song if top_song else max(discography, key=discography.get)
        self._active = True
        self.created_at = datetime.now()
        Artist.__artist_count += 1
        Artist.__all_artists.append(self)

    @property
    def career_length(self) -> int:
        return datetime.now().year - self.debut_year

    @property
    def popularity_score(self) -> float:
        return sum(self.discography.values()) / len(self.discography) if self.discography else 0.0

    def info(self) -> str:
        return f"{self.name} | {self.genre} | Debut: {self.debut_year} | Career: {self.career_length} yrs | Popularity: {self.popularity_score:.1f}"

    def top_song_info(self) -> Tuple[str, int]:
        score = self.discography.get(self.top_song, 0)
        return self.top_song, score

    def average_popularity(self) -> float:
        return sum(self.discography.values()) / len(self.discography) if self.discography else 0.0

    def get_top_3_songs(self) -> List[Tuple[str, int]]:
        sorted_songs = sorted(self.discography.items(), key=lambda x: x[1], reverse=True)
        return sorted_songs[:3]

    def get_bottom_3_songs(self) -> List[Tuple[str, int]]:
        sorted_songs = sorted(self.discography.items(), key=lambda x: x[1])
        return sorted_songs[:3]

    def compare_with(self, other: 'Artist') -> Dict[str, Any]:
        return {
            "name_1": self.name,
            "name_2": other.name,
            "popularity_1": self.popularity_score,
            "popularity_2": other.popularity_score,
            "winner": self.name if self.popularity_score > other.popularity_score else other.name,
            "difference": abs(self.popularity_score - other.popularity_score)
        }

    @classmethod
    def get_total_artists(cls) -> int:
        return cls.__artist_count

    @classmethod
    def get_artist_list(cls) -> List['Artist']:
        return cls.__all_artists

    @staticmethod
    def format_popularity(score: int) -> str:
        if score >= 90:
            return "🌟 LEGENDARY"
        elif score >= 80:
            return "⭐ SUPERSTAR"
        elif score >= 70:
            return "🎵 HITMAKER"
        else:
            return "📀 RISING"

    def __str__(self) -> str:
        return f"Artist({self.name})"

    def __repr__(self) -> str:
        return f"Artist(name='{self.name}', genre='{self.genre}', debut={self.debut_year})"


class SoloArtist(Artist):
    solo_artist_count = 0

    def __init__(self, name: str, genre: str, debut_year: int, discography: Dict[str, int], label: str = "Independent", top_song: str = None, instrument: str = "Vocals"):
        super().__init__(name, genre, debut_year, discography, top_song)
        self.label = label
        self.instrument = instrument
        self.solo_projects = []
        SoloArtist.solo_artist_count += 1

    def info(self) -> str:
        base = super().info()
        return f"{base} | Label: {self.label} | Instrument: {self.instrument} | Solo Career"

    def add_solo_project(self, project_name: str, year: int):
        self.solo_projects.append({"project": project_name, "year": year})

    def get_solo_projects(self) -> List[Dict]:
        return self.solo_projects

    @classmethod
    def get_solo_count(cls) -> int:
        return cls.solo_artist_count


class BandArtist(Artist):
    band_count = 0

    def __init__(self, name: str, genre: str, debut_year: int, discography: Dict[str, int], members: int, members_names: List[str] = None, top_song: str = None):
        super().__init__(name, genre, debut_year, discography, top_song)
        self.members = members
        self.members_names = members_names if members_names else []
        self.is_active = True
        BandArtist.band_count += 1

    def info(self) -> str:
        base = super().info()
        return f"{base} | Members: {self.members} | Active: {self.is_active} | Band"

    def disband(self):
        self.is_active = False

    def get_members_list(self) -> str:
        if self.members_names:
            return ", ".join(self.members_names)
        return f"{self.members} members"

    @classmethod
    def get_band_count(cls) -> int:
        return cls.band_count


class Song:
    def __init__(self, title: str, artist: str, year: int, popularity: int, duration_seconds: int):
        self.title = title
        self.artist = artist
        self.year = year
        self.popularity = popularity
        self.duration_seconds = duration_seconds

    def duration_formatted(self) -> str:
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def rating_category(self) -> str:
        if self.popularity >= 90:
            return "Masterpiece"
        elif self.popularity >= 80:
            return "Hit Single"
        elif self.popularity >= 70:
            return "Album Track"
        else:
            return "Deep Cut"

    def info(self) -> str:
        return f"🎵 {self.title} - {self.artist} ({self.year}) | {self.duration_formatted()} | {self.rating_category()}"


class FanQuiz:
    def __init__(self):
        self.questions = self._generate_questions()
        self.scores = {"Directioner": 0, "Swiftie": 0}
        self.answers = []

    def _generate_questions(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "question": "Which era defines your music taste most?",
                "options": ["Up All Night (2011)", "1989 World Tour", "Midnights Lavender Haze", "FOUR Stadium"],
                "scores": [("Directioner", 2), ("Swiftie", 2), ("Swiftie", 1), ("Directioner", 2)]
            },
            {
                "id": 2,
                "question": "Pick your ultimate anthem:",
                "options": ["What Makes You Beautiful", "Shake It Off", "Night Changes", "All Too Well"],
                "scores": [("Directioner", 3), ("Swiftie", 2), ("Directioner", 2), ("Swiftie", 3)]
            },
            {
                "id": 3,
                "question": "Concert vibe you'd die for:",
                "options": ["Massive stadium with screaming harmonies", "Intimate acoustic storytelling", "High energy dance pop", "Rock-infused pop show"],
                "scores": [("Directioner", 3), ("Swiftie", 2), ("Swiftie", 2), ("Directioner", 1)]
            },
            {
                "id": 4,
                "question": "Favorite lyrical theme:",
                "options": ["Young love & adventure", "Heartbreak & self-reflection", "Revenge & reputation", "Nostalgia & friendship"],
                "scores": [("Directioner", 2), ("Swiftie", 3), ("Swiftie", 2), ("Directioner", 2)]
            },
            {
                "id": 5,
                "question": "Which album cover you prefer?",
                "options": ["Take Me Home (neon)", "1989 (polaroid)", "Midnight Memories (hotel)", "Folklore (black & white)"],
                "scores": [("Directioner", 2), ("Swiftie", 2), ("Directioner", 1), ("Swiftie", 3)]
            },
            {
                "id": 6,
                "question": "Band or solo superstar?",
                "options": ["5-member boyband chemistry", "Solo singer-songwriter domination", "Both legendary", "Group dynamic always wins"],
                "scores": [("Directioner", 3), ("Swiftie", 3), ("Directioner", 1), ("Directioner", 2)]
            },
            {
                "id": 7,
                "question": "Preferred music video style:",
                "options": ["Fun and energetic choreography", "Cinematic storytelling", "Behind the scenes raw footage", "High budget fantasy"],
                "scores": [("Directioner", 2), ("Swiftie", 2), ("Directioner", 1), ("Swiftie", 2)]
            },
            {
                "id": 8,
                "question": "Which decade of pop speaks to you?",
                "options": ["Early 2010s bubblegum pop", "Mid 2010s synth-pop", "Late 2010s alternative", "2020s indie folk"],
                "scores": [("Directioner", 3), ("Swiftie", 2), ("Swiftie", 1), ("Swiftie", 2)]
            },
            {
                "id": 9,
                "question": "Favorite fashion aesthetic:",
                "options": ["Leather jackets and skinny jeans", "Sparkly dresses and red lips", "Retro bohemian", "Dark edgy vibe"],
                "scores": [("Directioner", 2), ("Swiftie", 2), ("Swiftie", 1), ("Directioner", 1)]
            },
            {
                "id": 10,
                "question": "What makes a song legendary?",
                "options": ["Catchy chorus you can sing anywhere", "Lyrics that make you cry", "Danceable beat", "Powerful vocal performance"],
                "scores": [("Directioner", 2), ("Swiftie", 3), ("Directioner", 1), ("Directioner", 1)]
            }
        ]

    def answer_question(self, question_id: int, answer_index: int):
        q = next((q for q in self.questions if q["id"] == question_id), None)
        if q and answer_index < len(q["scores"]):
            fan_type, points = q["scores"][answer_index]
            self.scores[fan_type] += points
            self.answers.append({"question_id": question_id, "answer_index": answer_index, "fan_type": fan_type, "points": points})

    def compute_result(self) -> str:
        if self.scores["Directioner"] > self.scores["Swiftie"]:
            return "Kamu Directioner!"
        elif self.scores["Swiftie"] > self.scores["Directioner"]:
            return "Kamu Swiftie!"
        else:
            return random.choice(["Kamu Directioner!", "Kamu Swiftie!"])

    def get_detailed_report(self) -> Dict:
        total = sum(self.scores.values())
        return {
            "directioner_score": self.scores["Directioner"],
            "swiftie_score": self.scores["Swiftie"],
            "directioner_percent": (self.scores["Directioner"] / total * 100) if total > 0 else 0,
            "swiftie_percent": (self.scores["Swiftie"] / total * 100) if total > 0 else 0,
            "result": self.compute_result(),
            "total_answers": len(self.answers)
        }


def create_demo_objects():
    songs_db = []
    songs_db.append(Song("What Makes You Beautiful", "One Direction", 2011, 92, 212))
    songs_db.append(Song("Night Changes", "One Direction", 2014, 88, 226))
    songs_db.append(Song("Story of My Life", "One Direction", 2013, 90, 245))
    songs_db.append(Song("All Too Well (10 Minute Version)", "Taylor Swift", 2021, 100, 600))
    songs_db.append(Song("Shake It Off", "Taylor Swift", 2014, 98, 219))
    songs_db.append(Song("Blank Space", "Taylor Swift", 2014, 97, 231))
    songs_db.append(Song("Perfect", "One Direction", 2015, 87, 210))
    songs_db.append(Song("Drag Me Down", "One Direction", 2015, 85, 192))
    songs_db.append(Song("Anti-Hero", "Taylor Swift", 2022, 94, 200))
    songs_db.append(Song("Cardigan", "Taylor Swift", 2020, 91, 239))
    songs_db.append(Song("Best Song Ever", "One Direction", 2013, 86, 195))
    songs_db.append(Song("Cruel Summer", "Taylor Swift", 2019, 96, 178))
    songs_db.append(Song("Steal My Girl", "One Direction", 2014, 84, 228))
    songs_db.append(Song("Enchanted", "Taylor Swift", 2010, 86, 353))
    songs_db.append(Song("Live While We're Young", "One Direction", 2012, 83, 198))
    return songs_db


def get_quiz_questions() -> List[Dict[str, Any]]:
    fan_quiz = FanQuiz()
    return fan_quiz.questions


def compute_quiz_result(answers: List[str]) -> str:
    questions = get_quiz_questions()
    directioner_score = 0
    swiftie_score = 0

    for idx, ans in enumerate(answers):
        if idx >= len(questions) or ans is None:
            continue
        q = questions[idx]
        if ans not in q["options"]:
            continue
        opt_idx = q["options"].index(ans)
        if opt_idx < len(q["scores"]):
            fan_type, points = q["scores"][opt_idx]
            if fan_type == "Directioner":
                directioner_score += points
            else:
                swiftie_score += points

    if directioner_score > swiftie_score:
        return "Kamu Directioner!"
    elif swiftie_score > directioner_score:
        return "Kamu Swiftie!"
    else:
        return random.choice(["Kamu Directioner!", "Kamu Swiftie!"])


def compute_quiz_result_detailed(answers: List[str]) -> Tuple[str, int, int]:
    questions = get_quiz_questions()
    directioner_score = 0
    swiftie_score = 0

    for idx, ans in enumerate(answers):
        if idx >= len(questions) or ans is None:
            continue
        q = questions[idx]
        if ans not in q["options"]:
            continue
        opt_idx = q["options"].index(ans)
        if opt_idx < len(q["scores"]):
            fan_type, points = q["scores"][opt_idx]
            if fan_type == "Directioner":
                directioner_score += points
            else:
                swiftie_score += points

    if directioner_score > swiftie_score:
        return "Kamu Directioner!", directioner_score, swiftie_score
    elif swiftie_score > directioner_score:
        return "Kamu Swiftie!", directioner_score, swiftie_score
    else:
        return random.choice(["Kamu Directioner!", "Kamu Swiftie!"]), directioner_score, swiftie_score


def show_basics_demo():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📝 TYPE CASTING")
        str_num = "42"
        int_num = int(str_num)
        float_num = float("3.14159")
        str_bool = str(True)
        st.code(f"str('42') -> int: {int_num}\nstr('3.14') -> float: {float_num}\nbool(True) -> str: {str_bool}")
        a, b = 17, 5
        st.write(f"Arithmetic: {a}+{b}={a+b}, {a}-{b}={a-b}, {a}*{b}={a*b}, {a}/{b}={a/b:.2f}, {a}%{b}={a%b}")
    with col2:
        st.markdown("### 🔍 OPERATORS")
        x, y = 10, 3
        st.write(f"Comparison: {x} > {y} = {x > y}")
        st.write(f"Comparison: {x} == {y} = {x == y}")
        st.write(f"Logic: True and False = {True and False}")
        st.write(f"Logic: True or False = {True or False}")
        st.write(f"Logic: not True = {not True}")
        st.write(f"Bitwise: {x} & {y} = {x & y}")
        st.write(f"Bitwise: {x} | {y} = {x | y}")
    with col3:
        st.markdown("### 📊 ARRAYS & DICT")
        nilai_array = [95, 88, 92, 79, 100, 87, 93, 84, 91, 86]
        st.write(f"List nilai: {nilai_array}")
        st.write(f"Max: {max(nilai_array)}, Min: {min(nilai_array)}")
        st.write(f"Sum: {sum(nilai_array)}, Avg: {sum(nilai_array)/len(nilai_array):.1f}")
        directioner_dict = {"fandom": "Directioners", "active_years": "2010-2016", "hit_songs": 22, "albums": 5}
        swiftie_dict = {"fandom": "Swifties", "eras": 10, "grammys": 12, "albums": 10}
        st.json({"One Direction": directioner_dict, "Taylor Swift": swiftie_dict})


def show_oop_demo():
    st.markdown("### 🏗️ ARTIST OOP INSTANCES")
    
    colA, colB = st.columns(2)
    with colA:
        st.markdown("#### 🎤 One Direction (BandArtist)")
        st.info(one_direction.info())
        song, score = one_direction.top_song_info()
        st.metric("Top Song", song, delta=f"Pop: {score}/100")
        st.metric("Avg Popularity", f"{one_direction.average_popularity():.1f}/100")
        st.metric("Career Length", f"{one_direction.career_length} years")
        st.write(f"Members: {one_direction.get_members_list()}")
    
    with colB:
        st.markdown("#### 🎵 Taylor Swift (SoloArtist)")
        st.info(taylor_swift.info())
        song, score = taylor_swift.top_song_info()
        st.metric("Top Song", song, delta=f"Pop: {score}/100")
        st.metric("Avg Popularity", f"{taylor_swift.average_popularity():.1f}/100")
        st.metric("Career Length", f"{taylor_swift.career_length} years")
        st.write(f"Label: {taylor_swift.label}")
    
    st.markdown("### 📈 COMPARISON")
    comparison = one_direction.compare_with(taylor_swift)
    colC, colD, colE = st.columns(3)
    with colC:
        st.metric(comparison["name_1"], f"{comparison['popularity_1']:.1f}")
    with colD:
        st.metric(comparison["name_2"], f"{comparison['popularity_2']:.1f}")
    with colE:
        st.metric("WINNER", comparison["winner"])
    
    st.markdown("### 🎯 TOP 3 SONGS")
    colF, colG = st.columns(2)
    with colF:
        st.write("**One Direction Top 3**")
        for song, score in one_direction.get_top_3_songs():
            st.write(f"• {song}: {score}/100 ({Artist.format_popularity(score)})")
        st.write("**One Direction Bottom 3**")
        for song, score in one_direction.get_bottom_3_songs():
            st.write(f"• {song}: {score}/100")
    with colG:
        st.write("**Taylor Swift Top 3**")
        for song, score in taylor_swift.get_top_3_songs():
            st.write(f"• {song}: {score}/100 ({Artist.format_popularity(score)})")
        st.write("**Taylor Swift Bottom 3**")
        for song, score in taylor_swift.get_bottom_3_songs():
            st.write(f"• {song}: {score}/100")
    
    st.markdown(f"**Total Artists instantiated:** {Artist.get_total_artists()}")
    st.markdown(f"**Solo Artists:** {SoloArtist.get_solo_count()} | **Bands:** {BandArtist.get_band_count()}")
    
    st.code("""
class Artist:
    def info(self) -> str
    def top_song_info(self) -> Tuple
    def average_popularity(self) -> float
    def get_top_3_songs(self) -> List[Tuple]
    def compare_with(self, other) -> Dict
    @property career_length
    @property popularity_score
    
class SoloArtist(Artist):
    def add_solo_project(self, project_name, year)
    
class BandArtist(Artist):
    def disband(self)
    def get_members_list(self)
    """, language="python")


def render_bar_chart():
    songs_1d = list(ONE_DIRECTION_DATA["songs"].keys())[:6]
    scores_1d = [ONE_DIRECTION_DATA["songs"][s] for s in songs_1d]
    songs_ts = list(TAYLOR_SWIFT_DATA["songs"].keys())[:6]
    scores_ts = [TAYLOR_SWIFT_DATA["songs"][s] for s in songs_ts]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].barh(songs_1d, scores_1d, color='#ff7e5e', alpha=0.85, edgecolor='white', linewidth=1)
    axes[0].set_xlabel('Popularity Score', fontsize=10)
    axes[0].set_title('One Direction Top Songs', fontsize=12, fontweight='bold')
    axes[0].set_xlim(70, 100)
    for i, v in enumerate(scores_1d):
        axes[0].text(v + 1, i, str(v), va='center', fontweight='bold')
    
    axes[1].barh(songs_ts, scores_ts, color='#6a5acd', alpha=0.85, edgecolor='white', linewidth=1)
    axes[1].set_xlabel('Popularity Score', fontsize=10)
    axes[1].set_title('Taylor Swift Top Songs', fontsize=12, fontweight='bold')
    axes[1].set_xlim(70, 100)
    for i, v in enumerate(scores_ts):
        axes[1].text(v + 1, i, str(v), va='center', fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig)


def render_pie_chart():
    col1, col2 = st.columns(2)
    
    with col1:
        fan_dist = st.session_state.get("fan_distribution", {"Directioner": 62, "Swiftie": 38})
        fig1, ax1 = plt.subplots()
        wedges, texts, autotexts = ax1.pie(
            fan_dist.values(), 
            labels=fan_dist.keys(), 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=['#ff7e5e', '#6a5acd'],
            wedgeprops={'edgecolor': 'white', 'linewidth': 2},
            textprops={'fontsize': 12, 'fontweight': 'bold'}
        )
        ax1.set_title('Global Fan Distribution', fontsize=14, fontweight='bold')
        st.pyplot(fig1)
    
    with col2:
        album_sales = {
            "Up All Night": 4.5,
            "1989": 15.2,
            "FOUR": 5.9,
            "Red": 12.8,
            "Midnights": 10.5,
            "Fearless": 8.2
        }
        fig2, ax2 = plt.subplots()
        ax2.pie(
            album_sales.values(),
            labels=album_sales.keys(),
            autopct='%1.1f%%',
            startangle=45,
            colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0']
        )
        ax2.set_title('Album Sales Distribution (Selected)', fontsize=14, fontweight='bold')
        st.pyplot(fig2)


def render_line_chart():
    years_1d = ONE_DIRECTION_DATA["album_release_years"]
    sales_1d = ONE_DIRECTION_DATA["album_sales_millions"]
    years_ts = TAYLOR_SWIFT_DATA["album_release_years"]
    sales_ts = TAYLOR_SWIFT_DATA["album_sales_millions"]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(years_1d, sales_1d, marker='o', label='One Direction', linewidth=3, color='#ff7e5e', markersize=8)
    ax.plot(years_ts, sales_ts, marker='s', label='Taylor Swift', linewidth=3, color='#6a5acd', markersize=8)
    
    ax.set_xlabel('Release Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Album Sales (Millions)', fontsize=12, fontweight='bold')
    ax.set_title('Album Sales Trend Over Time', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_facecolor('#f8f9fa')
    
    for i, (x, y) in enumerate(zip(years_1d, sales_1d)):
        ax.annotate(f'{y}M', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)
    
    for i, (x, y) in enumerate(zip(years_ts[:len(sales_ts)], sales_ts)):
        ax.annotate(f'{y}M', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)
    
    st.pyplot(fig)


def render_multi_charts():
    st.markdown("### 📊 COMPREHENSIVE DATA VISUALIZATION")
    
    tab_chart1, tab_chart2, tab_chart3 = st.tabs(["Bar Chart", "Line Chart", "Scatter Plot"])
    
    with tab_chart1:
        fig, ax = plt.subplots(figsize=(10, 6))
        categories = ['Billboard #1', 'Grammy Wins', 'World Tours', 'Fan Awards', 'Studio Albums']
        one_d = [6, 0, 4, 200, 5]
        taylor = [9, 12, 6, 450, 10]
        
        x = np.arange(len(categories))
        width = 0.35
        
        ax.bar(x - width/2, one_d, width, label='One Direction', color='#ff7e5e')
        ax.bar(x + width/2, taylor, width, label='Taylor Swift', color='#6a5acd')
        
        ax.set_ylabel('Count', fontsize=11)
        ax.set_title('Career Achievements Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        st.pyplot(fig)
    
    with tab_chart2:
        years_1d = ONE_DIRECTION_DATA["album_release_years"]
        years_ts = TAYLOR_SWIFT_DATA["album_release_years"]
        cumulative_data = []
        for i, year in enumerate(years_ts[:8]):
            cumulative_data.append({
                'year': year,
                'One Direction': len([y for y in years_1d if y <= year]),
                'Taylor Swift': i + 1
            })
        df_cum = pd.DataFrame(cumulative_data)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df_cum['year'], df_cum['One Direction'], marker='o', label='One Direction', linewidth=2, markersize=8)
        ax.plot(df_cum['year'], df_cum['Taylor Swift'], marker='s', label='Taylor Swift', linewidth=2, markersize=8)
        ax.set_xlabel('Year')
        ax.set_ylabel('Cumulative Albums')
        ax.set_title('Cumulative Album Releases')
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.6)
        st.pyplot(fig)
    
    with tab_chart3:
        fig, ax = plt.subplots(figsize=(10, 6))
        album_years_1d = ONE_DIRECTION_DATA["album_release_years"]
        album_scores_1d = [85, 87, 86, 88, 85]
        album_years_ts = TAYLOR_SWIFT_DATA["album_release_years"][:8]
        album_scores_ts = [82, 85, 84, 90, 95, 87, 89, 91]
        
        ax.scatter(album_years_1d, album_scores_1d, s=200, c='#ff7e5e', marker='*', label='One Direction', edgecolors='white', linewidth=2)
        ax.scatter(album_years_ts, album_scores_ts, s=200, c='#6a5acd', marker='D', label='Taylor Swift', edgecolors='white', linewidth=2)
        
        ax.set_xlabel('Album Release Year', fontsize=12)
        ax.set_ylabel('Metacritic Score', fontsize=12)
        ax.set_title('Album Quality Over Time', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, linestyle='--', alpha=0.3)
        st.pyplot(fig)


def render_song_objects_demo(songs_db):
    st.markdown("### 🎼 SONG OBJECTS (Tugas Extended)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**One Direction Songs**")
        for song in songs_db[:5]:
            st.write(f"• {song.info()}")
    with col2:
        st.write("**Taylor Swift Songs**")
        for song in songs_db[3:8]:
            st.write(f"• {song.info()}")
    
    st.markdown("### 📋 SONG DATAFRAME")
    songs_data = []
    for song in songs_db:
        songs_data.append({
            "Title": song.title,
            "Artist": song.artist,
            "Year": song.year,
            "Popularity": song.popularity,
            "Duration": song.duration_formatted(),
            "Rating": song.rating_category()
        })
    df_songs = pd.DataFrame(songs_data)
    st.dataframe(df_songs, width='stretch')


def pseudocode_section():
    st.markdown("### 📝 PSEUDOCODE TUGAS 5")
    
    with st.expander("📌 PSEUDOCODE KUIS (Directioner vs Swiftie)", expanded=True):
        st.code("""
=== PSEUDOCODE ALGORITMA KUIS FAN IDENTITY ===

START PROGRAM KUIS

    INISIALISASI array questions DENGAN 10 pertanyaan
    SET setiap question memiliki:
        - id
        - teks pertanyaan
        - 4 opsi jawaban
        - skor untuk Directioner dan Swiftie
    
    INISIALISASI directioner_score = 0
    INISIALISASI swiftie_score = 0
    
    FOR setiap question IN questions:
        TAMPILKAN question.teks
        FOR setiap option IN question.options:
            TAMPILKAN option
        END FOR
        
        INPUT user_answer DARI user
        
        cari index dari user_answer dalam question.options
        ambil (fan_type, points) dari question.scores[index]
        
        IF fan_type == "Directioner":
            directioner_score = directioner_score + points
        ELSE IF fan_type == "Swiftie":
            swiftie_score = swiftie_score + points
        END IF
    END FOR
    
    IF directioner_score > swiftie_score:
        result = "Kamu Directioner!"
    ELSE IF swiftie_score > directioner_score:
        result = "Kamu Swiftie!"
    ELSE:
        result = random.choice(["Kamu Directioner!", "Kamu Swiftie!"])
    END IF
    
    TAMPILKAN result dengan animasi
    
END PROGRAM
        """, language="text")
    
    with st.expander("🏗️ PSEUDOCODE CLASS ARTIST + INHERITANCE", expanded=True):
        st.code("""
=== PSEUDOCODE CLASS ARTIST ===

CLASS Artist:
    ATRIBUT:
        - name (string)
        - genre (string)
        - debut_year (integer)
        - discography (dictionary: song_name -> popularity_score)
        - top_song (string)
        - _active (boolean)
        - created_at (datetime)
    
    METHOD __init__(name, genre, debut_year, discography, top_song=None):
        SET self.name = name
        SET self.genre = genre
        SET self.debut_year = debut_year
        SET self.discography = discography
        
        IF top_song IS None:
            cari song dengan popularity_score tertinggi dari discography
            SET self.top_song = song_tertinggi
        ELSE:
            SET self.top_song = top_song
        END IF
        
        SET self._active = True
        artist_count = artist_count + 1
    
    PROPERTY career_length:
        RETURN (current_year - debut_year)
    
    PROPERTY popularity_score:
        RETURN (sum of all popularity scores) / (jumlah songs)
    
    METHOD info():
        RETURN f"{name} | {genre} | Debut: {debut_year} | Career: {career_length} yrs"
    
    METHOD top_song_info():
        RETURN (top_song, discography[top_song])
    
    METHOD average_popularity():
        RETURN popularity_score
    
    METHOD get_top_3_songs():
        sort discography berdasarkan score descending
        RETURN 3 songs pertama
    
    METHOD get_bottom_3_songs():
        sort discography berdasarkan score ascending
        RETURN 3 songs terbawah
    
    METHOD compare_with(other_artist):
        IF popularity_score > other_artist.popularity_score:
            winner = self.name
        ELSE:
            winner = other_artist.name
        END IF
        RETURN dictionary of comparison results
    
    STATIC METHOD format_popularity(score):
        IF score >= 90: RETURN "🌟 LEGENDARY"
        ELSE IF score >= 80: RETURN "⭐ SUPERSTAR"
        ELSE IF score >= 70: RETURN "🎵 HITMAKER"
        ELSE: RETURN "📀 RISING"
        END IF

END CLASS


=== PSEUDOCODE SUBCLASS SOLOARTIST ===

CLASS SoloArtist INHERITS Artist:
    ATRIBUT TAMBAHAN:
        - label (string)
        - instrument (string)
        - solo_projects (list)
    
    METHOD __init__(name, genre, debut_year, discography, label, instrument, top_song=None):
        PANGGIL super().__init__(name, genre, debut_year, discography, top_song)
        SET self.label = label
        SET self.instrument = instrument
        SET self.solo_projects = []
        solo_artist_count = solo_artist_count + 1
    
    METHOD info():
        base_info = super().info()
        RETURN base_info + f" | Label: {label} | Solo Career"
    
    METHOD add_solo_project(project_name, year):
        APPEND {"project": project_name, "year": year} to solo_projects

END CLASS


=== PSEUDOCODE SUBCLASS BANDARTIST ===

CLASS BandArtist INHERITS Artist:
    ATRIBUT TAMBAHAN:
        - members (integer)
        - members_names (list)
        - is_active (boolean)
    
    METHOD __init__(name, genre, debut_year, discography, members, members_names, top_song=None):
        PANGGIL super().__init__(name, genre, debut_year, discography, top_song)
        SET self.members = members
        SET self.members_names = members_names
        SET self.is_active = True
        band_count = band_count + 1
    
    METHOD info():
        base_info = super().info()
        RETURN base_info + f" | Members: {members} | Band"
    
    METHOD disband():
        SET self.is_active = False
    
    METHOD get_members_list():
        IF members_names tidak kosong:
            RETURN join members_names dengan koma
        ELSE:
            RETURN f"{members} members"
        END IF

END CLASS
        """, language="text")
    
    with st.expander("🔄 FLOWCHART LOGIC (ALGORITMA UTAMA)", expanded=True):
        st.markdown("""
**ALUR PROGRAM UTAMA (Streamlit App):**

```
                                    START
                                       |
                                       v
                            CONFIGURE PAGE CONFIG
                       (title, layout, sidebar state)
                                       |
                                       v
                         INITIALIZE THEME STATE
                    (dark/light, primary color, accent)
                                       |
                                       v
                            APPLY CUSTOM CSS STYLES
                       (gradients, animations, cards)
                                       |
                                       v
                         INITIALIZE DATA CONSTANTS
                   (One Direction & Taylor Swift datasets)
                                       |
                                       v
                           DEFINE CLASSES
              Artist, SoloArtist, BandArtist, Song, FanQuiz
                                       |
                                       v
                        CREATE OBJECT INSTANCES
                 taylor_swift, one_direction, songs_db
                                       |
                                       v
                     DEFINE HELPER FUNCTIONS
                (quiz, charts, demos, pseudocode)
                                       |
                                       v
                          RENDER SIDEBAR
                 (metrics, analytics, theme selector, reset)
                                       |
                                       v
                          RENDER MAIN TABS
                                       |
               +---------------------------------------------------+
               |                                                   |
               v                                                   v
        TAB 1: FAN IDENTITY                               TAB 2: ARTIST PROFILES
               |                                                   |
               v                                                   v
        Display 10 questions                              Display JSON datasets
               |                                                   |
               v                                                   v
        User selects answers                              Show primitives demo
               |                                          (int, float, str, list, dict)
               v                                                   |
        Submit button                                             v
               |                                          Show array & dict operations
               v                                                   |
        Compute Directioner/Swiftie scores                         |
               |                                                   |
               v                                                   v
        Display result with animation                     TAB 3: DATA CHARTS
               |                                                   |
               |                                                   v
               |                                          Render Bar Chart
               |                                          (Top songs comparison)
               |                                                   |
               |                                                   v
               |                                          Render Pie Chart
               |                                          (Fan distribution)
               |                                                   |
               |                                                   v
               |                                          Render Line Chart
               |                                          (Sales trends)
               |                                                   |
               |                                                   v
               |                                          Render Multi Charts
               |                                          (Bar/Line/Scatter)
               |                                                   |
               |                                                   v
               |                                          TAB 4: OOP & BASICS
               |                                                   |
               |                                                   v
               |                                          Show OOP Demo
               |                                          (Artist instances)
               |                                                   |
               |                                                   v
               |                                          Show Python Basics
               |                                          (typecasting, operators)
               |                                                   |
               |                                                   v
               |                                          Show Song Objects
               |                                          (Extended demo)
               |                                                   |
               |                                                   v
               |                                          TAB 5: PSEUDOCODE
               |                                                   |
               |                                                   v
               |                                          Display pseudocode
               |                                          in expanders
               |                                                   |
               +---------------------------------------------------+
                                       |
                                       v
                                    END
```
        """)


def theme_selector():
    st.markdown("### 🎨 CUSTOMIZE THEME")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        new_theme = st.selectbox(
            "Theme Mode",
            options=["dark", "light"],
            index=0 if st.session_state.theme_mode == "dark" else 1,
            key="theme_selector_widget"
        )
    with col_t2:
        new_primary = st.selectbox(
            "Primary Color",
            options=["gradient", "blue", "green", "red"],
            index=["gradient", "blue", "green", "red"].index(st.session_state.primary_color),
            key="primary_selector_widget"
        )
    
    new_accent = st.selectbox(
        "Accent Color",
        options=["purple", "blue", "green", "pink"],
        index=["purple", "blue", "green", "pink"].index(st.session_state.accent_color),
        key="accent_selector_widget"
    )
    
    if new_theme != st.session_state.theme_mode:
        st.session_state.theme_mode = new_theme
        st.rerun()
    
    if new_primary != st.session_state.primary_color:
        st.session_state.primary_color = new_primary
        st.rerun()
    
    if new_accent != st.session_state.accent_color:
        st.session_state.accent_color = new_accent
        st.rerun()


def sidebar_metrics():
    with st.sidebar:
        st.markdown("## 🎯 ARTIST ANALYTICS")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("One Direction", "5 Albums", delta="2010-2015")
            st.metric("Billboard #1", "6 Hits")
            st.metric("World Tours", "4 Tours")
            st.metric("Members", "5")
        with col2:
            st.metric("Taylor Swift", "10 Albums", delta="2006-Present")
            st.metric("Grammy Awards", "12")
            st.metric("World Tours", "6 Tours")
            st.metric("Eras", "10")
        
        st.markdown("---")
        st.markdown("### 📊 STREAMING METRICS")
        st.metric("Global Streams (1D)", "15B", delta="+1.2B")
        st.metric("Global Streams (TS)", "35B", delta="+4.5B")
        st.metric("Social Followers (1D)", "120M")
        st.metric("Social Followers (TS)", "250M")
        
        
        st.markdown("---")
        theme_selector()
        
        st.markdown("---")
        if st.button("🔄 Reset Quiz Session", use_container_width=True):
            for key in ["quiz_answers", "quiz_result", "quiz_scores"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.caption("Made by zidan for Directioners & Swifties")


taylor_swift = SoloArtist(
    name=TAYLOR_SWIFT_DATA["name"],
    genre=TAYLOR_SWIFT_DATA["genre"],
    debut_year=TAYLOR_SWIFT_DATA["debut_year"],
    discography=TAYLOR_SWIFT_DATA["songs"],
    label="Republic Records",
    top_song=TAYLOR_SWIFT_DATA["top_song"]
)

one_direction = BandArtist(
    name=ONE_DIRECTION_DATA["name"],
    genre=ONE_DIRECTION_DATA["genre"],
    debut_year=ONE_DIRECTION_DATA["debut_year"],
    discography=ONE_DIRECTION_DATA["songs"],
    members=ONE_DIRECTION_DATA["members"],
    members_names=ONE_DIRECTION_DATA["members_names"],
    top_song=ONE_DIRECTION_DATA["top_song"]
)


def main():
    sidebar_metrics()
    
    st.title("🎸 DIRECTIONER   VS   SWIFTIE 🎤")
    st.markdown("### The Ultimate Fan Identity Matrix & Python Showcase")
    st.markdown("---")
    
    songs_db = create_demo_objects()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 FAN IDENTITY TEST", "📀 ARTIST PROFILES", "📊 DATA CHARTS", "💻 OOP & BASICS", "📝 PSEUDOCODE"])

    with tab1:
        st.markdown("### 🎪 FAN IDENTITY QUIZ")
        st.markdown("Answer all 10 questions to discover your true fandom allegiance")
        
        questions = get_quiz_questions()
        answers = []
        
        with st.form(key="quiz_form"):
            for idx, q in enumerate(questions):
                st.markdown(f"**{idx+1}. {q['question']}**")
                # FIXED: Added proper label instead of empty string
                ans = st.radio(
                    label=f"Question {idx+1}",
                    options=q["options"],
                    key=f"q_{idx}",
                    index=None,
                    horizontal=False,
                    label_visibility="collapsed"
                )
                answers.append(ans)
                st.markdown("---")
            
            submitted = st.form_submit_button("🔮 REVEAL MY FANDOM", use_container_width=True)
        
        if submitted:
            if all(a is not None for a in answers):
                result, d_score, s_score = compute_quiz_result_detailed(answers)
                st.session_state["quiz_result"] = result
                st.session_state["quiz_scores"] = {"Directioner": d_score, "Swiftie": s_score}
                
                st.markdown("---")
                col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
                with col_r2:
                    st.markdown(f"""
                    <div class="custom-success">
                        <h2 style="color: white; margin: 0;">{result}</h2>
                        <p style="color: white; margin-top: 10px;">🎵 Directioner Score: {d_score} | 🎤 Swiftie Score: {s_score}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("### 📈 SCORE BREAKDOWN")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    total = d_score + s_score
                    if total > 0:
                        st.progress(d_score / total)
                    else:
                        st.progress(0.5)
                    st.caption(f"Directioner: {d_score} points")
                with col_s2:
                    total = d_score + s_score
                    if total > 0:
                        st.progress(s_score / total)
                    else:
                        st.progress(0.5)
                    st.caption(f"Swiftie: {s_score} points")
                
                st.balloons()
            else:
                st.error("Please answer all 10 questions before submitting!")
        
        if "quiz_result" in st.session_state:
            st.info(f"✨ Last result: {st.session_state['quiz_result']} ✨")

    with tab2:
        st.markdown("### 🎤 ARTIST COMPARISON PROFILES")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ONE DIRECTION")
            st.json({
                "Full Name": ONE_DIRECTION_DATA["name"],
                "Type": ONE_DIRECTION_DATA["type"],
                "Debut Year": ONE_DIRECTION_DATA["debut_year"],
                "Members": ONE_DIRECTION_DATA["members_names"],
                "Genre": ONE_DIRECTION_DATA["genre"],
                "Total Albums": ONE_DIRECTION_DATA["total_albums"],
                "Albums": ONE_DIRECTION_DATA["albums"],
                "Top Tracks": list(ONE_DIRECTION_DATA["songs"].keys())[:5],
                "Awards": ONE_DIRECTION_DATA["awards"],
                "Tours": ONE_DIRECTION_DATA["tours"],
                "Spotify Streams": f"{ONE_DIRECTION_DATA['spotify_streams_billions']}B"
            })
        with col2:
            st.markdown("#### TAYLOR SWIFT")
            st.json({
                "Full Name": TAYLOR_SWIFT_DATA["name"],
                "Type": TAYLOR_SWIFT_DATA["type"],
                "Debut Year": TAYLOR_SWIFT_DATA["debut_year"],
                "Genre": TAYLOR_SWIFT_DATA["genre"],
                "Total Albums": TAYLOR_SWIFT_DATA["total_albums"],
                "Albums": TAYLOR_SWIFT_DATA["albums"],
                "Top Tracks": list(TAYLOR_SWIFT_DATA["songs"].keys())[:5],
                "Awards": TAYLOR_SWIFT_DATA["awards"],
                "Tours": TAYLOR_SWIFT_DATA["tours"],
                "Spotify Streams": f"{TAYLOR_SWIFT_DATA['spotify_streams_billions']}B"
            })
        
        st.markdown("---")
        st.markdown("### 📦 TIPE DATA & VARIABEL (Tugas 2)")
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.markdown("**Primitive Types**")
            st.write(f"String: '{ONE_DIRECTION_DATA['name']}'")
            st.write(f"Integer: {ONE_DIRECTION_DATA['total_albums']}")
            st.write(f"Float: {TAYLOR_SWIFT_DATA['album_sales_millions'][4]}M")
            st.write(f"Boolean: {True}")
        with col_d2:
            st.markdown("**Array / List**")
            st.write(f"1D Albums: {ONE_DIRECTION_DATA['albums']}")
            st.write(f"TS Albums: {TAYLOR_SWIFT_DATA['albums'][:3]}...")
            st.write(f"Max popularity: {max(TAYLOR_SWIFT_DATA['songs'].values())}")
        with col_d3:
            st.markdown("**Dictionary**")
            directioner_dict = {"fandom": "Directioners", "active": "2010-2016", "hit_songs": 22}
            swiftie_dict = {"fandom": "Swifties", "eras": 10, "grammys": 12}
            st.json({"1D Profile": directioner_dict, "TS Profile": swiftie_dict})
        
        st.markdown("---")
        st.markdown("### 🔄 TYPECASTING DEMO")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            str_num = "100"
            int_num = int(str_num)
            float_num = float(str_num)
            st.code(f"str('100') → int: {int_num}\nstr('100') → float: {float_num}\nint(3.14) → int: {int(3.14)}")
        with col_t2:
            int_val = 65
            str_val = str(int_val)
            float_val = float(int_val)
            st.code(f"int(65) → str: '{str_val}'\nint(65) → float: {float_val}\nfloat(99.9) → int: {int(99.9)}")

    with tab3:
        st.markdown("### 📊 DATA VISUALIZATION")
        render_bar_chart()
        render_pie_chart()
        render_line_chart()
        render_multi_charts()

    with tab4:
        st.markdown("### 💻 OBJECT ORIENTED PROGRAMMING")
        show_oop_demo()
        
        st.markdown("---")
        st.markdown("### 🎼 SONG OBJECTS DEMO")
        render_song_objects_demo(songs_db)
        
        st.markdown("---")
        st.markdown("### 🐍 PYTHON BASICS (Tugas 2)")
        show_basics_demo()
        
        st.markdown("---")
        st.markdown("### 🔧 LIST COMPREHENSION & LAMBDAS")
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            squares = [x**2 for x in nums]
            evens = [x for x in nums if x % 2 == 0]
            st.write(f"Original: {nums}")
            st.write(f"Squares: {squares}")
            st.write(f"Evens: {evens}")
        with col_l2:
            scores = [85, 92, 78, 90, 88, 95, 82]
            passed = list(filter(lambda x: x >= 85, scores))
            doubled = list(map(lambda x: x * 2, scores))
            st.write(f"Scores: {scores}")
            st.write(f"Passed (>=85): {passed}")
            st.write(f"Doubled: {doubled}")

    with tab5:
        pseudocode_section()
        
if __name__ == "__main__":
    if "fan_distribution" not in st.session_state:
        st.session_state["fan_distribution"] = {"Directioner": 62, "Swiftie": 38}
    
    try:
        main()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please refresh the page or check your Streamlit installation.")
