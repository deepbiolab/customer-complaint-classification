import os
from openai import AzureOpenAI
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def generate_image(prompt: str, output_dir: str = "output", sample_name: str = "") -> str:
    """
    Generates an image based on a prompt using OpenAI's DALL-E model.

    Args:
        prompt (str): The prompt to generate the image from.
        output_dir (str): Directory to save the generated image.

    Returns:
        str: The path to the generated image.
    """
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY_R2"), # we use 
        api_version=os.getenv("DALLE_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_R2")
    )

    try:
        # Call DALL-E to generate image
        response = client.images.generate(
            model=os.getenv("DALLE_DEPLOYMENT"),
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        # Get the image URL
        image_url = response.data[0].url

        # Download the image
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            raise Exception("Failed to download the image")

        # Create output subfolder
        output_subfolder = os.path.join(output_dir, sample_name)
        Path(output_subfolder).mkdir(parents=True, exist_ok=True)

        # Save the image
        image_path = os.path.join(output_subfolder, "generated_image.png")
        with open(image_path, "wb") as f:
            f.write(image_response.content)

        print(f"Image generated and saved at: {image_path}")
        return image_path

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Test prompt based on the transcription example
    test_prompt = "Create an image depicting a frustrated customer waiting for a delayed package delivery. Show a calendar with days crossed off, a tracking page on a computer screen with no updates, and a worried person checking their watch. The scene should convey a sense of urgency and disappointment."
    
    image_path = generate_image(test_prompt)
    if image_path:
        print(f"Generated image saved at: {image_path}")
    else:
        print("Failed to generate image.")