"""
Save Manager for Cthulhu Horror TRPG

Handles saving and loading of game states, character data, and campaign progress.
Specialized for Cthulhu mythos gaming with sanity tracking, mythos knowledge,
and investigation progress.
"""

import json
import gzip
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class CthulhuCharacterData:
    """Structured data for Cthulhu character saves."""
    # Basic Character Info
    name: str
    age: int
    occupation: str
    residence: str
    birthplace: str
    
    # Core Attributes
    strength: int
    constitution: int
    power: int
    dexterity: int
    appearance: int
    size: int
    intelligence: int
    education: int
    
    # Derived Attributes
    hit_points_current: int
    hit_points_maximum: int
    sanity_current: int
    sanity_maximum: int
    sanity_starting: int
    magic_points_current: int
    magic_points_maximum: int
    
    # Skills (dict of skill_name: skill_data)
    skills: Dict[str, Dict[str, Any]]
    
    # Mythos-specific data
    mythos_knowledge: int = 0
    mythos_tomes_read: List[str] = None
    spells_known: List[str] = None
    phobias: List[str] = None
    manias: List[str] = None
    
    # Equipment and possessions
    possessions: List[str] = None
    weapons: List[Dict[str, Any]] = None
    cash_and_assets: Dict[str, float] = None
    
    # Investigation data
    clues_discovered: List[str] = None
    locations_visited: List[str] = None
    contacts_met: List[str] = None
    
    # Character development
    experience_points: int = 0
    skill_improvements: Dict[str, int] = None
    
    def __post_init__(self):
        """Initialize mutable default values."""
        if self.mythos_tomes_read is None:
            self.mythos_tomes_read = []
        if self.spells_known is None:
            self.spells_known = []
        if self.phobias is None:
            self.phobias = []
        if self.manias is None:
            self.manias = []
        if self.possessions is None:
            self.possessions = []
        if self.weapons is None:
            self.weapons = []
        if self.cash_and_assets is None:
            self.cash_and_assets = {}
        if self.clues_discovered is None:
            self.clues_discovered = []
        if self.locations_visited is None:
            self.locations_visited = []
        if self.contacts_met is None:
            self.contacts_met = []
        if self.skill_improvements is None:
            self.skill_improvements = {}


@dataclass  
class CthulhuGameSession:
    """Data structure for current game session."""
    session_id: str
    start_time: datetime
    current_scenario: str
    current_location: str
    current_turn: int
    game_master_notes: str
    
    # Investigation state
    investigation_phase: str  # "preparation", "investigation", "confrontation", "resolution"
    active_leads: List[str]
    completed_leads: List[str]
    mythos_rating: int  # How deep into mythos territory
    
    # Environmental factors
    time_of_day: str
    weather: str
    season: str
    
    # AI Agent memory
    agent_memories: Dict[str, List[Dict[str, Any]]]
    story_context: List[str]
    recent_events: List[Dict[str, Any]]
    
    # Session statistics
    sanity_lost_this_session: int = 0
    skill_checks_made: int = 0
    critical_successes: int = 0
    fumbles: int = 0
    
    def __post_init__(self):
        """Initialize mutable default values."""
        if self.active_leads is None:
            self.active_leads = []
        if self.completed_leads is None:
            self.completed_leads = []
        if self.agent_memories is None:
            self.agent_memories = {}
        if self.story_context is None:
            self.story_context = []
        if self.recent_events is None:
            self.recent_events = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        return data


