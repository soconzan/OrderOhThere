import sounddevice as sd
from scipy.io.wavfile import write
import os
from openai import OpenAI


# 오디오 녹음
def record_audio(seconds=10, samplerate=44100, channels=2, filename='temp_audio.wav'):
    print(f"{seconds}초 동안 마이크로부터 오디오를 녹음합니다...")
    recording = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=channels, dtype='int16')
    sd.wait()  # 녹음이 완료될 때까지 기다립니다
    write(filename, samplerate, recording)  # 파일로 저장
    print(f"녹음 완료: {filename}")

# 텍스트 변환
def audio_to_text(filename):
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    with open(filename, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription.text


if __name__ == "__main__":
    seconds = 5
    samplerate = 44100
    channels = 2
    audio_filename = 'temp_audio.wav'

    record_audio(seconds, samplerate, channels, audio_filename)

    text = audio_to_text(audio_filename)

    print("변환된 텍스트:")
    print(text)
