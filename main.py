import os
import json
import time
import logging
from pathlib import Path
from whisper import transcribe_audio
from dalle import generate_image
from vision import describe_image
from gpt import classify_with_gpt

# Configure logging
def setup_logging(output_dir: str):
    """
    Set up logging configuration
    """
    log_file = os.path.join(output_dir, 'output.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also print to console
        ]
    )

def create_prompt(transcription: str) -> str:
    """
    Create a prompt for image generation based on the transcription.
    """
    return (
        f"Create a simple, clear image focusing only on the following customer complaint scenario: {transcription}, "
        "Show only the essential items and issues mentioned. "
        "Do not add unnecessary details or background elements. "
        "The image should clearly illustrate the specific problem(s) described."
    )

def save_predictions(predictions):
    """
    Save predictions to a JSON file.
    """
    predictions_file = "prediction.json"
    with open(predictions_file, 'w') as f:
        json.dump({"complaints": predictions}, f, indent=2)
    logging.info(f"Predictions saved to {predictions_file}")

def calculate_accuracy(predictions, labels):
    """
    Calculate accuracy by comparing predictions with labels.
    First match predictions and labels by ID, then compare categories.
    """
    correct = 0
    total = 0
    
    # Create dictionaries with ID as key for faster lookup
    pred_dict = {p['id']: p for p in predictions}
    label_dict = {l['id']: l for l in labels}
    
    # Find matching IDs
    matching_ids = set(pred_dict.keys()) & set(label_dict.keys())
    total = len(matching_ids)
    
    # Compare only matching samples
    for id in matching_ids:
        pred = pred_dict[id]
        label = label_dict[id]
        if pred['category'] == label['category'] and pred['subcategory'] == label['subcategory']:
            correct += 1
            
    return correct / total if total > 0 else 0

def main():
    """
    Orchestrates the workflow for handling customer complaints.
    """
    audio_dir = "audio"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up logging
    setup_logging(output_dir)
    logging.info("Starting complaint processing workflow")
    
    predictions = []

    # Process all audio files in the audio directory
    for audio_file in sorted(os.listdir(audio_dir)):
        if audio_file.endswith(('.mp3', '.wav')):
            audio_path = os.path.join(audio_dir, audio_file)
            sample_name = Path(audio_path).stem
            logging.info(f"Processing: {audio_file}")

            try:
                # 1. Transcribe the audio complaint
                transcription = transcribe_audio(audio_path, output_dir)
                logging.info("Transcription completed")

                # 2. Create a prompt from the transcription
                prompt = create_prompt(transcription)
                logging.info("Prompt created")

                # 3. Generate an image based on the prompt
                max_retries = 3
                retry_delay = 5  # seconds
                for attempt in range(max_retries):
                    image_path = generate_image(prompt, output_dir, sample_name)
                    if image_path is not None:
                        logging.info(f"Image generated successfully on attempt {attempt + 1}")
                        break
                    else:
                        if attempt < max_retries - 1:
                            logging.warning(f"Image generation failed. Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                        else:
                            raise Exception(f"Image generation failed after {max_retries} attempts")

                if image_path is None:
                    raise Exception("Image generation failed")

                # 4. Describe and annotate the generated image
                image_description, annotated_image_path = describe_image(image_path, transcription, output_dir, sample_name)
                logging.info("Image described and annotated")

                # 5. Classify the complaint based on the image description and transcription
                classification = classify_with_gpt(transcription, image_description, output_dir, sample_name)
                logging.info("Complaint classified")

                # Add prediction to the list
                predictions.append({
                    "id": sample_name,
                    "category": classification['category'],
                    "subcategory": classification['subcategory']
                })

                # Log results
                logging.info("\nResults Summary:")
                logging.info(f"Transcription (excerpt): {transcription[:100]}...")
                logging.info(f"Generated Image: {image_path}")
                logging.info(f"Annotated Image: {annotated_image_path}")
                logging.info(f"Classification: {classification}")
                logging.info("="*50)

            except Exception as e:
                logging.error(f"Error processing {audio_file}: {str(e)}")

    # Save predictions
    save_predictions(predictions)

    # Calculate accuracy
    labels_file = 'labels.json'
    if os.path.exists(labels_file):
        try:
            with open(labels_file, 'r') as f:
                labels = json.load(f)['complaints']
            accuracy = calculate_accuracy(predictions, labels)
            logging.info(f"Accuracy: {accuracy:.2%}")
        except Exception as e:
            logging.error(f"Error calculating accuracy: {str(e)}")
    else:
        logging.warning(f"Labels file '{labels_file}' not found. Skipping accuracy calculation.")

    logging.info("Processing completed for all audio files")

if __name__ == "__main__":
    main()