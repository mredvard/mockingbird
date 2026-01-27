import sys
import mlx_whisper

MODEL = "mlx-community/whisper-large-v3-turbo"

def transcribe_audio(filename: str = "voice_sample.wav"):
    print(f"Transcribing {filename}...")
    result = mlx_whisper.transcribe(filename, path_or_hf_repo=MODEL)
    print("\nTranscription:")
    print(result["text"])
    return result["text"]

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "voice_sample.wav"
    transcribe_audio(filename)
