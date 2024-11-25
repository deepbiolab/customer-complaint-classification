import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def load_categories(json_path: str = "categories.json") -> dict:
    """
    Load categories and subcategories from JSON file.
    
    Args:
        json_path (str): Path to the categories JSON file
        
    Returns:
        dict: Categories and their subcategories
    """
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading categories: {str(e)}")

def format_categories(categories: dict) -> str:
    """
    Format categories dictionary into a string for the prompt.
    
    Args:
        categories (dict): Categories and subcategories
        
    Returns:
        str: Formatted string of categories
    """
    formatted = "Available categories and subcategories:\n\n"
    for category, subcategories in categories.items():
        formatted += f"{category}:\n"
        for sub in subcategories:
            formatted += f"- {sub}\n"
        formatted += "\n"
    return formatted

def classify_with_gpt(transcription: str, image_description: str, output_dir: str = "output", sample_name: str = "") -> dict:
    """
    Classify customer complaint into appropriate category/subcategory using GPT.
    
    Args:
        transcription (str): Customer complaint transcription
        image_description (str): Description of the generated image
        output_dir (str): Directory to save classification results
        
    Returns:
        dict: Classification results including category, subcategory, and confidence
    """
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("GPT_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    try:
        # Load categories
        categories = load_categories()
        categories_format = format_categories(categories)

        # Prepare the prompt
        prompt = f"""As an AI complaint classification expert, analyze the following customer complaint and image description to determine the most appropriate category and subcategory.

                    Customer Complaint Transcription:
                    {transcription}

                    Image Description:
                    {image_description}

                    {categories_format}

                    Please classify this complaint into the most appropriate category and subcategory from the provided list. Provide your response in the following JSON format:
                    {{
                        "category": "selected main category",
                        "subcategory": "selected subcategory",
                        "confidence": "high/medium/low",
                        "reasoning": "brief explanation of classification decision"
                    }}
                """

        # Call GPT model for classification
        response = client.chat.completions.create(
            model=os.getenv("GPT_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are an expert in classifying customer complaints."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent results
            response_format={ "type": "json_object" }
        )

        # Parse the response
        classification = json.loads(response.choices[0].message.content)

        # Validate classification against available categories
        if (classification['category'] in categories and 
            classification['subcategory'] in categories[classification['category']]):
            
            # Save classification to text file (changed from .json to .txt)
            os.makedirs(output_dir, exist_ok=True)
            
            # Create output subfolder
            output_subfolder = os.path.join(output_dir, sample_name)
            Path(output_subfolder).mkdir(parents=True, exist_ok=True)

            # Save classification to text file
            output_path = os.path.join(output_subfolder, "classification.txt")
            
            
            # Format the classification results as text
            classification_text = (
                f"Category: {classification['category']}\n"
                f"Subcategory: {classification['subcategory']}\n"
                f"Confidence: {classification['confidence']}\n"
                f"Reasoning: {classification['reasoning']}\n"
            )
            
            # Write to text file
            with open(output_path, 'w') as f:
                f.write(classification_text)

            return classification
        else:
            raise ValueError("Classification does not match available categories")

    except Exception as e:
        raise Exception(f"Error in classification: {str(e)}")

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Test data
    test_transcription = """I placed an order two weeks ago, and it still hasn't arrived. 
    The estimated delivery time was 5 days, but now it's way overdue. I need this item urgently, 
    and there's been no update from your side."""
    
    test_image_description = """The image shows a frustrated customer checking their wristwatch 
    and looking at delivery tracking information on multiple electronic devices. A delivery truck 
    icon is visible on the screen, indicating a delayed shipment."""
    
    try:
        classification = classify_with_gpt(test_transcription, test_image_description)
        print("\nClassification Results:")
        print(json.dumps(classification, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")