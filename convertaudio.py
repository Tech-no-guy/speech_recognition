import speech_recognition as sr
import os
import json
from pydub import AudioSegment
from pydub.silence import split_on_silence
import wave
import contextlib

class AudioTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    def get_audio_duration(self, audio_path):
        """Get duration of audio file in seconds"""
        with contextlib.closing(wave.open(audio_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration

    def convert_to_wav(self, audio_path, output_path):
        """Convert audio file to WAV format if needed"""
        try:
            audio = AudioSegment.from_file(audio_path)
            audio.export(output_path, format="wav")
            return output_path
        except Exception as e:
            print(f"Error converting audio: {str(e)}")
            return None

    def transcribe_large_audio(self, path):
        """
        Splits larger audio files and transcribes them in chunks
        """
        try:
            sound = AudioSegment.from_wav(path)
            chunks = split_on_silence(
                sound,
                min_silence_len=700,
                silence_thresh=sound.dBFS-14,
                keep_silence=500
            )
            
            folder_name = "audio-chunks"
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
            
            full_text = ""
            
            for i, audio_chunk in enumerate(chunks, start=1):
                chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
                audio_chunk.export(chunk_filename, format="wav")
                
                with sr.AudioFile(chunk_filename) as source:
                    audio = self.recognizer.record(source)
                    try:
                        text = self.recognizer.recognize_google(audio, language='kn-IN')
                        full_text += text + " "
                    except sr.UnknownValueError:
                        print(f"Could not understand chunk {i}")
                    except sr.RequestError as e:
                        print(f"Error with chunk {i}: {str(e)}")
                
                os.remove(chunk_filename)
            
            os.rmdir(folder_name)
            return full_text.strip()
        except Exception as e:
            print(f"Error processing large audio: {str(e)}")
            return None

    def transcribe_audio(self, audio_path):
        """
        Transcribes a single audio file to Kannada text
        """
        try:
            file_ext = os.path.splitext(audio_path)[1].lower()
            if file_ext != '.wav':
                wav_path = os.path.splitext(audio_path)[0] + '.wav'
                audio_path = self.convert_to_wav(audio_path, wav_path)
                if not audio_path:
                    raise Exception("Failed to convert audio to WAV format")
            
            duration = self.get_audio_duration(audio_path)
            
            if duration > 60:
                return self.transcribe_large_audio(audio_path)
            else:
                with sr.AudioFile(audio_path) as source:
                    audio = self.recognizer.record(source)
                    return self.recognizer.recognize_google(audio, language='kn-IN')
        except Exception as e:
            print(f"Error transcribing file {audio_path}: {str(e)}")
            return None

    def transcribe_folder(self, folder_path, output_file="transcriptions.json"):
        """
        Transcribes all audio files in a folder and saves the output as JSON
        """
        try:
            if not os.path.isdir(folder_path):
                raise NotADirectoryError(f"Provided path is not a directory: {folder_path}")
            
            transcriptions = {}
            for root, _, files in os.walk(folder_path):
                for file in files:
                    audio_path = os.path.join(root, file)
                    print(f"Processing: {audio_path}")
                    text = self.transcribe_audio(audio_path)
                    if text:
                        transcriptions[audio_path] = text
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(transcriptions, f, ensure_ascii=False, indent=4)
            
            print(f"Transcriptions saved to {output_file}")
            return transcriptions
        except Exception as e:
            print(f"Error processing folder: {str(e)}")
            return None

# Example usage
if __name__ == "__main__":
    transcriber = AudioTranscriber()
    
    # Replace with your folder path containing audio files
    audio_folder = "audio_chunks_database"  # Folder containing audio files
    output_file = "transcriptionss.json"
    
    # Transcribe all audio files in the folder
    transcriptions = transcriber.transcribe_folder(audio_folder, output_file)
    
    if transcriptions:
        print("Transcription successful!")
        print(json.dumps(transcriptions, ensure_ascii=False, indent=4))
    else:
        print("Transcription failed. Please check the error messages above.")
