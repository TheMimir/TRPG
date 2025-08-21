#!/usr/bin/env python3
"""
Example usage of the Cthulhu TRPG Save System

This demonstrates how to use the comprehensive save/load system
for Cthulhu Horror TRPG with all specialized features.
"""

from datetime import datetime
from pathlib import Path

# Import the save system components
from src.data.save_manager import CthulhuSaveManager, CthulhuCharacterData, CthulhuGameSession
from src.utils.save_system import CthulhuSaveSystem, SaveSystemConfig


def create_example_character() -> CthulhuCharacterData:
    """Create an example character for demonstration."""
    return CthulhuCharacterData(
        # Basic Info
        name="Dr. Henry Armitage",
        age=65,
        occupation="University Librarian",
        residence="Arkham, Massachusetts",
        birthplace="Boston, Massachusetts",
        
        # Attributes
        strength=50,
        constitution=60,
        power=80,
        dexterity=45,
        appearance=55,
        size=60,
        intelligence=90,
        education=95,
        
        # Derived Attributes
        hit_points_current=12,
        hit_points_maximum=12,
        sanity_current=65,
        sanity_maximum=80,
        sanity_starting=80,
        magic_points_current=16,
        magic_points_maximum=16,
        
        # Skills
        skills={
            "library_use": {"base_value": 25, "current_value": 85, "occupation_points": 60, "personal_points": 0},
            "occult": {"base_value": 5, "current_value": 70, "occupation_points": 45, "personal_points": 20},
            "psychology": {"base_value": 10, "current_value": 60, "occupation_points": 30, "personal_points": 20},
            "spot_hidden": {"base_value": 25, "current_value": 55, "occupation_points": 20, "personal_points": 10}
        },
        
        # Mythos-specific data
        mythos_knowledge=15,
        mythos_tomes_read=["Necronomicon (partial)", "Cultes des Goules"],
        spells_known=["Contact Deity (Yog-Sothoth)", "Elder Sign"],
        phobias=["Agoraphobia (mild)"],
        
        # Equipment
        possessions=["Personal library", "Antique desk", "Reading glasses"],
        weapons=[{"name": ".32 Revolver", "damage": "1d8", "range": "15", "attacks": "1"}],
        cash_and_assets={"spending_level": 4, "cash": 250.50, "assets": 15000.00},
        
        # Investigation data
        clues_discovered=["Strange symbols in old texts", "References to Dunwich Horror"],
        locations_visited=["Miskatonic University Library", "Dunwich Village"],
        contacts_met=["Wilbur Whateley", "Old Zechariah Whateley"],
        
        # Development
        experience_points=25,
        skill_improvements={"occult": 5, "psychology": 10}
    )


def create_example_session() -> CthulhuGameSession:
    """Create an example game session."""
    return CthulhuGameSession(
        session_id="session_001",
        start_time=datetime.now(),
        current_scenario="The Dunwich Horror",
        current_location="Miskatonic University Library",
        current_turn=15,
        game_master_notes="Player investigating strange occurrences in Dunwich",
        
        # Investigation state
        investigation_phase="investigation",
        active_leads=["Investigate Whateley farmhouse", "Research Necronomicon passages"],
        completed_leads=["Interview local townspeople", "Examine diary fragments"],
        mythos_rating=3,
        
        # Environment
        time_of_day="Late Evening",
        weather="Overcast, unseasonably cold",
        season="Autumn 1928",
        
        # AI Agent memories (example structure)
        agent_memories={
            "story_agent": [
                {"type": "plot_point", "content": "Player discovered connection to Yog-Sothoth"},
                {"type": "npc_interaction", "content": "Tense conversation with Wilbur Whateley"}
            ],
            "environment_agent": [
                {"type": "atmosphere", "content": "Increasing sense of cosmic dread"},
                {"type": "weather", "content": "Unnatural cold despite season"}
            ]
        },
        
        story_context=[
            "Strange lights seen over Sentinel Hill",
            "Cattle found dead with unusual markings", 
            "Local children reporting nightmares"
        ],
        
        recent_events=[
            {"turn": 13, "description": "Successfully translated Latin passage", "type": "skill_success"},
            {"turn": 14, "description": "Sanity loss from disturbing revelation", "type": "sanity_loss", "amount": 5},
            {"turn": 15, "description": "Found reference to dimensional barrier", "type": "clue_discovery"}
        ],
        
        # Session stats
        sanity_lost_this_session=8,
        skill_checks_made=12,
        critical_successes=2,
        fumbles=1
    )


