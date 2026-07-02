"""
SVHMP Adversarial Skeptic — F4 round 14
Lock date: 2026-06-26 (Mr.Long approve PDF adversarial-multiagent research adoption)

Pattern source:
- Du et al. ICML 2024 "Multi-Agent Debate" (arXiv 2305.14325)
- Liang et al. EMNLP 2024 "Encouraging Divergent Thinking through Multi-Agent Debate"
  → coined "Degeneration of Thought (DoT)" failure mode — same model self-critique
  becomes rubber-stamp.
- Mitigation: SEPARATE MODEL skeptic attacks both critics' findings + script.

Usage (Phase F4 wired actual after F3 Ollama gemma2:9b pulled):
    python tools/adversarial_skeptic.py \\
        --qa-output runtime/qa_output_ep01.json \\
        --episode output/ep_01/episode.md \\
        --output runtime/adversarial_skeptic_ep01.json

Algorithm:
1. Load QA findings (PHASE 12.0-12.18 verdicts from Claude QA)
2. Load original episode draft
3. Invoke DIFFERENT model (Gemma 2 9B via Ollama) with skeptic prompt:
   "Attack each QA finding: argue why it's wrong/trivial.
    Find issues QA missed."
4. Output: skeptic_review.json
   - attacked_qa_findings: [{finding_id, attack_reasoning, confidence}]
   - missed_issues: [{issue, severity, evidence}]
   - final_verdict_recommendation: ACCEPT | REJECT | NEEDS_HUMAN

Apply rule "cấm suy luận":
- Prompts skeptic role-defined explicitly (devil's advocate)
- Confidence scores forced 0-100 (não free-form)
- Output structured JSON (parseable, không free-form)
"""
import argparse
import json
import sys
import os
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent
_TOOLS = SVHMP / 'tools'
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

try:
    from llm_router import call_provider
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


SKEPTIC_SYSTEM_PROMPT = """Bạn là Adversarial Skeptic cho SVHMP (Vietnamese horror narration pipeline).

Vai trò:
- Tấn công findings của QA (Claude generated). KHÔNG đồng ý mặc định.
- Tìm issues QA bỏ qua.
- Đưa argument concrete, không vague.

Output STRUCTURED JSON:
{
  "attacked_qa_findings": [
    {"finding_id": "<id>", "attack_reasoning": "<why QA wrong>", "confidence": 0-100}
  ],
  "missed_issues": [
    {"issue": "<description>", "severity": "critical|major|minor", "evidence": "<quote>"}
  ],
  "final_verdict": "ACCEPT|REJECT|NEEDS_HUMAN",
  "verdict_reasoning": "<short>"
}

Rule cứng:
- KHÔNG tự đặt câu hỏi loanh quanh. Direct attack.
- Mỗi attack/missed phải có evidence (quote câu episode hoặc cite rule bị vi phạm).
- Confidence forced 0-100 numeric.
- KHÔNG echo lại findings — chỉ attack hoặc supplement.
"""


def build_skeptic_prompt(qa_output: dict, episode_md: str) -> str:
    """Build user prompt cho skeptic invocation."""
    qa_findings_str = json.dumps(qa_output.get('findings', qa_output), ensure_ascii=False, indent=2)
    return f"""# QA OUTPUT TỪ CLAUDE (need attack):

```json
{qa_findings_str}
```

# EPISODE DRAFT:

{episode_md[:8000]}  # truncate to fit context

# YÊU CẦU:
1. ATTACK 3-5 QA findings — argue why wrong/trivial.
2. FIND 2-5 issues QA missed.
3. Output STRUCTURED JSON theo schema system prompt.
"""


def invoke_skeptic(qa_output_path: str, episode_path: str, skeptic_provider: str = 'ollama_local') -> dict:
    """Invoke skeptic on different model than Claude QA."""
    with open(qa_output_path, encoding='utf-8') as f:
        qa_output = json.load(f)
    with open(episode_path, encoding='utf-8') as f:
        episode_md = f.read()

    if not LLM_AVAILABLE:
        return {
            'error': 'llm_router not available — wire F3 Ollama first',
            'tentative': True,
        }

    prompt = build_skeptic_prompt(qa_output, episode_md)
    response = call_provider(
        skeptic_provider,
        prompt,
        system=SKEPTIC_SYSTEM_PROMPT,
        temperature=0.5,
        max_tokens=2048,
    )

    if response is None:
        return {
            'error': f'Skeptic provider {skeptic_provider} returned None — likely model not pulled yet',
            'recommendation': 'Run: ollama pull gemma2:9b',
            'tentative': True,
        }

    # Try parse JSON from response
    try:
        # Strip markdown code fences if present
        cleaned = response.strip()
        if cleaned.startswith('```'):
            cleaned = cleaned.split('```', 2)[1]
            if cleaned.startswith('json'):
                cleaned = cleaned[4:].strip()
            cleaned = cleaned.rstrip('`').strip()
        parsed = json.loads(cleaned)
        parsed['_skeptic_provider'] = skeptic_provider
        parsed['_raw_response_length'] = len(response)
        return parsed
    except json.JSONDecodeError as e:
        return {
            'error': f'Skeptic response not valid JSON: {e}',
            'raw_response': response[:1000],
            'skeptic_provider': skeptic_provider,
        }


def cli():
    parser = argparse.ArgumentParser(description='SVHMP Adversarial Skeptic (F4 round 14)')
    parser.add_argument('--qa-output', required=True, help='Path to QA output JSON (Claude)')
    parser.add_argument('--episode', required=True, help='Path to episode.md draft')
    parser.add_argument('--output', required=True, help='Path to write skeptic review JSON')
    parser.add_argument('--provider', default='ollama_local',
                        help='Skeptic provider (ollama_local=gemma2:9b / ollama_qwen=qwen2.5:14b)')
    args = parser.parse_args()

    result = invoke_skeptic(args.qa_output, args.episode, args.provider)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    if 'error' in result:
        print(f"✗ Skeptic FAIL: {result['error']}", file=sys.stderr)
        if 'recommendation' in result:
            print(f"  → {result['recommendation']}", file=sys.stderr)
        sys.exit(1)

    print(f"✓ Skeptic review saved: {args.output}")
    print(f"  Attacked QA findings: {len(result.get('attacked_qa_findings', []))}")
    print(f"  Missed issues found: {len(result.get('missed_issues', []))}")
    print(f"  Verdict: {result.get('final_verdict', 'unknown')}")


if __name__ == '__main__':
    cli()
