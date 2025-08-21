"""
Miskatonic University Library Investigation
미스카토닉 대학교 도서관 조사

A complete Call of Cthulhu scenario for the Solo TRPG system.
This scenario involves investigating mysterious disappearances at the
famous Miskatonic University Library in Arkham, Massachusetts.

Scenario Details:
- Duration: 3-5 hours
- Difficulty: Beginner to Intermediate
- Themes: Academic horror, forbidden knowledge, cosmic entities
- Investigation focus: Library research, witness interviews, occult discovery
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from core.models import Investigation, TensionLevel, StoryContent, NarrativeContext


@dataclass
class ScenarioScene:
    """A scene within the scenario"""
    scene_id: str
    name: str
    description: str
    initial_tension: TensionLevel
    investigations: List[Investigation]
    npcs: List[Dict[str, Any]]
    special_rules: Dict[str, Any] = field(default_factory=dict)
    connected_scenes: List[str] = field(default_factory=list)
    completion_conditions: List[str] = field(default_factory=list)


class MiskatonicLibraryScenario:
    """
    Complete scenario: Miskatonic University Library Investigation
    
    Background:
    Several students and faculty members have gone missing from the
    Miskatonic University Library over the past month. The last person
    to see them alive was the night librarian, who reported strange
    sounds and flickering lights in the restricted section.
    
    The investigators are called in to solve the mystery before more
    people disappear.
    """
    
    def __init__(self):
        """Initialize the scenario"""
        self.scenario_id = "miskatonic_library_investigation"
        self.title = "미스카토닉 대학교 도서관의 비밀"
        self.subtitle = "The Secret of Miskatonic University Library"
        
        # Scenario metadata
        self.duration_hours = 4
        self.recommended_players = 1
        self.difficulty = "beginner_intermediate"
        self.themes = ["academic_horror", "forbidden_knowledge", "cosmic_entities"]
        
        # Scenario state
        self.current_scene = "university_entrance"
        self.discovered_clues: List[str] = []
        self.story_flags: Dict[str, Any] = {}
        self.npcs_met: List[str] = []
        
        # Initialize scenes
        self.scenes = self._create_scenes()
        
        # Initialize NPCs
        self.npcs = self._create_npcs()
        
        # Initialize clues and evidence
        self.clues = self._create_clues()
        
        # Scenario progression tracking
        self.act = 1
        self.key_discoveries = 0
        self.final_revelation_available = False
    
    def _create_scenes(self) -> Dict[str, ScenarioScene]:
        """Create all scenes for the scenario"""
        scenes = {}
        
        # Scene 1: University Entrance
        scenes["university_entrance"] = ScenarioScene(
            scene_id="university_entrance",
            name="미스카토닉 대학교 정문",
            description="""
            미스카토닉 대학교의 고풍스러운 정문 앞에 서 있습니다. 19세기 고딕 양식의 
            건물들이 늦은 오후 햇살에 장엄한 그림자를 드리우고 있습니다. 캠퍼스는 
            평소보다 조용해 보이며, 몇 명의 학생들이 서둘러 지나가고 있습니다.
            
            정문 옆 게시판에는 실종된 학생들에 대한 포스터가 붙어있고, 경비원이
            걱정스러운 표정으로 주변을 살피고 있습니다.
            """,
            initial_tension=TensionLevel.CALM,
            investigations=[
                Investigation(
                    description="게시판의 실종자 포스터를 자세히 살펴본다",
                    difficulty=3,
                    keywords=["게시판", "포스터", "실종자"],
                    rewards=["실종자들의 이름과 사진", "실종 시기 패턴 발견"]
                ),
                Investigation(
                    description="경비원과 대화를 시도한다",
                    difficulty=4,
                    keywords=["경비원", "대화", "정보"],
                    rewards=["최근 이상한 일들에 대한 증언", "도서관 접근 정보"]
                ),
                Investigation(
                    description="캠퍼스 분위기와 학생들의 행동을 관찰한다",
                    difficulty=5,
                    keywords=["관찰", "분위기", "학생"],
                    rewards=["학생들의 불안감 감지", "도서관 방향의 단서"]
                )
            ],
            npcs=["security_guard", "nervous_student"],
            connected_scenes=["library_entrance", "campus_quad", "administration_building"]
        )
        
        # Scene 2: Library Entrance
        scenes["library_entrance"] = ScenarioScene(
            scene_id="library_entrance",
            name="도서관 입구",
            description="""
            미스카토닉 대학교 도서관의 웅장한 입구에 도착했습니다. 거대한 참나무 문과
            고딕 양식의 아치가 인상적입니다. 도서관은 평소보다 한적해 보이며, 
            입구 근처에서 희미한 전등 불빛이 깜박이고 있습니다.
            
            문 앞에는 '제한적 운영 중'이라는 팻말이 붙어있고, 접수 데스크에서
            나이 든 사서가 책을 정리하고 있습니다.
            """,
            initial_tension=TensionLevel.UNEASY,
            investigations=[
                Investigation(
                    description="도서관 입구의 팻말과 공지사항을 확인한다",
                    difficulty=3,
                    keywords=["팻말", "공지사항", "운영시간"],
                    rewards=["운영 제한 사유", "특별 규정 발견"]
                ),
                Investigation(
                    description="접수 데스크의 사서와 대화한다",
                    difficulty=4,
                    keywords=["사서", "대화", "도서관"],
                    rewards=["실종 사건에 대한 정보", "제한 구역 정보"]
                ),
                Investigation(
                    description="도서관 내부 구조를 파악한다",
                    difficulty=5,
                    keywords=["구조", "층별", "지도"],
                    rewards=["도서관 배치도", "제한 구역 위치"]
                )
            ],
            npcs=["head_librarian", "worried_professor"],
            connected_scenes=["main_reading_room", "restricted_section", "university_entrance"]
        )
        
        # Scene 3: Main Reading Room
        scenes["main_reading_room"] = ScenarioScene(
            scene_id="main_reading_room",
            name="메인 열람실",
            description="""
            도서관의 메인 열람실에 들어섰습니다. 높은 천장과 거대한 창문들이 있는
            웅장한 공간이지만, 오늘은 대부분의 책상이 비어있습니다. 몇 명의 학생들이
            구석진 자리에서 조용히 공부하고 있으며, 그들의 표정은 긴장해 보입니다.
            
            열람실 한쪽 벽면에는 금지된 서적 목록이 게시되어 있고, 
            제한 구역으로 가는 문이 굳게 잠겨 있습니다.
            """,
            initial_tension=TensionLevel.UNEASY,
            investigations=[
                Investigation(
                    description="학생들과 대화하여 최근 상황을 알아본다",
                    difficulty=4,
                    keywords=["학생", "대화", "상황"],
                    rewards=["이상한 소음 목격담", "실종자 목격 정보"]
                ),
                Investigation(
                    description="금지된 서적 목록을 자세히 살펴본다",
                    difficulty=5,
                    keywords=["금지", "서적", "목록"],
                    rewards=["네크로노미콘 관련 기록", "위험한 책들의 제목"]
                ),
                Investigation(
                    description="제한 구역 문 주변을 조사한다",
                    difficulty=6,
                    keywords=["제한구역", "문", "자물쇠"],
                    rewards=["문 주변의 이상한 긁힌 자국", "비밀 열쇠 위치 단서"]
                ),
                Investigation(
                    description="열람실의 분위기와 에너지를 감지한다",
                    difficulty=7,
                    keywords=["분위기", "에너지", "초자연"],
                    rewards=["불안한 기운 감지", "제한 구역에서 오는 이상한 느낌"]
                )
            ],
            npcs=["anxious_student", "graduate_researcher"],
            connected_scenes=["library_entrance", "restricted_section", "basement_archives"],
            special_rules={
                "sanity_check_required": True,
                "sanity_loss": "1d2",
                "reason": "도서관의 불안한 분위기"
            }
        )
        
        # Scene 4: Restricted Section
        scenes["restricted_section"] = ScenarioScene(
            scene_id="restricted_section",
            name="제한 구역",
            description="""
            드디어 도서관의 제한 구역에 들어왔습니다. 이곳은 메인 열람실과는 완전히
            다른 분위기입니다. 공기가 무겁고 먼지 냄새와 함께 알 수 없는 향기가
            섞여 있습니다. 높은 책장들 사이로 희미한 전등이 으스스한 그림자를 만들어냅니다.
            
            한쪽 구석에는 특별히 보안이 강화된 유리 진열장이 있고, 그 안에는
            고대 양피지로 만든 책들이 보관되어 있습니다. 바닥에는 최근 누군가가
            지나간 듯한 발자국이 희미하게 남아있습니다.
            """,
            initial_tension=TensionLevel.TENSE,
            investigations=[
                Investigation(
                    description="유리 진열장의 고대 서적들을 조사한다",
                    difficulty=7,
                    keywords=["진열장", "고대서적", "양피지"],
                    rewards=["네크로노미콘 원본 발견", "라틴어 주문서 발견"],
                    requirements={"occult": 40}
                ),
                Investigation(
                    description="바닥의 발자국을 추적한다",
                    difficulty=6,
                    keywords=["발자국", "추적", "흔적"],
                    rewards=["지하로 향하는 발자국", "여러 명의 발자국 확인"]
                ),
                Investigation(
                    description="책장 사이의 숨겨진 통로를 찾는다",
                    difficulty=8,
                    keywords=["책장", "숨겨진통로", "비밀"],
                    rewards=["지하실로 향하는 비밀 계단 발견"]
                ),
                Investigation(
                    description="이상한 향기의 근원을 찾는다",
                    difficulty=7,
                    keywords=["향기", "냄새", "근원"],
                    rewards=["향 제단의 흔적", "의식의 증거"]
                )
            ],
            npcs=["night_librarian"],
            connected_scenes=["main_reading_room", "secret_basement", "hidden_chamber"],
            special_rules={
                "sanity_check_required": True,
                "sanity_loss": "1d4",
                "reason": "금지된 지식에 노출"
            },
            completion_conditions=["find_secret_passage", "discover_ritual_evidence"]
        )
        
        # Scene 5: Secret Basement
        scenes["secret_basement"] = ScenarioScene(
            scene_id="secret_basement",
            name="비밀 지하실",
            description="""
            제한 구역에서 발견한 비밀 계단을 따라 내려온 지하실입니다. 이곳은
            공식적으로 존재하지 않는 공간으로 보입니다. 벽면에는 이상한 기호들이
            새겨져 있고, 중앙에는 원형의 제단이 설치되어 있습니다.
            
            제단 주위에는 촛불의 흔적과 알 수 없는 붉은 얼룩들이 보입니다.
            한쪽 구석에는 최근까지 누군가가 사용했던 것으로 보이는 임시 거주지가
            마련되어 있습니다. 공기 중에는 강한 마법적 에너지가 감돌고 있습니다.
            """,
            initial_tension=TensionLevel.TERRIFYING,
            investigations=[
                Investigation(
                    description="벽면의 이상한 기호들을 해독한다",
                    difficulty=9,
                    keywords=["기호", "해독", "마법"],
                    rewards=["고대 소환 의식의 내용", "크툴루 관련 기록"],
                    requirements={"occult": 60}
                ),
                Investigation(
                    description="제단과 의식의 흔적을 조사한다",
                    difficulty=8,
                    keywords=["제단", "의식", "마법진"],
                    rewards=["인간 제물 의식의 증거", "차원 문 소환 시도"]
                ),
                Investigation(
                    description="임시 거주지의 소지품들을 확인한다",
                    difficulty=6,
                    keywords=["거주지", "소지품", "흔적"],
                    rewards=["실종자들의 개인 물품", "의식 주도자의 정체"]
                ),
                Investigation(
                    description="지하실의 다른 출입구를 찾는다",
                    difficulty=7,
                    keywords=["출입구", "터널", "지하"],
                    rewards=["대학 지하 터널 시스템 발견", "탈출로 발견"]
                )
            ],
            npcs=["cult_leader", "possessed_student"],
            connected_scenes=["restricted_section", "underground_tunnels", "ritual_chamber"],
            special_rules={
                "sanity_check_required": True,
                "sanity_loss": "1d6",
                "reason": "사악한 의식의 현장 목격",
                "combat_possible": True
            }
        )
        
        # Scene 6: Final Confrontation
        scenes["ritual_chamber"] = ScenarioScene(
            scene_id="ritual_chamber",
            name="의식의 방",
            description="""
            지하실 깊숙한 곳에 위치한 거대한 의식의 방에 도착했습니다. 이곳은 
            완전히 다른 차원과 연결된 것처럼 보입니다. 천장은 보이지 않을 만큼 높고,
            벽면에는 살아 움직이는 듯한 기하학적 무늬들이 끊임없이 변화하고 있습니다.
            
            방 중앙의 거대한 제단에서는 실종된 사람들이 최면에 걸린 채로 의식을
            진행하고 있습니다. 제단 위에는 현실과 다른 차원을 연결하는 포털이
            열려있고, 그 너머로 크툴루의 촉수가 서서히 모습을 드러내고 있습니다.
            """,
            initial_tension=TensionLevel.COSMIC_HORROR,
            investigations=[
                Investigation(
                    description="의식을 중단시킬 방법을 찾는다",
                    difficulty=10,
                    keywords=["의식", "중단", "방해"],
                    rewards=["의식 중단 방법", "포털 폐쇄 방법"],
                    one_time=True
                ),
                Investigation(
                    description="실종자들을 구출한다",
                    difficulty=9,
                    keywords=["구출", "실종자", "최면해제"],
                    rewards=["실종자 구출 성공", "추가 증인 확보"],
                    one_time=True
                ),
                Investigation(
                    description="크툴루의 영향력에 저항한다",
                    difficulty=12,
                    keywords=["저항", "크툴루", "정신력"],
                    rewards=["cosmic_horror_survival", "ultimate_knowledge"],
                    requirements={"sanity": 50}
                )
            ],
            npcs=["cthulhu_manifestation", "cult_high_priest"],
            connected_scenes=["secret_basement"],
            special_rules={
                "sanity_check_required": True,
                "sanity_loss": "2d10",
                "reason": "크툴루 직접 목격",
                "final_boss": True,
                "multiple_outcomes": True
            },
            completion_conditions=["defeat_cult", "close_portal", "escape_alive"]
        )
        
        return scenes
    
    def _create_npcs(self) -> Dict[str, Dict[str, Any]]:
        """Create NPCs for the scenario"""
        return {
            "security_guard": {
                "name": "윌리엄 톰슨",
                "role": "대학 경비원",
                "description": "30년간 미스카토닉 대학교에서 근무한 베테랑 경비원",
                "personality": "신중하고 관찰력이 뛰어남",
                "information": [
                    "최근 밤마다 도서관에서 이상한 불빛이 보인다",
                    "실종자들은 모두 밤늦게 도서관을 방문했다",
                    "제한 구역 열쇠가 며칠 전부터 없어졌다"
                ],
                "skills": {"spot_hidden": 70, "listen": 65}
            },
            
            "head_librarian": {
                "name": "헨리 아미티지 박사",
                "role": "수석 사서",
                "description": "미스카토닉 대학교의 수석 사서이자 오컬트 전문가",
                "personality": "학자적이고 신중하며 약간 신경질적",
                "information": [
                    "제한 구역에는 위험한 서적들이 보관되어 있다",
                    "네크로노미콘 원본이 최근 누군가에 의해 열람되었다",
                    "대학 지하에는 공식적으로 알려지지 않은 공간이 있다"
                ],
                "skills": {"library_use": 90, "occult": 75, "psychology": 60}
            },
            
            "anxious_student": {
                "name": "제니퍼 브라운",
                "role": "대학원생",
                "description": "인류학과 대학원생으로 최근 매우 불안해하고 있다",
                "personality": "똑똑하지만 겁이 많고 예민함",
                "information": [
                    "실종된 친구가 이상한 꿈에 대해 말했었다",
                    "밤마다 지하에서 이상한 소리가 들린다",
                    "누군가가 학생들을 지하로 이끌고 있다는 소문"
                ],
                "skills": {"anthropology": 45, "listen": 50}
            },
            
            "night_librarian": {
                "name": "에드워드 더비",
                "role": "야간 사서",
                "description": "야간 근무를 담당하는 사서, 최근 이상한 행동을 보임",
                "personality": "과거에는 친절했지만 최근 무언가에 홀린 듯함",
                "information": [
                    "제한 구역에서 누군가와 비밀 모임을 하고 있다",
                    "고대 언어로 된 이상한 주문을 중얼거린다",
                    "실종 사건과 연관되어 있을 가능성이 높다"
                ],
                "skills": {"library_use": 80, "occult": 60},
                "corruption_level": 0.7
            },
            
            "cult_leader": {
                "name": "윌버 왓틀리",
                "role": "컬트 지도자",
                "description": "크툴루 컬트의 지도자로 대학에 잠입한 인물",
                "personality": "카리스마틱하지만 광신적이고 위험함",
                "information": [
                    "크툴루를 현세에 소환하려고 한다",
                    "학생들을 세뇌하여 의식에 참여시킨다",
                    "네크로노미콘의 금지된 지식을 사용한다"
                ],
                "skills": {"occult": 95, "persuade": 85, "intimidate": 70},
                "sanity": 0,
                "boss_level": True
            }
        }
    
    def _create_clues(self) -> Dict[str, Dict[str, Any]]:
        """Create clues and evidence for the scenario"""
        return {
            "missing_persons_poster": {
                "name": "실종자 포스터",
                "description": "지난 한 달간 실종된 5명의 학생과 교직원 정보",
                "discovery_method": "investigation",
                "reveals": ["실종 패턴", "공통점 - 모두 도서관 이용자"],
                "importance": 6
            },
            
            "restricted_key": {
                "name": "제한 구역 열쇠",
                "description": "도서관 제한 구역으로 가는 특별한 열쇠",
                "discovery_method": "npc_interaction",
                "reveals": ["제한 구역 접근", "금지된 서적 열람 가능"],
                "importance": 8
            },
            
            "necronomicon_latin": {
                "name": "네크로노미콘 (라틴어판)",
                "description": "알 하자드의 광기어린 아랍인이 쓴 저주받은 책",
                "discovery_method": "restricted_section",
                "reveals": ["차원 소환 주문", "크툴루에 대한 지식"],
                "importance": 10,
                "sanity_loss": "1d8"
            },
            
            "ritual_circle": {
                "name": "의식용 마법진",
                "description": "지하실에 그려진 복잡한 소환 마법진",
                "discovery_method": "secret_basement",
                "reveals": ["의식의 목적", "완성 단계"],
                "importance": 9
            },
            
            "personal_belongings": {
                "name": "실종자 개인 물품",
                "description": "실종된 학생들의 가방, 신발, 안경 등",
                "discovery_method": "basement_investigation",
                "reveals": ["실종자들의 안전 확인", "강제 연행 증거"],
                "importance": 7
            },
            
            "cult_diary": {
                "name": "컬트 지도자의 일기",
                "description": "윌버 왓틀리가 쓴 의식 계획과 진행 상황",
                "discovery_method": "final_confrontation",
                "reveals": ["최종 의식 일정", "크툴루 소환 방법"],
                "importance": 10
            }
        }
    
    def get_current_scene(self) -> ScenarioScene:
        """Get the current scene"""
        return self.scenes.get(self.current_scene)
    
    def advance_to_scene(self, scene_id: str) -> bool:
        """Advance to a new scene"""
        if scene_id in self.scenes:
            self.current_scene = scene_id
            return True
        return False
    
    def discover_clue(self, clue_id: str):
        """Mark a clue as discovered"""
        if clue_id not in self.discovered_clues:
            self.discovered_clues.append(clue_id)
            self.key_discoveries += 1
            
            # Check for final revelation unlock
            if self.key_discoveries >= 4:
                self.final_revelation_available = True
    
    def set_story_flag(self, flag: str, value: Any):
        """Set a story flag"""
        self.story_flags[flag] = value
    
    def get_story_flag(self, flag: str) -> Any:
        """Get a story flag value"""
        return self.story_flags.get(flag)
    
    def check_completion_conditions(self) -> Dict[str, Any]:
        """Check scenario completion conditions"""
        current_scene = self.get_current_scene()
        if not current_scene:
            return {"complete": False}
        
        # Check scene-specific completion
        scene_complete = True
        for condition in current_scene.completion_conditions:
            if not self.get_story_flag(condition):
                scene_complete = False
                break
        
        # Overall scenario completion
        scenario_complete = (
            self.current_scene == "ritual_chamber" and
            len(self.discovered_clues) >= 5 and
            (self.get_story_flag("ritual_stopped") or self.get_story_flag("escaped_alive"))
        )
        
        return {
            "scene_complete": scene_complete,
            "scenario_complete": scenario_complete,
            "act": self.act,
            "key_discoveries": self.key_discoveries,
            "final_available": self.final_revelation_available
        }
    
    def get_scenario_summary(self) -> Dict[str, Any]:
        """Get current scenario summary"""
        return {
            "scenario_id": self.scenario_id,
            "title": self.title,
            "current_scene": self.current_scene,
            "act": self.act,
            "discovered_clues": len(self.discovered_clues),
            "story_flags": dict(self.story_flags),
            "npcs_met": self.npcs_met.copy(),
            "completion": self.check_completion_conditions()
        }
    
    def get_scene_initial_content(self, scene_id: Optional[str] = None) -> StoryContent:
        """Get initial story content for a scene"""
        if scene_id:
            scene = self.scenes.get(scene_id)
        else:
            scene = self.get_current_scene()
        
        if not scene:
            return StoryContent(
                text="알 수 없는 장소에 도착했습니다.",
                content_id=f"error_{int(time.time())}",
                scene_id="unknown",
                tension_level=TensionLevel.CALM,
                investigation_opportunities=[],
                story_threads={}
            )
        
        # Generate investigation opportunities from scene
        investigations = [inv.description for inv in scene.investigations[:5]]
        
        return StoryContent(
            text=scene.description.strip(),
            content_id=f"scene_intro_{scene.scene_id}_{int(time.time())}",
            scene_id=scene.scene_id,
            tension_level=scene.initial_tension,
            investigation_opportunities=investigations,
            story_threads={"current_location": scene.name},
            metadata={
                "scene_name": scene.name,
                "scenario": self.scenario_id,
                "act": self.act
            }
        )


# Factory function to create the scenario
def create_miskatonic_library_scenario() -> MiskatonicLibraryScenario:
    """Create and return the Miskatonic Library scenario"""
    return MiskatonicLibraryScenario()