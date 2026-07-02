"""
SVHMP Multi-LLM Router — F4.1 round 14.
Abstract LLM call layer + fallback chain.

Architecture (inspired by ainovel-cli OpenRouter/Anthropic/Gemini/OpenAI swap):
  - Primary: Claude (Anthropic API)
  - Fallback 1: Gemini (Google API)
  - Fallback 2: OpenAI GPT-4 (OpenAI API)
  - Fallback 3: Local Ollama (offline)

Usage:
  from tools.llm_router import call_llm
  response = call_llm(prompt="...", role="generator", retry_chain=True)

Apply rule "cấm suy luận":
- API key per provider lưu .env (KHÔNG hardcode)
- Em KHÔNG tự bịa cost per token — Mr.Long fill khi setup
- Model name per provider lock theo VERSION.md
"""
import os
import sys
import time
from typing import Optional, Callable
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# Model config — Mr.Long approve trước khi adopt
MODEL_REGISTRY = {
    'claude': {
        'provider': 'anthropic',
        'model_name': 'claude-opus-4-7',  # current latest 2026-01
        'cost_per_1m_input_usd': None,    # TENTATIVE — Mr.Long fill
        'cost_per_1m_output_usd': None,   # TENTATIVE — Mr.Long fill
        'context_window': 1_000_000,
        'env_key': 'ANTHROPIC_API_KEY',
    },
    'gemini': {
        'provider': 'google',
        'model_name': 'gemini-2.5-pro',   # TENTATIVE — verify available 2026-06
        'cost_per_1m_input_usd': None,
        'cost_per_1m_output_usd': None,
        'context_window': 2_000_000,
        'env_key': 'GOOGLE_API_KEY',
    },
    'openai': {
        'provider': 'openai',
        'model_name': 'gpt-4o',           # TENTATIVE
        'cost_per_1m_input_usd': None,
        'cost_per_1m_output_usd': None,
        'context_window': 128_000,
        'env_key': 'OPENAI_API_KEY',
    },
    'ollama_local': {
        'provider': 'ollama',
        'model_name': 'gemma2:9b',        # F3 round 14: best Vietnamese ≤14B per PDF research (VMLU 59.04)
        'cost_per_1m_input_usd': 0.0,
        'cost_per_1m_output_usd': 0.0,
        'context_window': 8_192,           # Gemma 2 native 8K (some quants extend)
        'env_key': None,  # local, no API key
        'install_cmd': 'ollama pull gemma2:9b',  # ~5.5GB download
    },
    'ollama_qwen': {
        'provider': 'ollama',
        'model_name': 'qwen2.5:14b',      # F3 round 14: strongest Apache-2.0 ≤14B (PDF research)
        'cost_per_1m_input_usd': 0.0,
        'cost_per_1m_output_usd': 0.0,
        'context_window': 32_768,
        'env_key': None,
        'install_cmd': 'ollama pull qwen2.5:14b',  # ~8.7GB download
    },
}

# Fallback chain — Mr.Long approve order
DEFAULT_CHAIN = ['claude', 'gemini', 'openai', 'ollama_local']

# Role → model preference (vd: TTS skip ollama vì cần multi-modal)
ROLE_PREFERENCES = {
    'director': DEFAULT_CHAIN,
    'generator': DEFAULT_CHAIN,
    'qa': DEFAULT_CHAIN,
    'tts': ['claude', 'gemini'],  # TTS không có local fallback
    'tts_adapter': DEFAULT_CHAIN,
    'video': ['claude'],          # multi-modal vision required
    'publisher': DEFAULT_CHAIN,
}


def check_provider_available(provider_id: str) -> bool:
    """Check if provider has valid API key set in env."""
    config = MODEL_REGISTRY.get(provider_id, {})
    env_key = config.get('env_key')
    if env_key is None:
        return True  # local, no key needed
    return bool(os.environ.get(env_key))


