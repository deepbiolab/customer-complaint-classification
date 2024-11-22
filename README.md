# Customer Complaint Classification Starter Project

## Overview

This starter project aims to help you learn and implement a generative AI-based solution for classifying customer complaints. The project involves various steps such as transcribing customer audio complaints, generating images, describing and annotating those images, and finally classifying the complaints into appropriate categories. By working through this project, you will get hands-on experience with multiple AI models and the practical integration of generative AI in a real-world scenario.

In addition to executing each of these steps, it is important to store the intermediate results after each stage. This will help in project evaluation and debugging, as well as allow you to understand how each step contributes to the final outcome.

1. **Transcribing Customer Audio Complaint**:

   - The first step is to convert the customer's audio complaint into text using a speech-to-text model. This involves using the `whisper.py` module.

2. **Create Prompt from Transcription**:

   - Once the audio is transcribed, a prompt is created from the transcription that will be used to generate a visual representation of the complaint.

3. **Generate Image Representing the Issue**:

   - Using the prompt created from the transcription, an image is generated to visually represent the customer complaint. This is managed by the `dalle.py` module.

4. **Describe the Generated Image**:

   - The generated image is then analyzed to provide a description of its contents, using the `vision.py` module. This helps identify the key elements related to the issue.

5. **Annotate the Reported Issue in the Image**:

   - The key reported issue in the image is highlighted through annotation, which includes identifying specific objects or areas related to the complaint.

6. **Classify Complaint into Category/Subcategory Pair**:
   - Use the generated image description and the catalog metadata to classify the complaint into a category and subcategory. This is handled by the `gpt.py` module.

***It is recommended to store the intermediate results after this step as well, to ensure that all stages of the process can be reviewed for evaluation.***

## File Structure

The project consists of the following files:

1. **`whisper.py`**:

   - This file contains a function to transcribe audio complaints into text using the Whisper model. The implementation is left incomplete for you to practice.

2. **`dalle.py`**:

   - Contains the function `generate_image()` to create an image representing the issue. The function is partially complete with guidance comments.

3. **`vision.py`**:

   - This file contains a function to describe the generated image and annotate it with the key elements identified. The implementation is incomplete to allow you to practice building it.

4. **`gpt.py`**:

   - Contains a function `classify_with_gpt()` that takes in an image description and classifies the complaint into an appropriate category/subcategory. You are required to complete the logic.

5. **`main.py`**:

   - Orchestrates the entire workflow, calling each of the modules in sequence. The workflow steps are described in comments, and you are required to implement the logic to connect each module.

## Learning Objectives

- **Hands-on with Generative AI**: You will learn to implement generative AI models for real-world tasks such as image generation and language modeling.
- **Practical Application of AI APIs**: Understand how to interact with various OpenAI APIs and apply them in a sequence to create an end-to-end solution.
- **Image Annotation and Description**: Gain experience with describing and annotating images using AI, which is useful in many computer vision applications.

## Prerequisites

- Basic understanding of Python programming.
- Familiarity with machine learning concepts and generative AI.
- Recent reading or coursework on generative AI models

## Helpful Tips

- **Start Small**: Focus on completing one function at a time. Test each module individually before integrating it into the full workflow.
- **Experiment with Prompts**: The quality of the generated image or classification can depend heavily on how the prompt is formulated. Experiment with different phrasing.
- **API Documentation**: Refer to the OpenAI API documentation as you work through the project to understand what parameters are needed for each API call.

## Resources

- [OpenAI API Documentation](https://beta.openai.com/docs/)
- [Python Documentation](https://docs.python.org/3/)
