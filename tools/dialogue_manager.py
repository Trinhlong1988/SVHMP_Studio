"""tools/dialogue_manager.py — D2 (TASK_G3_DIALOGUE.md), phuong an A DA DUOC BOSS CHOT
(governance/proposals/g3_manager_decision_proposal.yaml, mr_long_decision: APPROVED_A, 5/7).

Mong, CHI orchestrate context cho dialogue_generator.py — KHONG doc lai roster YAML lan 2
(dung tools/character_manager.CharacterRegistry lam nguon that duy nhat, dung pattern
roster_validator.py/dialog_voice_validator.py da dung cho migrate_roster_v2.HOME).

API duy nhat theo dung TASK: get_dialogue_context(character_id, ep_n) -> {
    voice_profile: dict | None,
    known_facts_upto_ep: dict,      # story_memory that cua nhan vat (KHONG bia neu rong)
    recent_lines: list[str],        # quote THAT da render cho nhan vat nay (tai dung
                                     # extract_quotes()/get_passenger_info() cua
                                     # audit_dialogue_hierarchy.py, KHONG viet lai regex)
}

KHONG import production/publisher (PHAN BIEN #9). KHONG tu tinh ratio thoai/narration
(viec cua decision_engine/G6) - manager nay chi doc context, khong quyet dinh gi ve noi dung.
"""
from __future__ import annotations
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from character_manager import CharacterRegistry, CharacterProfile  # noqa: E402
from audit_dialogue_hierarchy import extract_quotes, get_passenger_info  # noqa: E402

SVHMP = Path(__file__).parent.parent


class DialogueManager:
    """Thin wrapper quanh CharacterRegistry - KHONG so huu du lieu rieng."""

    def __init__(self, registry: CharacterRegistry = None):
        self.registry = registry or CharacterRegistry()

    def get_dialogue_context(self, character_id: str, ep_n: int = None) -> dict:
        c = self.registry.get(character_id)
        if c is None:
            return {
                'voice_profile': None,
                'known_facts_upto_ep': {},
                'recent_lines': [],
                'error': 'CHARACTER_NOT_FOUND',
            }
        voice_profile = {k: v for k, v in asdict(c.voice).items()}
        return {
            'voice_profile': voice_profile,
            'known_facts_upto_ep': dict(c.story_memory or {}),
            'recent_lines': self._recent_lines(c, ep_n),
            'kind': c.kind,
            'char_name': c.char_name,
        }

    def _recent_lines(self, c: CharacterProfile, ep_n: int = None) -> list:
        """Quote THAT da render cho nhan vat nay trong tap noi bat (assigned_ep hoac ep_n
        truyen vao). CHI lay khi ten passenger trich tu episode.md (get_passenger_info,
        tai dung) KHOP dung char_name - tranh gan nham quote cua passenger khac trong cung
        tap (moi tap = 1 passenger tam diem theo dung format du lieu hien co)."""
        target_ep = ep_n if ep_n is not None else c.assigned_ep
        if not target_ep:
            return []
        ep_path = SVHMP / 'output' / f'ep_{int(target_ep):02d}' / 'episode.md'
        if not ep_path.exists():
            return []
        text = ep_path.read_text(encoding='utf-8')
        name, _age = get_passenger_info(text)
        if not name or name != c.char_name:
            return []  # khong phai passenger tam diem cua tap nay - KHONG bia gan nham
        return [q for q, _ctx in extract_quotes(text) if len(q) >= 5]


if __name__ == '__main__':
    import json
    dm = DialogueManager()
    demo_id = next((c.id for c in dm.registry.all('passenger') if c.assigned_ep), None)
    if demo_id:
        print(json.dumps(dm.get_dialogue_context(demo_id), ensure_ascii=False, indent=2))
    else:
        print('Khong tim thay passenger co assigned_ep de demo.')
