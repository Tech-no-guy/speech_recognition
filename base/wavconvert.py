from pydub import AudioSegment
import os

def convert_to_wav(input_path, output_path=None):
    """
    Convert any audio file to WAV format
    
    Parameters:
    input_path (str): Path to input audio file
    output_path (str): Path for output WAV file (optional)
    
    Returns:
    str: Path to the converted WAV file
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # If output path is not specified, create one based on input file
        if output_path is None:
            output_path = os.path.splitext(input_path)[0] + '.wav'
        
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        
        # Export as WAV
        audio.export(output_path, format='wav')
        
        print(f"Successfully converted {input_path} to {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Error converting file: {str(e)}")
        return None

def batch_convert_to_wav(input_folder, output_folder=None):
    """
    Convert all audio files in a folder to WAV format
    
    Parameters:
    input_folder (str): Path to folder containing audio files
    output_folder (str): Path to output folder for WAV files (optional)
    """
    try:
        # Check if input folder exists
        if not os.path.exists(input_folder):
            raise FileNotFoundError(f"Input folder not found: {input_folder}")
        
        # If output folder is not specified, create one based on input folder
        if output_folder is None:
            output_folder = os.path.join(input_folder, 'wav_converted')
        
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Process each file in the input folder
        for filename in os.listdir(input_folder):
            input_path = os.path.join(input_folder, filename)
            
            # Skip if it's a directory
            if os.path.isdir(input_path):
                continue
            
            # Create output path
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '.wav')
            
            # Convert file
            convert_to_wav(input_path, output_path)
        
        print(f"Batch conversion completed. WAV files saved in: {output_folder}")
        
    except Exception as e:
        print(f"Error during batch conversion: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Convert a single file
    input_file = "kannada_audio.mp3"  # Replace with your audio file path
    converted_file = convert_to_wav(input_file)
    