def call_provider(provider_id: str, prompt: str, system: Optional[str] = None, **kwargs) -> Optional[str]:
    """Call specific provider. Returns None if call fails (caller handles fallback).

    Round 14 F3: Ollama provider wired actual (gemma2:9b/qwen2.5:14b/etc).
    Other providers (Claude/Gemini/OpenAI): still skeleton — Mr.Long approve install SDK + API key.
    """
    config = MODEL_REGISTRY.get(provider_id)
    if not config:
        return None

    if not check_provider_available(provider_id):
        print(f"  ⚠ {provider_id}: API key not set ({config.get('env_key')})", file=sys.stderr)
        return None

    # F3 Round 14: Ollama actual wired (local, no API key needed). Handles all Ollama-backed providers.
    if config.get('provider') == 'ollama':
        try:
            import ollama
            import subprocess

            CREATE_NO_WINDOW = 0x08000000 if __import__("sys").platform == "win32" else 0
            client = ollama.Client()
            messages = []
            if system:
                messages.append({'role': 'system', 'content': system})
            messages.append({'role': 'user', 'content': prompt})
            response = client.chat(
                model=config['model_name'],
                messages=messages,
                options={
                    'temperature': kwargs.get('temperature', 0.7),
                    'num_predict': kwargs.get('max_tokens', 2048),
                },
                keep_alive=0,  # B34 fix: unload model after invoke → free VRAM cho TTS/SDXL
            )
            result = response['message']['content']
            # B34 fix Phase 2: kill llama-server.exe sau invoke để free CUDA VRAM
            # (Ollama keep_alive=0 chỉ unload model logically, CUDA context vẫn giữ ~7GB)
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'llama-server.exe'],
                              capture_output=True, timeout=5, creationflags=CREATE_NO_WINDOW)
            except Exception:
                pass  # best-effort, không break flow
            return result
        except Exception as e:
            print(f"  ⚠ ollama_local fail: {e}", file=sys.stderr)
            return None


def free_ollama_vram():
    """Force free VRAM bằng cách kill llama-server.exe (Ollama worker process).
    Ollama daemon tự respawn khi có request mới (~20s reload tax).
    Dùng sau Skeptic invoke + trước TTS render để tránh OOM."""
    try:
        import subprocess
        subprocess.run(['taskkill', '/F', '/IM', 'llama-server.exe'],
                       capture_output=True, timeout=5, creationflags=CREATE_NO_WINDOW)
        return True
    except Exception:
        return False

    # Other providers: skeleton (TENTATIVE — Mr.Long approve install SDK)
    print(f"  ! {provider_id}: SDK integration TENTATIVE — Mr.Long approve actual SDK install", file=sys.stderr)
    return None


def call_llm(
    prompt: str,
    role: str = 'generator',
    retry_chain: bool = True,
    max_retries_per_provider: int = 2,
    retry_delay_s: float = 1.0,
) -> dict:
    """Call LLM với fallback chain.

    Returns:
        {
            'response': str | None,
            'provider_used': str | None,
            'attempts': list[{provider, status, error}],
            'success': bool,
        }
    """
    chain = ROLE_PREFERENCES.get(role, DEFAULT_CHAIN)
    attempts = []
    response = None
    provider_used = None

    for provider_id in chain:
        for attempt in range(1, max_retries_per_provider + 1):
            try:
                response = call_provider(provider_id, prompt)
                if response:
                    provider_used = provider_id
                    attempts.append({'provider': provider_id, 'status': 'success', 'attempt': attempt})
                    return {
                        'response': response,
                        'provider_used': provider_used,
                        'attempts': attempts,
                        'success': True,
                    }
                else:
                    attempts.append({'provider': provider_id, 'status': 'unavailable_or_skeleton', 'attempt': attempt})
                    break  # No retry if skeleton (will be implemented)
            except Exception as e:
                attempts.append({'provider': provider_id, 'status': 'error', 'attempt': attempt, 'error': str(e)[:80]})
                if attempt < max_retries_per_provider:
                    time.sleep(retry_delay_s)
        if not retry_chain:
            break  # caller chose single-shot

    return {
        'response': None,
        'provider_used': None,
        'attempts': attempts,
        'success': False,
    }


def main():
    """CLI smoke test."""
    print("=" * 75)
    print("SVHMP LLM Router — F4.1 round 14 (skeleton)")
    print("=" * 75)
    print("\nProvider availability:")
    for pid, config in MODEL_REGISTRY.items():
        avail = check_provider_available(pid)
        marker = "✓" if avail else "✗"
        env = config.get('env_key', '(local)')
        print(f"  {marker} {pid:15s} → {config['model_name']:25s} env={env}")

    print("\nRole → chain preference:")
    for role, chain in ROLE_PREFERENCES.items():
        print(f"  {role:15s} → {' → '.join(chain)}")

    print("\nTest call (skeleton — no actual SDK):")
    result = call_llm(prompt="test", role="generator")
    print(f"  Success: {result['success']}")
    print(f"  Attempts: {len(result['attempts'])}")
    for a in result['attempts']:
        print(f"    - {a}")

    print("\n" + "=" * 75)
    print("Status: SKELETON ready. Mr.Long approve trước khi adopt actual SDK calls.")
    print("Next: install SDK (pip install anthropic google-genai openai ollama)")
    print("=" * 75)


if __name__ == '__main__':
    main()
