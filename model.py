import json
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Function to process query and find relevant audio files
def find_relevant_audio_files(input_file, query, top_k=3):
    # Load the pre-trained sentence-transformers model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Load the JSON file
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract audio paths and corresponding text
    audio_paths = list(data.keys())
    sentences = list(data.values())

    # Compute sentence embeddings for the sentences and query
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Compute cosine similarity between query and sentences
    similarities = util.pytorch_cos_sim(query_embedding, sentence_embeddings)

    # Find the top_k most relevant sentences
    top_results = np.argsort(similarities[0].cpu().numpy())[::-1][:top_k]

    # Prepare the output with top results
    relevant_audio = {}
    for idx in top_results:
        relevant_audio[audio_paths[idx]] = sentences[idx]

    return relevant_audio

# Main function
def main():
    input_file = "translated_output.json"  # Input JSON file
    query = input("Enter your query: ")  # Get the query from the user

    # Find the most relevant audio files
    relevant_audio = find_relevant_audio_files(input_file, query)

    # Save the output to a JSON file
    output_file = "relevant_audio.json"
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(relevant_audio, file, ensure_ascii=False, indent=4)

    # Print relevant audio file paths and details
    print("Most Relevant Audio Files:")
    for path, text in relevant_audio.items():
        print(f"{path}: {text}")

    print(f"\nDetails saved to: {output_file}")

if __name__ == "__main__":
    main()
