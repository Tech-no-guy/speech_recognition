import os
import json
import numpy as np
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from flask import Flask, render_template, jsonify
from sentence_transformers import SentenceTransformer, util
import wave
import tempfile

app = Flask(__name__)

# Function to get relevant audio file paths
def get_relevant_audio_files(query, json_file_path='translated_output.json', folder_path='audio_chunks_database', max_files=5):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    audio_paths = list(data.keys())
    transcripts = list(data.values())

    # Use SentenceTransformer model to encode the transcripts
    model = SentenceTransformer('all-MiniLM-L6-v2')
    transcript_embeddings = model.encode(transcripts, convert_to_tensor=True)

    # Encode the query
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Calculate similarity scores
    similarity_scores = util.cos_sim(query_embedding, transcript_embeddings)[0]

    # Get indices of the top relevant audio files
    top_indices = np.argsort(-similarity_scores.cpu().numpy())[:max_files]

    # Prepend folder path to file names
    relevant_audio_paths = [os.path.join(folder_path, audio_paths[i]) for i in top_indices]
    return relevant_audio_paths

# Function to capture Kannada audio from the microphone and convert it to text
def get_query_from_microphone():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Please ask your query in Kannada:")
        recognizer.adjust_for_ambient_noise(source)
        audio_data = recognizer.listen(source)
        try:
            # Set the language to Kannada (kn-IN)
            query = recognizer.recognize_google(audio_data, language="kn-IN")
            print(f"Your Query (Kannada): {query}")
            return query
        except sr.UnknownValueError:
            print("Sorry, I could not understand the Kannada audio.")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None

# Function to record audio from the microphone and save it to a temporary file
def record_audio(duration=10):
    """Record audio from microphone for specified duration"""
    try:
        temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        sample_rate = 16000  # Standard sample rate for speech recognition
        
        print("Recording your query...")
        with sd.InputStream(samplerate=sample_rate, channels=1, callback=lambda indata, frames, time, status: sf.write(temp_wav_file.name, indata, sample_rate)):
            sd.sleep(duration * 1000)  # Convert to milliseconds
            
        print(f"Audio recorded and saved to: {temp_wav_file.name}")
        return temp_wav_file.name
        
    except Exception as e:
        print(f"Error recording audio: {str(e)}")
        if os.path.exists(temp_wav_file.name):
            os.remove(temp_wav_file.name)
        return None

# Route for rendering the frontend page
@app.route("/")
def home():
    return render_template("index.html")

# API to capture query from microphone and fetch relevant audio files
@app.route("/api/query-microphone", methods=["GET"])
def query_microphone():
    audio_path = None
    try:
        # Record audio
        audio_path = record_audio()
        print(f"Debug: Audio recorded at {audio_path}")
        
        # Convert audio to text
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            print("Debug: Reading audio file")
            recognizer.adjust_for_ambient_noise(source, duration=1)  # Added duration parameter
            print(f"Debug: Energy threshold set to {recognizer.energy_threshold}")
            audio_data = recognizer.record(source)
            print("Debug: Converting speech to text...")
            
            try:
                # First attempt with show_all=True to get detailed response
                raw_result = recognizer.recognize_google(
                    audio_data, 
                    language="kn-IN",
                    show_all=True
                )
                print(f"Debug: Raw recognition result: {raw_result}")
                
                if not raw_result:
                    print("Debug: No speech detected in the audio")
                    return jsonify({"error": "No speech detected. Please speak clearly and try again."}), 400
                
                # Get the most confident result
                query_text = raw_result['alternative'][0]['transcript'] if isinstance(raw_result, dict) else raw_result
                print(f"Debug: Final converted text: {query_text}")
                
                # Get relevant files
                print(f"Debug: Searching for relevant files with query: {query_text}")
                relevant_files = get_relevant_audio_files(query_text)
                
                if not relevant_files:
                    return jsonify({"error": "No matching audio files found"}), 404
                
                return jsonify({
                    "message": "Audio files retrieved successfully",
                    "audioFiles": relevant_files,
                    "queryText": query_text
                }), 200
                    
            except sr.UnknownValueError:
                print("Debug: Could not understand the audio")
                return jsonify({"error": "Could not understand the audio. Please speak clearly and try again."}), 400
            except sr.RequestError as e:
                print(f"Debug: Google Speech Recognition service error: {str(e)}")
                return jsonify({"error": "Speech recognition service error. Please try again later."}), 503
            
    except Exception as e:
        print(f"Debug: Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    finally:
        # Clean up temporary file
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                print(f"Debug: Cleaned up temporary file: {audio_path}")
            except Exception as e:
                print(f"Debug: Failed to clean up temporary file: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)
