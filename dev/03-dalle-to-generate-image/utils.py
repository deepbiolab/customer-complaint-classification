from openai import AzureOpenAI
import os
import json
import base64
from mimetypes import guess_type


def create_openai_client(api_version, api_key, api_endpoint):
    client = AzureOpenAI(
        api_version=api_version,
        api_key=api_key,
        azure_endpoint=api_endpoint
    )
    return client


def local_image_to_data_url(image_path):
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(
            image_file.read()).decode('utf-8')
    return f"data:{mime_type};base64,{base64_encoded_data}"


def describe_local_image(client, image_path, deployment_name, prompt):
    data_url = local_image_to_data_url(image_path)

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
            }
        ],
        max_tokens=1024
    )
    return response.choices[0].message.content


def describe_online_image(client, image_url, deployment_name, prompt):
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        max_tokens=1024
    )
    return response.choices[0].message.content


def generate_image(client, prompt, model, size,
                   quality,
                   style):
    result = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        style=style
    )

    json_response = json.loads(result.model_dump_json())
    image_url = json_response["data"][0]["url"]

    return image_url
