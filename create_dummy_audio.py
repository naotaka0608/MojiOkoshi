import numpy as np
import soundfile as sf

def create_dummy_audio(filename="test_audio.wav", duration=5, samplerate=16000):
    t = np.linspace(0, duration, int(samplerate * duration))
    # Generate a 440 Hz sine wave (A4)
    data = 0.5 * np.sin(2 * np.pi * 440 * t)
    sf.write(filename, data, samplerate)
    print(f"Created {filename}")

if __name__ == "__main__":
    create_dummy_audio()