def demonstrate_basic_save_system():
    """Demonstrate the basic save manager functionality."""
    print("=== Cthulhu Save Manager Demo ===")
    
    # Initialize save manager
    save_manager = CthulhuSaveManager("./saves")
    
    # Create example data
    character = create_example_character()
    session = create_example_session()
    
    # Create game state
    ai_agent_states = {
        "gm_brain_memory": ["Player showing interest in mythos", "Tension building appropriately"],
        "story_continuity": ["Dunwich incident escalating", "Player character gaining dangerous knowledge"]
    }
    
    game_state = save_manager.create_game_state(character, session, ai_agent_states)
    
    # Save the game
    save_name = "Dunwich_Investigation_Session1"
    if save_manager.save_game(game_state, save_name):
        print(f"✓ Game saved: {save_name}")
    
    # Save character separately
    if save_manager.save_character_only(character, "Dr_Henry_Armitage"):
        print(f"✓ Character saved: {character.name}")
    
    # List all saves
    print("\nAvailable saves:")
    saves = save_manager.list_saves()
    for save_info in saves:
        save_name = save_info.get('save_name', save_info.get('filename', 'Unknown'))
        save_type = save_info.get('save_type', 'unknown')
        size_mb = save_info.get('size_mb', 0)
        print(f"  - {save_name} ({save_type}) - {size_mb} MB")
        if 'character_name' in save_info:
            char_name = save_info.get('character_name', 'Unknown')
            char_occ = save_info.get('character_occupation', 'Unknown')
            sanity = save_info.get('sanity_current', 0)
            mythos = save_info.get('mythos_knowledge', 0)
            print(f"    Character: {char_name} ({char_occ})")
            print(f"    Sanity: {sanity}, Mythos: {mythos}")
    
    # Load the game back
    loaded_game = save_manager.load_game("Dunwich_Investigation_Session1")
    if loaded_game:
        print(f"✓ Game loaded: Dunwich_Investigation_Session1")
        print(f"  Character: {loaded_game['player_character']['name']}")
        print(f"  Scenario: {loaded_game['session_data']['current_scenario']}")
        print(f"  Mythos Exposure: {loaded_game['mythos_exposure_level']}")
        print(f"  Sanity Status: {loaded_game['sanity_status']}")
    
    # Show statistics
    stats = save_manager.get_save_statistics()
    print(f"\nSave Statistics:")
    print(f"  Total saves: {stats['total_saves']}")
    print(f"  Disk usage: {stats['disk_usage']['total_size_mb']} MB")
    print(f"  Recent activity: {stats['recent_activity']['saves_this_week']} saves this week")


def demonstrate_advanced_save_system():
    """Demonstrate the advanced save system with all features."""
    print("\n=== Advanced Save System Demo ===")
    
    # Initialize advanced save system
    config = SaveSystemConfig()
    config.max_save_slots = 10
    config.compression_enabled = True
    config.auto_save_enabled = True
    config.auto_save_interval = 300  # 5 minutes
    
    save_system = CthulhuSaveSystem("./saves", config)
    
    # Create comprehensive game state
    character = create_example_character()
    session = create_example_session()
    
    # Convert dataclasses to dictionaries properly
    from dataclasses import asdict
    
    game_state = {
        "player_character": asdict(character),
        "session_data": session.to_dict(),
        "ai_agents": {
            "story_agent": {"memory": ["Plot advancement", "Character development"]},
            "gm_brain": {"context": ["Mythos investigation", "Rising tension"]},
            "environment_agent": {"atmosphere": "Growing cosmic dread"}
        },
        "current_turn": 15,
        "real_time_elapsed": 3600,  # 1 hour of play
        "recent_events": session.recent_events
    }
    
    # Save to specific slot
    slot_number = 1
    save_name = "Advanced Dunwich Investigation"
    
    try:
        if save_system.save_game(game_state, slot_number, save_name):
            print(f"✓ Advanced save successful: Slot {slot_number}")
        
        # Quick save
        if save_system.quick_save(game_state):
            print("✓ Quick save completed")
        
        # Show save metadata
        metadata = save_system.get_save_metadata(slot_number)
        if metadata:
            print(f"\nSave Metadata for Slot {slot_number}:")
            print(f"  Name: {metadata.save_name}")
            print(f"  Character: {metadata.character_name} (Level {metadata.character_level})")
            print(f"  Scenario: {metadata.current_scenario}")
            print(f"  Location: {metadata.current_location}")
            print(f"  Sanity Status: {metadata.sanity_status}")
            print(f"  Play Time: {metadata.play_time:.1f} hours")
            print(f"  Turn: {metadata.turn_number}")
            print(f"  File Size: {metadata.file_size} bytes")
            
            print(f"\n  Game Screenshot:")
            print(metadata.screenshot_text)
        
        # Load the game
        loaded_game = save_system.load_game(slot_number)
        if loaded_game:
            print(f"✓ Advanced load successful: {loaded_game['player_character']['name']}")
        
        # Show comprehensive statistics
        system_stats = save_system.get_save_statistics()
        print(f"\nSystem Statistics:")
        print(f"  Save System:")
        print(f"    Total slots: {system_stats['save_system']['total_slots']}")
        print(f"    Occupied slots: {system_stats['save_system']['occupied_slots']}")
        print(f"    Auto-save enabled: {system_stats['save_system']['auto_save_enabled']}")
        print(f"    Compression enabled: {system_stats['save_system']['compression_enabled']}")
        
    except Exception as e:
        print(f"Error in advanced save system: {e}")


def demonstrate_export_import():
    """Demonstrate character export/import functionality."""
    print("\n=== Export/Import Demo ===")
    
    save_manager = CthulhuSaveManager("./saves")
    character = create_example_character()
    
    # Export character
    export_path = Path("./Dr_Armitage_Export.json")
    if save_manager.export_character(character, export_path):
        print(f"✓ Character exported to: {export_path}")
    
    # Import character back
    imported_character = save_manager.import_character(export_path)
    if imported_character:
        print(f"✓ Character imported: {imported_character.name}")
        print(f"  Occupation: {imported_character.occupation}")
        print(f"  Mythos Knowledge: {imported_character.mythos_knowledge}")
        print(f"  Spells Known: {', '.join(imported_character.spells_known)}")
    
    # Clean up
    if export_path.exists():
        export_path.unlink()


if __name__ == "__main__":
    """Run all demonstrations."""
    try:
        demonstrate_basic_save_system()
        demonstrate_advanced_save_system()
        demonstrate_export_import()
        
        print("\n=== Save System Demo Complete ===")
        print("All systems working correctly!")
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()