class CthulhuSaveManager:
    """Enhanced save manager for Cthulhu Horror TRPG."""
    
    def __init__(self, saves_directory: str):
        """
        Initialize the Cthulhu-specific save manager.
        
        Args:
            saves_directory: Base directory for save files
        """
        self.saves_directory = Path(saves_directory)
        self.saves_directory.mkdir(parents=True, exist_ok=True)
        
        # Create specialized subdirectories
        self.character_saves_dir = self.saves_directory / "characters"
        self.campaign_saves_dir = self.saves_directory / "campaigns"
        self.investigation_saves_dir = self.saves_directory / "investigations"
        self.backup_dir = self.saves_directory / "backups"
        
        for directory in [self.character_saves_dir, self.campaign_saves_dir, 
                         self.investigation_saves_dir, self.backup_dir]:
            directory.mkdir(exist_ok=True)
        
        logger.info(f"Cthulhu Save Manager initialized at {self.saves_directory}")
    
    def create_game_state(self, character: CthulhuCharacterData, 
                         session: CthulhuGameSession,
                         ai_agent_states: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a complete game state dictionary.
        
        Args:
            character: Character data
            session: Session data
            ai_agent_states: Optional AI agent states
            
        Returns:
            Complete game state dictionary
        """
        game_state = {
            "save_version": "1.0.0",
            "save_timestamp": datetime.now().isoformat(),
            "player_character": asdict(character),
            "session_data": session.to_dict(),
            "ai_agents": ai_agent_states or {},
            
            # Cthulhu-specific metadata
            "mythos_exposure_level": self._calculate_mythos_exposure(character),
            "sanity_status": self._determine_sanity_status(character),
            "investigation_progress": self._calculate_investigation_progress(session),
            
            # Game statistics
            "total_play_time": 0,  # Will be calculated
            "scenarios_completed": [],
            "notable_events": [],
            
            # System metadata
            "system_info": {
                "game_engine_version": "1.0.0",
                "save_format": "cthulhu_json_v1",
                "compression": True
            }
        }
        
        return game_state
    
    def save_game(self, game_state: Dict[str, Any], save_name: str,
                  compress: bool = True, create_backup: bool = True) -> bool:
        """
        Save complete game state.
        
        Args:
            game_state: Complete game state dictionary
            save_name: Name for the save file
            compress: Whether to compress the save file
            create_backup: Whether to create a backup
            
        Returns:
            True if save successful
        """
        try:
            # Ensure save name is valid
            safe_save_name = self._sanitize_filename(save_name)
            save_path = self.campaign_saves_dir / f"{safe_save_name}.json"
            
            if compress:
                save_path = save_path.with_suffix('.json.gz')
            
            # Create backup if file exists
            if create_backup and save_path.exists():
                self.create_backup(save_path)
            
            # Add save metadata
            game_state["save_metadata"] = {
                "save_name": save_name,
                "save_path": str(save_path),
                "save_time": datetime.now().isoformat(),
                "file_hash": self._calculate_hash(game_state),
                "compressed": compress
            }
            
            # Save the file
            json_data = json.dumps(game_state, indent=2, ensure_ascii=False, default=str)
            
            if compress:
                with gzip.open(save_path, 'wt', encoding='utf-8') as f:
                    f.write(json_data)
            else:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(json_data)
            
            logger.info(f"Game saved: {save_name} -> {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save game '{save_name}': {e}")
            return False
    
    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        """
        Load complete game state.
        
        Args:
            save_name: Name of save file to load
            
        Returns:
            Game state dictionary, or None if load failed
        """
        try:
            safe_save_name = self._sanitize_filename(save_name)
            
            # Try compressed version first
            save_path = self.campaign_saves_dir / f"{safe_save_name}.json.gz"
            if not save_path.exists():
                save_path = self.campaign_saves_dir / f"{safe_save_name}.json"
            
            if not save_path.exists():
                logger.warning(f"Save file not found: {save_name}")
                return None
            
            # Load the file
            if save_path.suffix == '.gz':
                with gzip.open(save_path, 'rt', encoding='utf-8') as f:
                    game_state = json.load(f)
            else:
                with open(save_path, 'r', encoding='utf-8') as f:
                    game_state = json.load(f)
            
            # Verify integrity
            if not self._verify_save_integrity(game_state):
                logger.warning(f"Save file integrity check failed: {save_name}")
            
            logger.info(f"Game loaded: {save_name}")
            return game_state
            
        except Exception as e:
            logger.error(f"Failed to load game '{save_name}': {e}")
            return None
    
    def save_character_only(self, character: CthulhuCharacterData, 
                           filename: str) -> bool:
        """
        Save character data separately.
        
        Args:
            character: Character data to save
            filename: Filename for character save
            
        Returns:
            True if save successful
        """
        try:
            safe_filename = self._sanitize_filename(filename)
            save_path = self.character_saves_dir / f"{safe_filename}.json"
            
            character_data = {
                "save_type": "character",
                "save_timestamp": datetime.now().isoformat(),
                "character_data": asdict(character),
                "character_summary": {
                    "name": character.name,
                    "occupation": character.occupation,
                    "current_sanity": character.sanity_current,
                    "mythos_knowledge": character.mythos_knowledge,
                    "experience_points": character.experience_points
                }
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Character saved: {character.name} -> {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save character '{filename}': {e}")
            return False
    
    def load_character(self, filename: str) -> Optional[CthulhuCharacterData]:
        """
        Load character data.
        
        Args:
            filename: Character file to load
            
        Returns:
            Character data, or None if load failed
        """
        try:
            safe_filename = self._sanitize_filename(filename)
            save_path = self.character_saves_dir / f"{safe_filename}.json"
            
            if not save_path.exists():
                logger.warning(f"Character file not found: {filename}")
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            # Convert back to CthulhuCharacterData
            char_dict = character_data.get("character_data", {})
            character = CthulhuCharacterData(**char_dict)
            
            logger.info(f"Character loaded: {character.name}")
            return character
            
        except Exception as e:
            logger.error(f"Failed to load character '{filename}': {e}")
            return None
    
    def list_saves(self, save_type: str = "all") -> List[Dict[str, Any]]:
        """
        List available save files with metadata.
        
        Args:
            save_type: Type of saves to list ("all", "campaigns", "characters", "investigations")
            
        Returns:
            List of save file information
        """
        saves = []
        
        directories = {
            "campaigns": self.campaign_saves_dir,
            "characters": self.character_saves_dir,
            "investigations": self.investigation_saves_dir
        }
        
        if save_type == "all":
            search_dirs = directories.values()
        elif save_type in directories:
            search_dirs = [directories[save_type]]
        else:
            logger.warning(f"Unknown save type: {save_type}")
            return saves
        
        for directory in search_dirs:
            try:
                for save_file in directory.glob("*.json*"):
                    save_info = self._extract_save_info(save_file)
                    if save_info:
                        saves.append(save_info)
            except Exception as e:
                logger.error(f"Error listing saves in {directory}: {e}")
        
        # Sort by modification time, newest first
        saves.sort(key=lambda x: x.get('modified_time', datetime.min), reverse=True)
        return saves
    
    def delete_save(self, save_name: str, save_type: str = "campaigns") -> bool:
        """
        Delete a save file.
        
        Args:
            save_name: Name of save to delete
            save_type: Type of save ("campaigns", "characters", "investigations")
            
        Returns:
            True if deletion successful
        """
        try:
            directories = {
                "campaigns": self.campaign_saves_dir,
                "characters": self.character_saves_dir,
                "investigations": self.investigation_saves_dir
            }
            
            if save_type not in directories:
                logger.error(f"Unknown save type: {save_type}")
                return False
            
            directory = directories[save_type]
            safe_save_name = self._sanitize_filename(save_name)
            
            # Try both compressed and uncompressed versions
            for suffix in [".json.gz", ".json"]:
                save_path = directory / f"{safe_save_name}{suffix}"
                if save_path.exists():
                    # Create backup before deletion
                    self.create_backup(save_path)
                    save_path.unlink()
                    logger.info(f"Deleted save: {save_name}")
                    return True
            
            logger.warning(f"Save file not found for deletion: {save_name}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete save '{save_name}': {e}")
            return False
    
    def create_backup(self, save_path: Path) -> Optional[Path]:
        """
        Create backup of save file.
        
        Args:
            save_path: Path to save file
            
        Returns:
            Path to backup file, or None if backup failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{save_path.stem}_backup_{timestamp}{save_path.suffix}"
            backup_path = self.backup_dir / backup_name
            
            if save_path.exists():
                with open(save_path, 'rb') as src:
                    with open(backup_path, 'wb') as dst:
                        dst.write(src.read())
                
                logger.info(f"Backup created: {backup_path}")
                return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create backup for {save_path}: {e}")
        
        return None
    
    def export_character(self, character: CthulhuCharacterData, 
                        export_path: Path) -> bool:
        """
        Export character to external file.
        
        Args:
            character: Character to export
            export_path: Path for exported file
            
        Returns:
            True if export successful
        """
        try:
            export_data = {
                "export_type": "cthulhu_character",
                "export_timestamp": datetime.now().isoformat(),
                "game_system": "Call of Cthulhu",
                "character_data": asdict(character),
                "export_summary": {
                    "character_name": character.name,
                    "occupation": character.occupation,
                    "sanity_remaining": character.sanity_current,
                    "mythos_exposure": character.mythos_knowledge
                }
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Character exported: {character.name} -> {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export character: {e}")
            return False
    
    def import_character(self, import_path: Path) -> Optional[CthulhuCharacterData]:
        """
        Import character from external file.
        
        Args:
            import_path: Path to character file
            
        Returns:
            Imported character data, or None if import failed
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if import_data.get("export_type") != "cthulhu_character":
                logger.error("Invalid character export file format")
                return None
            
            char_dict = import_data.get("character_data", {})
            character = CthulhuCharacterData(**char_dict)
            
            logger.info(f"Character imported: {character.name}")
            return character
            
        except Exception as e:
            logger.error(f"Failed to import character from {import_path}: {e}")
            return None
    
    def get_save_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive save statistics.
        
        Returns:
            Dictionary with save system statistics
        """
        stats = {
            "total_saves": 0,
            "save_types": {
                "campaigns": 0,
                "characters": 0,
                "investigations": 0,
                "backups": 0
            },
            "disk_usage": {
                "total_size_mb": 0,
                "by_type": {}
            },
            "recent_activity": {
                "last_save": None,
                "saves_this_week": 0
            }
        }
        
        directories = {
            "campaigns": self.campaign_saves_dir,
            "characters": self.character_saves_dir,
            "investigations": self.investigation_saves_dir,
            "backups": self.backup_dir
        }
        
        week_ago = datetime.now() - timedelta(days=7)
        
        for save_type, directory in directories.items():
            try:
                files = list(directory.glob("*.json*"))
                stats["save_types"][save_type] = len(files)
                stats["total_saves"] += len(files)
                
                type_size = 0
                for file_path in files:
                    size = file_path.stat().st_size
                    type_size += size
                    
                    # Check recent activity
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mod_time > week_ago:
                        stats["recent_activity"]["saves_this_week"] += 1
                    
                    # Track latest save
                    if (stats["recent_activity"]["last_save"] is None or 
                        mod_time > stats["recent_activity"]["last_save"]):
                        stats["recent_activity"]["last_save"] = mod_time
                
                stats["disk_usage"]["by_type"][save_type] = round(type_size / (1024 * 1024), 2)
                stats["disk_usage"]["total_size_mb"] += type_size / (1024 * 1024)
                
            except Exception as e:
                logger.error(f"Error calculating stats for {save_type}: {e}")
        
        stats["disk_usage"]["total_size_mb"] = round(stats["disk_usage"]["total_size_mb"], 2)
        
        return stats
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe filesystem usage."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        return filename[:50]
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate SHA256 hash of save data."""
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _verify_save_integrity(self, game_state: Dict[str, Any]) -> bool:
        """Verify save file integrity."""
        try:
            metadata = game_state.get("save_metadata", {})
            stored_hash = metadata.get("file_hash")
            
            if not stored_hash:
                return True  # No hash to verify
            
            # Calculate current hash (excluding metadata)
            temp_state = game_state.copy()
            temp_state.pop("save_metadata", None)
            current_hash = self._calculate_hash(temp_state)
            
            return stored_hash == current_hash
        except Exception:
            return False
    
    def _calculate_mythos_exposure(self, character: CthulhuCharacterData) -> str:
        """Calculate character's mythos exposure level."""
        mythos = character.mythos_knowledge
        
        if mythos >= 50:
            return "Deeply Exposed"
        elif mythos >= 25:
            return "Significantly Exposed"
        elif mythos >= 10:
            return "Moderately Exposed"
        elif mythos > 0:
            return "Lightly Exposed"
        else:
            return "Unexposed"
    
    def _determine_sanity_status(self, character: CthulhuCharacterData) -> str:
        """Determine character's sanity status."""
        current = character.sanity_current
        maximum = character.sanity_maximum
        
        if current <= 0:
            return "Insane"
        elif current <= maximum * 0.25:
            return "Critical"
        elif current <= maximum * 0.5:
            return "Unstable"
        elif current <= maximum * 0.75:
            return "Shaken"
        else:
            return "Stable"
    
    def _calculate_investigation_progress(self, session: CthulhuGameSession) -> float:
        """Calculate investigation progress percentage."""
        total_leads = len(session.active_leads) + len(session.completed_leads)
        if total_leads == 0:
            return 0.0
        
        return (len(session.completed_leads) / total_leads) * 100.0
    
    def _extract_save_info(self, save_path: Path) -> Optional[Dict[str, Any]]:
        """Extract basic information from save file."""
        try:
            stat = save_path.stat()
            
            save_info = {
                "filename": save_path.name,
                "path": str(save_path),
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified_time": datetime.fromtimestamp(stat.st_mtime),
                "save_type": save_path.parent.name
            }
            
            # Try to extract additional metadata if possible
            try:
                if save_path.suffix == '.gz':
                    with gzip.open(save_path, 'rt', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    with open(save_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                
                # Extract character info if available
                character_data = data.get("player_character", {})
                if character_data:
                    save_info.update({
                        "character_name": character_data.get("name", "Unknown"),
                        "character_occupation": character_data.get("occupation", "Unknown"),
                        "sanity_current": character_data.get("sanity_current", 0),
                        "mythos_knowledge": character_data.get("mythos_knowledge", 0)
                    })
                
                # Extract session info
                session_data = data.get("session_data", {})
                if session_data:
                    save_info.update({
                        "current_scenario": session_data.get("current_scenario", "Unknown"),
                        "current_location": session_data.get("current_location", "Unknown"),
                        "investigation_phase": session_data.get("investigation_phase", "Unknown")
                    })
                
                # Extract save metadata
                save_metadata = data.get("save_metadata", {})
                if save_metadata:
                    save_info["save_name"] = save_metadata.get("save_name", save_path.stem)
                
            except (json.JSONDecodeError, KeyError, Exception):
                # If we can't read the save, just use file info
                save_info["save_name"] = save_path.stem
            
            return save_info
            
        except Exception as e:
            logger.error(f"Error extracting save info from {save_path}: {e}")
            return None