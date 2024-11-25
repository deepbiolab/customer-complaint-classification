import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import base64
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def describe_image(image_path: str, transcription: str, output_dir: str = "output", sample_name: str = "") -> tuple:
    """
    Describes an image, identifies key visual elements related to the customer complaint,
    and annotates the image with these elements.

    Args:
        image_path (str): Path to the image file to analyze
        transcription (str): The transcription of the customer complaint
        output_dir (str): Directory to save output files

    Returns:
        tuple: (description, annotated_image_path)
    """
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("GPT_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    try:
        # Encode the image
        base64_image = encode_image(image_path)

        # Prepare the messages for the API call
        messages = [
            {
                "role": "system",
                "content": "You are a visual analysis expert specializing in customer complaint scenarios. Analyze the image in detail, focusing on elements that directly relate to the customer's complaint. Identify key objects, expressions, or situations that illustrate the specific issues mentioned in the complaint. For each key element, provide its approximate location in the image as [x, y] coordinates, where [0, 0] is the top-left corner and [1, 1] is the bottom-right corner."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}"
                    },
                    {
                        "type": "text",
                        "text": f"Analyze this image in detail, focusing on key issues mentioned by customer related to the following customer complaint: {transcription}\n\nIdentify and locate key objects or situations that specifically illustrate the complaint."
                    }
                ]
            }
        ]

        # Call the GPT-4 Vision model
        response = client.chat.completions.create(
            model=os.getenv("GPT_DEPLOYMENT"),
            messages=messages,
            max_tokens=500
        )

        # Extract the description
        description = response.choices[0].message.content

        # Save description to file
        os.makedirs(output_dir, exist_ok=True)
        # Create output subfolder
        output_subfolder = os.path.join(output_dir, sample_name)
        Path(output_subfolder).mkdir(parents=True, exist_ok=True)

        # Save description to file
        description_path = os.path.join(output_subfolder, "image_description.txt")
        with open(description_path, "w") as f:
            f.write(description)

        # Annotate the image
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        # Use a smaller font size
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except IOError:
            font = ImageFont.load_default().font_variant(size=14)

        # Parse the description to find key elements and their locations
        lines = description.split('\n')
        for line in lines:
            if '[' in line and ']' in line:
                try:
                    element = line.split(':')[0].strip()
                    element = element.replace('*', '').split('[')[0].strip()
                    coords = eval(line.split('[')[1].split(']')[0])
                    x, y = int(coords[0] * img.width), int(coords[1] * img.height)
                    
                    # Draw a semi-transparent background for text
                    text_bbox = draw.textbbox((x, y), element, font=font)
                    draw.rectangle(text_bbox, fill=(255, 255, 255, 180))
                    
                    # Draw text
                    draw.text((x, y), element, fill="red", font=font)
                    
                    # Draw a more visible marker
                    marker_size = 6
                    draw.ellipse([x-marker_size, y-marker_size, x+marker_size, y+marker_size], 
                                outline="red", width=2)
                except:
                    continue

        # Save annotated image
        annotated_image_path = os.path.join(output_subfolder, "annotated_image.png")
        img.save(annotated_image_path)

        return description, annotated_image_path

    except Exception as e:
        raise Exception(f"Error analyzing and annotating image: {str(e)}")


# Example Usage (for testing purposes)
if __name__ == "__main__":
    test_image = "output/generated_image.png"  # Replace with your test image path
    test_transcription = """I purchased a smartwatch from your store, but it's not syncing properly with my phone. The app keeps crashing, and the watch doesn't track my steps accurately. I've already tried resetting it multiple times, but the issue persists. I need a replacement or a full refund."""
    
    try:
        if os.path.exists(test_image):
            description, annotated_image_path = describe_image(test_image, test_transcription)
            print("Image Description:")
            print(description)
            print(f"Annotated image saved at: {annotated_image_path}")
        else:
            print(f"Test image not found: {test_image}")
    except Exception as e:
        print(f"Error: {str(e)}")