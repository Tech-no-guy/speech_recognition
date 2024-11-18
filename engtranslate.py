import json
from googletrans import Translator

# Function to translate Kannada text to English
def translate_kannada_to_english(input_file, output_file):
    # Initialize the Translator
    translator = Translator()

    # Read the JSON input from the file
    with open(input_file, 'r', encoding='utf-8') as file:
        input_data = json.load(file)

    translated_data = {}

    # Translate each value in the JSON
    for audio_path, kannada_text in input_data.items():
        try:
            # Translate Kannada to English
            translation = translator.translate(kannada_text, src='kn', dest='en')
            translated_data[audio_path] = translation.text
        except Exception as e:
            translated_data[audio_path] = f"Error translating: {str(e)}"

    # Write the translated data to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(translated_data, file, ensure_ascii=False, indent=4)

    print(f"Translation completed. Translated data saved to: {output_file}")

def main():
    input_file = "output.json"  # Input JSON file containing Kannada text
    output_file = "translated_output.json"  # Output JSON file for English translation

    # Translate Kannada text to English and save it
    translate_kannada_to_english(input_file, output_file)

if __name__ == "__main__":
    main()
