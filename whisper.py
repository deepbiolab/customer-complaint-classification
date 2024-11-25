import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

def transcribe_audio(audio_path: str, output_dir: str = "output") -> str:
    """
    Transcribes a single audio file using OpenAI's Whisper model and saves the transcription.
    
    Args:
        audio_path (str): Path to the audio file to transcribe
        output_dir (str): Directory to save the transcription file
        
    Returns:
        str: The transcribed text
        
    Raises:
        Exception: If transcription fails
    """
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("WHISPER_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    
    try:
        # Open and transcribe audio file
        with open(audio_path, "rb") as audio:
            # Call Whisper API
            response = client.audio.transcriptions.create(
                model=os.getenv("WHISPER_DEPLOYMENT"),
                file=audio,
                response_format="text"
            )
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate output file name
        output_filename = "transcription.txt"
        # Generate output file name and create subfolder based on sample name
        sample_name = Path(audio_path).stem
        output_subfolder = os.path.join(output_dir, sample_name)
        Path(output_subfolder).mkdir(parents=True, exist_ok=True)
        output_filename = "transcription.txt"
        output_path = os.path.join(output_subfolder, output_filename)
        
        # Save transcription to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response)
        
        print(f"Transcription saved to: {output_path}")
        
        return response
            
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Test with a single audio file
    test_file = "audio/sample1.mp3"  # Replace with your test file
    try:
        if os.path.exists(test_file):
            transcription = transcribe_audio(test_file)
            print(f"Transcription: {transcription[:200]}...")  # Print first 200 chars
        else:
            print(f"Test file not found: {test_file}")
    except Exception as e:
        print(f"Error: {str(e)}")