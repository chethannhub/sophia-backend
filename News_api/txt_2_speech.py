import os
import datetime
from pydub import AudioSegment
from google.cloud import texttospeech
from dotenv import load_dotenv
import json
from . import create_con_text
import uuid

load_dotenv()

class TextToSpeech:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.client = texttospeech.TextToSpeechClient()

    def synthesize_speech(self, voice_name, text, output_file):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice_name,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        with open(output_file, "wb") as out:
            out.write(response.audio_content)
            print(f"Speech synthesis succeeded for {output_file}")
            return output_file
        print(f"Speech synthesis failed for {output_file}")
        return None

    def process_conversation(self, input_file, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        unique_id = str(uuid.uuid4())
        output_dir = os.path.join(output_folder, unique_id)
        os.makedirs(output_dir, exist_ok=True)

        with open(input_file, 'r') as f:
            conversation_data = json.load(f)
        i = 1
        audio_files = []
        for i, turn in enumerate(conversation_data['conversation']):
            voices = {
                'Andrew Krepthy': "en-US-Chirp-HD-D",
                'Smithi': "en-US-Chirp-HD-F"
                
            }
            speaker = turn['speaker']
            if i % 2 == 0:
                voice_name = voices.get(speaker, "en-US-Chirp-HD-D")  # Default to male voice if unknown
            else:
                voice_name = voices.get(speaker, "en-US-Chirp-HD-F")  # Default to male voice if unknown
            i +=1
            speaker_slug = speaker.lower().replace(" ", "_")
            output_file = os.path.join(output_dir, f'{speaker_slug}_part_{i}.mp3')
            
            result = self.synthesize_speech(voice_name, turn['text'], output_file)
            
            if result:
                audio_files.append(result)


        merged_audio = self.merge_audio_files_pydub(audio_files, output_dir)
        self.cleanup_files(audio_files + [os.path.join(output_dir, 'input.txt')])
        
        return merged_audio

    def merge_audio_files_pydub(self , audio_files, output_dir):
        # Create an empty AudioSegment
        combined = AudioSegment.empty()
        sorted_files = sorted(audio_files , key = lambda x : int(x.split("_")[-1].split(".")[0]))
        # Iterate over each audio file and append to the combined segment
        for file_path in sorted_files:
            audio = AudioSegment.from_file(file_path)
            combined += audio
        os.makedirs(output_dir, exist_ok=True)
        # Define output file path
        output_file_path = os.path.join(output_dir, 'output.mp3')

        # Export the combined audio
        combined.export(output_file_path, format='mp3')

        print(f"Audio files have been merged into '{output_file_path}'")
        return output_file_path

    def cleanup_files(self, files_to_remove):
        for file in files_to_remove:
            if os.path.exists(file):
                os.remove(file)

def text_to_speech(urls, output_folder= "summarized/audio"):
    os.makedirs("summarized/audio" , exist_ok=True)
    os.makedirs("summarized/text" , exist_ok=True)
    if not os.path.exists(output_folder + "/history.json"):
        with open(output_folder + "/history.json", "w") as file:
            json.dump({"history": []}, file)
    with open(output_folder + "/history.json", "r") as file:
        history = json.load(file)
    for i in history["history"]:
        if i["urls"] == urls:
            return i["path"]

    input_file = f"summarized/text/{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}.json"
    create_con_text.get_context(urls ,input_file)
    tts = TextToSpeech()

    out = tts.process_conversation(input_file, output_folder)

    history["history"].append({"urls": urls , "path": out})
    with open(output_folder+"/history.json" , "w") as file:
        json.dump(history , file , indent=4)
    return out