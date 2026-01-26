# Mockingbird

Text-to-speech with voice cloning using MLX on Apple Silicon.

## Setup

```bash
uv sync
```

## Usage

### Generate speech

```bash
uv run python -m mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16 \
  --text "Hello, this is a test." \
  --play
```

### Voice cloning

1. Record your voice sample:

```bash
# Record for 5 seconds (default)
uv run python record.py

# Record for 10 seconds
uv run python record.py 10
```

2. Generate speech with your voice:

```bash
uv run python -m mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16 \
  --text "Whatever you want it to say." \
  --ref_audio voice_sample.wav \
  --ref_text "What you said in the recording." \
  --play
```

## Models

- `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16` - Qwen3 TTS (voice cloning supported)
- `mlx-community/Kokoro-82M-bf16` - Kokoro (multilingual, use `--lang_code a` for American English)
