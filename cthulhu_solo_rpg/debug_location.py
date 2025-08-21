#!/usr/bin/env python3
"""
위치 추정 디버그 테스트
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_location_estimation():
    """위치 추정 함수 테스트"""
    
    from src.core.gameplay_controller import GameplayController
    
    controller = GameplayController()
    
    test_scene_ids = [
        'scene_001_entrance',
        'scene_002_living_room', 
        'scene_003_kitchen',
        'scene_004_study',
        'scene_004_upstairs',
        'scene_005_basement'
    ]
    
    print("=== 위치 추정 테스트 ===\n")
    
    for scene_id in test_scene_ids:
        estimated_location = controller._estimate_current_location(scene_id)
        print(f"씬 ID: {scene_id}")
        print(f"추정 위치: {estimated_location}")
        print()

if __name__ == "__main__":
    test_location_estimation()