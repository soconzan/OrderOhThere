from openai import OpenAI
import os

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# audio_file = open("audio_files/hyeinbubble.mp3", "rb")
# audio_file = open("audio_files/minizin01.mp3", "rb"
audio_file = open("audio_files/strangecat.mp3", "rb")
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file
)
print(transcription.text)
