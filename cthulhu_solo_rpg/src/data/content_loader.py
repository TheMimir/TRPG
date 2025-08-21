"""
Content Loader for game data

Loads scenarios, NPCs, locations, and other game content from files.
Provides comprehensive access to all Cthulhu TRPG data.
"""

import json
import os
import random
import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class ContentLoader:
    """Loads and manages game content from data files."""
    
    def __init__(self, data_directory: str):
        self.data_directory = data_directory
        
        # Core content categories
        self.scenarios = {}
        self.entities = {}
        self.locations = {}
        self.items = {}
        self.events = {}
        self.atmosphere = {}
        
        # Cache for loaded content
        self._cache = {}
        self._loaded_files = set()
        
        # Initialize with current directory if not specified
        if not os.path.exists(data_directory):
            current_dir = os.path.dirname(__file__)
            self.data_directory = current_dir
            logger.warning(f"Data directory not found, using: {self.data_directory}")
    
    def load_all_content(self) -> bool:
        """Load all game content from data files."""
        try:
            self.load_scenarios()
            self.load_entities()
            self.load_locations()
            self.load_items()
            self.load_events()
            self.load_atmosphere()
            logger.info("All content loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load content: {e}")
            return False
    
    def load_scenarios(self) -> bool:
        """Load scenario data."""
        scenario_files = [
            "scenarios/beginner_scenarios.json",
            "scenarios/classic_scenarios.json", 
            "scenarios/investigation_scenarios.json",
            "scenarios/scenario_templates.json"
        ]
        
        for file_path in scenario_files:
            full_path = os.path.join(self.data_directory, file_path)
            data = self._load_json_file(full_path)
            if data:
                # Extract filename without extension as key
                key = os.path.splitext(os.path.basename(file_path))[0]
                self.scenarios[key] = data
        
        return len(self.scenarios) > 0
    
    def load_entities(self) -> bool:
        """Load entity data (creatures, cultists, gods)."""
        entity_files = [
            "entities/great_old_ones.json",
            "entities/outer_gods.json",
            "entities/mythos_creatures.json", 
            "entities/cultists.json"
        ]
        
        for file_path in entity_files:
            full_path = os.path.join(self.data_directory, file_path)
            data = self._load_json_file(full_path)
            if data:
                key = os.path.splitext(os.path.basename(file_path))[0]
                self.entities[key] = data
        
        return len(self.entities) > 0
    
    def load_locations(self) -> bool:
        """Load location data."""
        location_files = [
            "locations/arkham_locations.json",
            "locations/dunwich_locations.json",
            "locations/miskatonic_university.json",
            "locations/haunted_locations.json"
        ]
        
        for file_path in location_files:
            full_path = os.path.join(self.data_directory, file_path)
            data = self._load_json_file(full_path)
            if data:
                key = os.path.splitext(os.path.basename(file_path))[0]
                self.locations[key] = data
        
        return len(self.locations) > 0
    
    def load_items(self) -> bool:
        """Load item and equipment data."""
        item_files = [
            "items/investigation_tools.json",
            "items/occult_books.json",
            "items/artifacts.json",
            "items/weapons.json"
        ]
        
        for file_path in item_files:
            full_path = os.path.join(self.data_directory, file_path)
            data = self._load_json_file(full_path)
            if data:
                key = os.path.splitext(os.path.basename(file_path))[0]
                self.items[key] = data
        
        return len(self.items) > 0
    
    def load_events(self) -> bool:
        """Load event data."""
        event_files = [
            "events/random_encounters.json"
            # Add more event files as they are created
        ]
        
        for file_path in event_files:
            full_path = os.path.join(self.data_directory, file_path)
            data = self._load_json_file(full_path)
            if data:
                key = os.path.splitext(os.path.basename(file_path))[0]
                self.events[key] = data
        
        return len(self.events) > 0
    
    def load_atmosphere(self) -> bool:
        """Load atmosphere and descriptive data."""
        atmosphere_files = [
            "atmosphere/horror_descriptors.json"
            # Add more atmosphere files as they are created
        ]
        
        for file_path in atmosphere_files:
            full_path = os.path.join(self.data_directory, file_path)
            data = self._load_json_file(full_path)
            if data:
                key = os.path.splitext(os.path.basename(file_path))[0]
                self.atmosphere[key] = data
        
        return len(self.atmosphere) > 0
    
    def _load_json_file(self, file_path: str) -> Optional[Dict]:
        """Load and parse a JSON file."""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return None
                
            if file_path in self._loaded_files:
                logger.debug(f"File already loaded: {file_path}")
                return self._cache.get(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._cache[file_path] = data
                self._loaded_files.add(file_path)
                logger.debug(f"Loaded file: {file_path}")
                return data
                
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None
    
    def get_random_content(self, content_type: str, subcategory: Optional[str] = None) -> Optional[Dict]:
        """Get random content of specified type."""
        try:
            # Map content types to data structures
            content_map = {
                'scenario': self.scenarios,
                'entity': self.entities,
                'location': self.locations,
                'item': self.items,
                'event': self.events,
                'atmosphere': self.atmosphere
            }
            
            if content_type not in content_map:
                logger.warning(f"Unknown content type: {content_type}")
                return None
            
            data_source = content_map[content_type]
            
            if subcategory:
                if subcategory in data_source:
                    return self._get_random_from_collection(data_source[subcategory])
                else:
                    logger.warning(f"Subcategory {subcategory} not found in {content_type}")
                    return None
            else:
                # Return random item from any subcategory
                all_items = []
                for category_data in data_source.values():
                    if isinstance(category_data, dict):
                        items = self._extract_items_from_data(category_data)
                        all_items.extend(items)
                
                return random.choice(all_items) if all_items else None
                
        except Exception as e:
            logger.error(f"Error getting random content: {e}")
            return None
    
    def _get_random_from_collection(self, data: Dict) -> Optional[Dict]:
        """Get random item from a data collection."""
        try:
            items = self._extract_items_from_data(data)
            return random.choice(items) if items else None
        except Exception as e:
            logger.error(f"Error getting random from collection: {e}")
            return None
    
    def _extract_items_from_data(self, data: Dict) -> List[Dict]:
        """Extract individual items from structured data."""
        items = []
        
        # Look for common collection keys
        collection_keys = ['scenarios', 'entities', 'locations', 'items', 'events', 
                          'encounters', 'creatures', 'artifacts', 'tools']
        
        for key in collection_keys:
            if key in data and isinstance(data[key], list):
                items.extend(data[key])
        
        # If no standard collections found, return the data itself if it looks like an item
        if not items and 'id' in data or 'name' in data:
            items.append(data)
        
        return items
    
    def get_content_by_id(self, content_type: str, item_id: str) -> Optional[Dict]:
        """Get specific content by ID."""
        try:
            content_map = {
                'scenario': self.scenarios,
                'entity': self.entities, 
                'location': self.locations,
                'item': self.items,
                'event': self.events,
                'atmosphere': self.atmosphere
            }
            
            if content_type not in content_map:
                return None
            
            # Search through all subcategories for the item
            for category_data in content_map[content_type].values():
                items = self._extract_items_from_data(category_data)
                for item in items:
                    if isinstance(item, dict) and item.get('id') == item_id:
                        return item
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting content by ID {item_id}: {e}")
            return None
    
    def get_content_by_difficulty(self, content_type: str, difficulty: int) -> List[Dict]:
        """Get content filtered by difficulty level."""
        try:
            filtered_items = []
            
            content_map = {
                'scenario': self.scenarios,
                'entity': self.entities,
                'location': self.locations
            }
            
            if content_type not in content_map:
                return filtered_items
            
            for category_data in content_map[content_type].values():
                items = self._extract_items_from_data(category_data)
                for item in items:
                    if isinstance(item, dict):
                        item_difficulty = item.get('difficulty', 0)
                        if item_difficulty == difficulty:
                            filtered_items.append(item)
            
            return filtered_items
            
        except Exception as e:
            logger.error(f"Error filtering by difficulty: {e}")
            return []
    
    def search_content(self, query: str, content_type: Optional[str] = None) -> List[Dict]:
        """Search for content containing the query string."""
        try:
            results = []
            query_lower = query.lower()
            
            search_categories = []
            if content_type:
                content_map = {
                    'scenario': self.scenarios,
                    'entity': self.entities,
                    'location': self.locations,
                    'item': self.items,
                    'event': self.events,
                    'atmosphere': self.atmosphere
                }
                if content_type in content_map:
                    search_categories = [content_map[content_type]]
            else:
                search_categories = [self.scenarios, self.entities, self.locations, 
                                   self.items, self.events, self.atmosphere]
            
            for category in search_categories:
                for subcategory_data in category.values():
                    items = self._extract_items_from_data(subcategory_data)
                    for item in items:
                        if isinstance(item, dict):
                            # Search in name, title, description fields
                            searchable_text = ""
                            for field in ['name', 'title', 'description', 'name_en', 'title_en']:
                                if field in item:
                                    searchable_text += str(item[field]).lower() + " "
                            
                            if query_lower in searchable_text:
                                results.append(item)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return []
    
    def get_random_horror_descriptor(self, category: Optional[str] = None, intensity: Optional[int] = None) -> Optional[str]:
        """Get random horror descriptor for atmosphere building."""
        try:
            if 'horror_descriptors' not in self.atmosphere:
                return None
            
            descriptors_data = self.atmosphere['horror_descriptors']
            
            if category and category in descriptors_data:
                # Get from specific category
                category_data = descriptors_data[category]
                if isinstance(category_data, dict):
                    all_descriptors = []
                    for subcategory in category_data.values():
                        if isinstance(subcategory, list):
                            all_descriptors.extend(subcategory)
                    return random.choice(all_descriptors) if all_descriptors else None
                elif isinstance(category_data, list):
                    return random.choice(category_data)
            
            # Get from intensity level if specified
            if intensity and 'intensity_levels' in descriptors_data:
                for level in descriptors_data['intensity_levels']:
                    if level.get('level') == intensity:
                        descriptors = level.get('descriptors', [])
                        return random.choice(descriptors) if descriptors else None
            
            # Get random from all visual elements as default
            if 'visual_elements' in descriptors_data:
                all_visual = []
                for visual_category in descriptors_data['visual_elements'].values():
                    if isinstance(visual_category, list):
                        all_visual.extend(visual_category)
                return random.choice(all_visual) if all_visual else None
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting horror descriptor: {e}")
            return None
    
    def reload_content(self) -> bool:
        """Reload all content from files (useful for development)."""
        try:
            self._cache.clear()
            self._loaded_files.clear()
            
            self.scenarios.clear()
            self.entities.clear()
            self.locations.clear()
            self.items.clear()
            self.events.clear()
            self.atmosphere.clear()
            
            return self.load_all_content()
            
        except Exception as e:
            logger.error(f"Error reloading content: {e}")
            return False
    
    def get_content_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics about loaded content."""
        stats = {}
        
        categories = {
            'scenarios': self.scenarios,
            'entities': self.entities,
            'locations': self.locations,
            'items': self.items,
            'events': self.events,
            'atmosphere': self.atmosphere
        }
        
        for category_name, category_data in categories.items():
            stats[category_name] = {}
            total_items = 0
            
            for subcategory_name, subcategory_data in category_data.items():
                items = self._extract_items_from_data(subcategory_data)
                item_count = len(items)
                stats[category_name][subcategory_name] = item_count
                total_items += item_count
            
            stats[category_name]['total'] = total_items
        
        return stats