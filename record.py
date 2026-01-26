import sounddevice as sd
import numpy as np
import wave
import sys

SAMPLE_RATE = 24000

def record_voice(duration: int = 5, filename: str = "voice_sample.wav"):
    print(f"Recording for {duration} seconds... Speak now!")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype=np.int16)
    sd.wait()
    print("Done recording.")

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())

    print(f"Saved to {filename}")

if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    record_voice(duration)
