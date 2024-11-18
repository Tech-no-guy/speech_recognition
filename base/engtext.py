from googletrans import Translator

# Function to translate Kannada text to English
def translate_kannada_to_english(input_file, output_file):
    # Initialize the Translator
    translator = Translator()

    # Read Kannada text from the input file
    with open(input_file, 'r', encoding='utf-8') as file:
        kannada_text = file.read()

    # Translate the text
    translated = translator.translate(kannada_text, src='kn', dest='en')

    # Save the translated English text to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(translated.text)

    print(f"Translation completed. Translated text saved to: {output_file}")

def main():
    input_file = "kannada_transcription.txt"  # Input file containing Kannada text
    output_file = "translated_text.txt"  # Output file for English translation

    # Translate Kannada text to English and save it
    translate_kannada_to_english(input_file, output_file)

if __name__ == "__main__":
    main()
