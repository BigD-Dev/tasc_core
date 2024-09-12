import openai
import os
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

class OpenAIClient:
    def __init__(self, api_key: str, organization_id: str = None, project_id: str = None):
        """
        Initializes the OpenAI client with the given API key, organization, and project.

        :param api_key: The API key for OpenAI.
        :param organization_id: The organization ID (optional).
        :param project_id: The project ID (optional).
        """
        openai.api_key = api_key
        if organization_id:
            openai.organization = organization_id
        if project_id:
            openai.project = project_id

    def generate_completion(self, prompt: str, model: str = "gpt-4", temperature: float = 0.7, chat_history: list = None):
        """
        Sends a chat completion request to the OpenAI API.

        :param prompt: The prompt text to send to the model.
        :param model: The model to use (default: "gpt-4").
        :param temperature: Sampling temperature (default: 0.7).
        :param chat_history: List of dictionaries representing the chat history (optional).
        :return: The completion text.
        """
        messages = chat_history if chat_history else []
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=150
        )
        return response.choices[0].message['content'].strip()

    def generate_streaming_completion(self, prompt: str, model: str = "gpt-4", chat_history: list = None):
        """
        Sends a completion request to the OpenAI API with streaming response.

        :param prompt: The prompt text to send to the model.
        :param model: The model to use (default: "gpt-4").
        :param chat_history: List of dictionaries representing the chat history (optional).
        :return: Generator that streams the completion text.
        """
        messages = chat_history if chat_history else []
        messages.append({"role": "user", "content": prompt})

        stream = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            if 'content' in chunk.choices[0].delta:
                yield chunk.choices[0].delta['content']

    def generate_image_prompt(self, image_url: str, prompt: str, model: str = "gpt-4", temperature: float = 0.7):
        """
        Fetches an image from a URL and generates a prompt based on the image.

        :param image_url: The URL of the image.
        :param prompt: The prompt text to send to the model.
        :param model: The model to use (default: "gpt-4").
        :param temperature: Sampling temperature (default: 0.7).
        :return: The completion text.
        """
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))

        # Here you can add any image processing if needed

        # Convert image to a format that can be sent to OpenAI (e.g., base64)
        # For simplicity, we assume the image is already in a suitable format

        # Generate prompt based on the image
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=150
        )
        return response.choices[0].message['content'].strip()

# Example Usage
if __name__ == "__main__":
    # Load API key from environment variables or any secure storage
    api_key = os.getenv("OPENAI_API_KEY")
    organization_id = os.getenv("OPENAI_ORG_ID")  # Optional: specify your organization ID
    project_id = os.getenv("OPENAI_PROJECT_ID")  # Optional: specify your project ID

    # Initialize OpenAI client
    client = OpenAIClient(api_key, organization_id, project_id)

    # # Example without chat history
    # prompt = "What is the meaning of life?"
    # result = client.generate_completion(prompt)
    # print(f"Completion without chat history: {result}")

    # Example with chat history
    # chat_history = [
    #     {"role": "system", "content": "You are a helpful assistant."},
    #     {"role": "user", "content": "Who won the world series in 2020?"},
    #     {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."}
    # ]
    # result_with_history = client.generate_completion(prompt, chat_history=chat_history)
    # print(f"Completion with chat history: {result_with_history}")

    # Example of generating a prompt based on an image
    image_url = "https://cdn.shopify.com/s/files/1/0327/7452/0971/files/IMG_1949.jpg?v=1725126033"
    image_prompt = "Give me the primary, secondary and tietary pixel colour in the image"
    image_result = client.generate_image_prompt(image_url, image_prompt)
    print(f"Image prompt result: {image_result}")