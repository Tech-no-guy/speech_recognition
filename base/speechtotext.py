import speech_recognition as sr
import os
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
            # Load audio file
            sound = AudioSegment.from_wav(path)
            
            # Split audio where silence is 700ms or more and get chunks
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
            
            # Process each chunk
            for i, audio_chunk in enumerate(chunks, start=1):
                chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
                audio_chunk.export(chunk_filename, format="wav")
                
                # Recognize chunk
                with sr.AudioFile(chunk_filename) as source:
                    audio = self.recognizer.record(source)
                    try:
                        text = self.recognizer.recognize_google(audio, language='kn-IN')
                        full_text += text + " "
                    except sr.UnknownValueError:
                        print(f"Could not understand chunk {i}")
                    except sr.RequestError as e:
                        print(f"Error with chunk {i}: {str(e)}")
                
                # Clean up chunk file
                os.remove(chunk_filename)
            
            # Clean up chunks directory
            os.rmdir(folder_name)
            
            return full_text.strip()
            
        except Exception as e:
            print(f"Error processing large audio: {str(e)}")
            return None

    def transcribe_audio(self, audio_path, output_file="transcription.txt"):
        """
        Main function to transcribe audio to Kannada text
        """
        try:
            # Check if file exists
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Convert to WAV if needed
            file_ext = os.path.splitext(audio_path)[1].lower()
            if file_ext != '.wav':
                wav_path = os.path.splitext(audio_path)[0] + '.wav'
                audio_path = self.convert_to_wav(audio_path, wav_path)
                if not audio_path:
                    raise Exception("Failed to convert audio to WAV format")
            
            # Get audio duration
            duration = self.get_audio_duration(audio_path)
            
            # Choose processing method based on duration
            if duration > 60:  # For files longer than 60 seconds
                text = self.transcribe_large_audio(audio_path)
            else:
                # For shorter files, process directly
                with sr.AudioFile(audio_path) as source:
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio, language='kn-IN')
            
            if text:
                # Save transcription to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"Transcription completed and saved to {output_file}")
                return text
            else:
                raise Exception("No text was transcribed from the audio")
            
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            return None

    def adjust_noise(self, audio_path):
        """
        Adjust for background noise in the audio
        """
        try:
            with sr.AudioFile(audio_path) as source:
                self.recognizer.adjust_for_ambient_noise(source)
                return True
        except Exception as e:
            print(f"Error adjusting for noise: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    transcriber = AudioTranscriber()
    
    # Replace with your audio file path
    audio_file = "audio_chunks/chunk_1.wav"  # Can be mp3, wav, etc.
    output_file = "kannada_transcription.txt"
    
    # Transcribe the audio
    transcribed_text = transcriber.transcribe_audio(audio_file, output_file)
    
    if transcribed_text:
        print("Transcription successful!")
        print("Transcribed text:")
        print(transcribed_text)
    else:
        print("Transcription failed. Please check the error messages above.")