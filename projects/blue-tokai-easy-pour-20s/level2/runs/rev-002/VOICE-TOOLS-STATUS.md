# Voice tools status — Level 2 / Level 3

Checked 2026-11-15 on this machine.

| Tool | Installed? | Working? | Notes |
|---|---|---|---|
| ShortGPT Edge TTS | yes (`D:\shortgpt\.venv`) | **yes** | produced male 19.10 s and female 19.18 s takes |
| faster-whisper (cached tiny.en) | yes (Pinaka venv) | yes | transcription/timing, not a TTS model |
| AI4Bharat Indic Parler-TTS | **no** | no | `parler_tts` not installed, no cached weights |
| Kokoro-82M | **no** | no | `kokoro` not installed, no cached weights |
| Qwen3-TTS VoiceDesign | **no** | no | `qwen_tts` not installed, no cached weights |
| Chatterbox Multilingual | **no** | no | `chatterbox` not installed, no cached weights |

## What this means

- The working voice is **ShortGPT Edge TTS** (free, no key).
- The two audition takes use the same continuous script with different
  profiles/rates:
  - `VO-M1` male, `en-IN-PrabhatNeural`, rate `-25%`, 19.10 s.
  - `VO-F1` female, `en-IN-NeerjaNeural`, rate `-22%`, 19.18 s.
- Indic Parler-TTS / Kokoro / Qwen3-TTS / Chatterbox can be installed later for
  Hindi direction, custom voices or reference-based delivery; they are not
  available now, so no claim is made that they ran.

## Files

- `VOICE-DIRECTION.md` / `voice-direction.json`
- `generated/AS-09-male-take.mp3`
- `generated/AS-09-female-take.mp3`
- `voice-take-male.json`, `voice-take-female.json`
