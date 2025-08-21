"""
Localization System for Cthulhu Solo TRPG

Provides multi-language support with:
- Korean and English text management
- Dynamic language switching
- Context-aware translations
- Fallback to English for missing translations
"""

import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from enum import Enum


logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages"""
    KOREAN = "ko"
    ENGLISH = "en"


class LocalizationManager:
    """
    Manages localization for the game system.
    
    Handles loading, caching, and providing localized text
    based on the current language setting.
    """
    
    def __init__(self, default_language: Language = Language.KOREAN):
        """Initialize the localization manager"""
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.fallback_language = Language.ENGLISH
        
        # Load built-in translations
        self._load_builtin_translations()
        
        logger.info(f"LocalizationManager initialized with language: {default_language.value}")
    
    def _load_builtin_translations(self):
        """Load built-in translation dictionaries"""
        # Korean translations
        korean_translations = {
            # Game system
            "game_title": "크툴루 솔로 TRPG",
            "welcome_message": "크툴루 신화 세계에 오신 것을 환영합니다!",
            "game_master": "게임 마스터",
            "player": "플레이어",
            
            # Character creation
            "character_creation": "캐릭터 생성",
            "character_name": "캐릭터 이름",
            "occupation": "직업",
            "age": "나이",
            "residence": "거주지",
            "birthplace": "출생지",
            
            # Character stats
            "strength": "근력",
            "constitution": "체질",
            "power": "정신력",
            "dexterity": "민첩성",
            "appearance": "외모",
            "size": "체격",
            "intelligence": "지능",
            "education": "교육",
            "hit_points": "체력",
            "magic_points": "마법력",
            "sanity_points": "정신력",
            "luck_points": "행운",
            
            # Game interface
            "turn_number": "턴 번호",
            "scene": "장면",
            "tension_level": "긴장도",
            "investigation_opportunities": "조사 기회",
            "story_threads": "스토리 진행",
            "character_sheet": "캐릭터 시트",
            "inventory": "인벤토리",
            "game_status": "게임 상태",
            
            # Actions and input
            "enter_action": "행동을 입력하세요",
            "processing": "처리 중...",
            "turn_completed": "턴 완료",
            "action_result": "행동 결과",
            "dice_roll": "주사위 굴림",
            "skill_check": "기능 판정",
            "investigation_result": "조사 결과",
            
            # Tension levels
            "tension_calm": "평온",
            "tension_uneasy": "불안",
            "tension_tense": "긴장",
            "tension_terrifying": "공포",
            "tension_cosmic_horror": "우주적 공포",
            
            # Success levels
            "critical_failure": "대실패",
            "failure": "실패",
            "success": "성공",
            "hard_success": "어려운 성공",
            "extreme_success": "극도의 성공",
            "critical_success": "대성공",
            
            # Game commands
            "help": "도움말",
            "character": "캐릭터",
            "save": "저장",
            "load": "불러오기",
            "quit": "종료",
            "settings": "설정",
            "statistics": "통계",
            "history": "기록",
            "clear": "지우기",
            
            # Error messages
            "error_occurred": "오류가 발생했습니다",
            "invalid_input": "잘못된 입력입니다",
            "character_not_loaded": "캐릭터가 로드되지 않았습니다",
            "save_failed": "저장에 실패했습니다",
            "load_failed": "불러오기에 실패했습니다",
            
            # Occupations
            "investigator": "조사원",
            "professor": "교수",
            "antiquarian": "골동품상",
            "archaeologist": "고고학자",
            "journalist": "기자",
            "private_investigator": "사립탐정",
            "physician": "의사",
            "occultist": "오컬티스트",
            
            # Skills
            "accounting": "회계",
            "anthropology": "인류학",
            "archaeology": "고고학",
            "charm": "매력",
            "climb": "등반",
            "dodge": "회피",
            "fast_talk": "빠른 말솜씨",
            "first_aid": "응급처치",
            "history": "역사",
            "intimidate": "위협",
            "library_use": "도서관 이용",
            "listen": "경청",
            "medicine": "의학",
            "occult": "오컬트",
            "persuade": "설득",
            "psychology": "심리학",
            "spot_hidden": "숨겨진 것 발견",
            "stealth": "은밀",
            "swim": "수영",
            "throw": "던지기",
            
            # Investigation templates
            "investigate_surroundings": "주변을 자세히 살펴본다",
            "examine_floor": "바닥에 떨어진 것들을 확인한다",
            "check_walls": "벽면을 점검한다",
            "look_for_passages": "숨겨진 통로나 문을 찾는다",
            "track_smell": "이상한 냄새의 근원을 추적한다",
            "search_furniture": "가구 아래를 들여다본다",
            "examine_books": "책장이나 책들을 조사한다",
            "observe_window": "창문 밖을 관찰한다",
            "check_electrical": "조명이나 전기 시설을 확인한다",
            
            # Narrative elements
            "mysterious_atmosphere": "신비로운 분위기",
            "unsettling_feeling": "불안한 기분",
            "eerie_silence": "음산한 정적",
            "strange_sounds": "이상한 소리",
            "shadows_moving": "움직이는 그림자",
            "cold_breeze": "차가운 바람",
            "musty_smell": "곰팡이 냄새",
            "ancient_presence": "고대의 존재감",
            
            # Common scenarios
            "old_house": "오래된 저택",
            "dark_library": "어둠에 싸인 도서관",
            "mysterious_basement": "수상한 지하실",
            "abandoned_church": "버려진 교회",
            "fog_covered_street": "안개로 덮인 거리",
            "university_campus": "대학교 캠퍼스",
            "rural_village": "시골 마을",
            "cemetery": "묘지",
        }
        
        # English translations (fallback)
        english_translations = {
            "game_title": "Cthulhu Solo TRPG",
            "welcome_message": "Welcome to the world of Cthulhu Mythos!",
            "game_master": "Game Master",
            "player": "Player",
            
            "character_creation": "Character Creation",
            "character_name": "Character Name",
            "occupation": "Occupation",
            "age": "Age",
            "residence": "Residence",
            "birthplace": "Birthplace",
            
            "strength": "Strength",
            "constitution": "Constitution",
            "power": "Power",
            "dexterity": "Dexterity",
            "appearance": "Appearance",
            "size": "Size",
            "intelligence": "Intelligence",
            "education": "Education",
            "hit_points": "Hit Points",
            "magic_points": "Magic Points",
            "sanity_points": "Sanity Points",
            "luck_points": "Luck Points",
            
            "turn_number": "Turn Number",
            "scene": "Scene",
            "tension_level": "Tension Level",
            "investigation_opportunities": "Investigation Opportunities",
            "story_threads": "Story Progress",
            "character_sheet": "Character Sheet",
            "inventory": "Inventory",
            "game_status": "Game Status",
            
            "enter_action": "Enter your action",
            "processing": "Processing...",
            "turn_completed": "Turn completed",
            "action_result": "Action Result",
            "dice_roll": "Dice Roll",
            "skill_check": "Skill Check",
            "investigation_result": "Investigation Result",
            
            "tension_calm": "Calm",
            "tension_uneasy": "Uneasy",
            "tension_tense": "Tense",
            "tension_terrifying": "Terrifying",
            "tension_cosmic_horror": "Cosmic Horror",
            
            "critical_failure": "Critical Failure",
            "failure": "Failure",
            "success": "Success",
            "hard_success": "Hard Success",
            "extreme_success": "Extreme Success",
            "critical_success": "Critical Success",
            
            "help": "Help",
            "character": "Character",
            "save": "Save",
            "load": "Load",
            "quit": "Quit",
            "settings": "Settings",
            "statistics": "Statistics",
            "history": "History",
            "clear": "Clear",
            
            "error_occurred": "An error occurred",
            "invalid_input": "Invalid input",
            "character_not_loaded": "Character not loaded",
            "save_failed": "Save failed",
            "load_failed": "Load failed",
            
            "investigator": "Investigator",
            "professor": "Professor",
            "antiquarian": "Antiquarian",
            "archaeologist": "Archaeologist",
            "journalist": "Journalist",
            "private_investigator": "Private Investigator",
            "physician": "Physician",
            "occultist": "Occultist",
        }
        
        self.translations[Language.KOREAN.value] = korean_translations
        self.translations[Language.ENGLISH.value] = english_translations
    
    def set_language(self, language: Language):
        """Set the current language"""
        self.current_language = language
        logger.info(f"Language changed to: {language.value}")
    
    def get_text(self, key: str, **kwargs) -> str:
        """
        Get localized text for a key.
        
        Args:
            key: Translation key
            **kwargs: Format arguments for the text
            
        Returns:
            Localized text or key if translation not found
        """
        # Try current language
        current_translations = self.translations.get(self.current_language.value, {})
        text = current_translations.get(key)
        
        # Fallback to English if not found
        if text is None:
            fallback_translations = self.translations.get(self.fallback_language.value, {})
            text = fallback_translations.get(key)
        
        # Use key as fallback if translation completely missing
        if text is None:
            logger.warning(f"Missing translation for key: {key}")
            text = key
        
        # Apply formatting if provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to format text for key '{key}': {e}")
        
        return text
    
    def get_tension_level_text(self, tension_level: str) -> str:
        """Get localized text for tension level"""
        tension_map = {
            "calm": "tension_calm",
            "uneasy": "tension_uneasy",
            "tense": "tension_tense",
            "terrifying": "tension_terrifying",
            "cosmic_horror": "tension_cosmic_horror"
        }
        
        key = tension_map.get(tension_level.lower(), "tension_calm")
        return self.get_text(key)
    
    def get_success_level_text(self, success_level: str) -> str:
        """Get localized text for success level"""
        success_map = {
            "critical_failure": "critical_failure",
            "failure": "failure",
            "success": "success",
            "hard_success": "hard_success",
            "extreme_success": "extreme_success",
            "critical_success": "critical_success"
        }
        
        key = success_map.get(success_level.lower(), "success")
        return self.get_text(key)
    
    def get_occupation_text(self, occupation: str) -> str:
        """Get localized text for occupation"""
        return self.get_text(occupation.lower(), default=occupation)
    
    def load_external_translations(self, file_path: str):
        """
        Load translations from external JSON file.
        
        Args:
            file_path: Path to JSON file with translations
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"Translation file not found: {file_path}")
                return
            
            with open(path, 'r', encoding='utf-8') as f:
                external_translations = json.load(f)
            
            # Merge with existing translations
            for lang, translations in external_translations.items():
                if lang not in self.translations:
                    self.translations[lang] = {}
                self.translations[lang].update(translations)
            
            logger.info(f"Loaded external translations from: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load external translations: {e}")
    
    def save_translations(self, file_path: str, language: Optional[Language] = None):
        """
        Save translations to JSON file.
        
        Args:
            file_path: Output file path
            language: Specific language to save (all if None)
        """
        try:
            if language:
                data = {language.value: self.translations.get(language.value, {})}
            else:
                data = self.translations
            
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved translations to: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save translations: {e}")
    
    def get_available_languages(self) -> List[str]:
        """Get list of available language codes"""
        return list(self.translations.keys())
    
    def get_translation_coverage(self, language: Language) -> float:
        """
        Get translation coverage percentage for a language.
        
        Args:
            language: Language to check
            
        Returns:
            Coverage percentage (0.0 to 1.0)
        """
        if language.value not in self.translations:
            return 0.0
        
        current_translations = self.translations[language.value]
        fallback_translations = self.translations.get(self.fallback_language.value, {})
        
        if not fallback_translations:
            return 1.0  # No fallback to compare against
        
        total_keys = len(fallback_translations)
        translated_keys = len(current_translations)
        
        return min(translated_keys / total_keys, 1.0) if total_keys > 0 else 1.0


# Global localization manager instance
_localization_manager: Optional[LocalizationManager] = None


def get_localization_manager() -> LocalizationManager:
    """Get the global localization manager instance"""
    global _localization_manager
    if _localization_manager is None:
        _localization_manager = LocalizationManager()
    return _localization_manager


def set_language(language: Language):
    """Set the global language"""
    manager = get_localization_manager()
    manager.set_language(language)


def get_text(key: str, **kwargs) -> str:
    """Get localized text using the global manager"""
    manager = get_localization_manager()
    return manager.get_text(key, **kwargs)


def t(key: str, **kwargs) -> str:
    """Shorthand function for getting localized text"""
    return get_text(key, **kwargs)


# Common text functions
def get_tension_text(level: str) -> str:
    """Get tension level text"""
    return get_localization_manager().get_tension_level_text(level)


def get_success_text(level: str) -> str:
    """Get success level text"""
    return get_localization_manager().get_success_level_text(level)


def get_occupation_text(occupation: str) -> str:
    """Get occupation text"""
    return get_localization_manager().get_occupation_text(occupation)