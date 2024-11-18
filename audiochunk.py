from pydub import AudioSegment
from pydub.utils import make_chunks
import os
from pathlib import Path

# Function to split the audio file into fixed-duration chunks
def split_audio(file_path, chunk_duration_ms, output_dir):
    # Load the audio file
    print(f"Processing: {file_path}")
    audio = AudioSegment.from_file(file_path)

    # Split the audio into chunks of specified duration
    chunks = make_chunks(audio, chunk_duration_ms)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save each chunk as a separate file
    for i, chunk in enumerate(chunks):
        chunk_name = os.path.join(output_dir, f"{Path(file_path).stem}_chunk_{i+1}.wav")
        chunk.export(chunk_name, format="wav")
        print(f"Exported: {chunk_name}")

    print(f"Splitting completed for {file_path}! Files are saved in: {output_dir}")

# Function to process all audio files in a folder
def process_audio_folder(input_folder, chunk_duration_ms, output_base_dir):
    # Walk through the folder and process all audio files
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.mp3', '.wav', '.flac')):  # Supported formats
                input_file = os.path.join(root, file)
                
                # Create output directory structure mirroring the input folder
                relative_path = os.path.relpath(root, input_folder)
                output_dir = os.path.join(output_base_dir, relative_path)
                
                # Split the audio file
                try:
                    split_audio(input_file, chunk_duration_ms, output_dir)
                except Exception as e:
                    print(f"Error processing {input_file}: {e}")

def main():
    input_folder = "data"  # Replace with the folder containing audio files
    chunk_duration_ms = 30000  # Duration of each chunk in milliseconds (e.g., 30 seconds)
    output_base_dir = "audio_chunks_database"  # Base directory to save all chunks

    # Process all audio files in the folder
    process_audio_folder(input_folder, chunk_duration_ms, output_base_dir)

if __name__ == "__main__":
    main()
 