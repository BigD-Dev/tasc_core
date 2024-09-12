import openai
import os
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

    def generate_completion(self, prompt: str, model: str = "gpt-4", temperature: float = 0.7):
        """
        Sends a chat completion request to the OpenAI API.

        :param prompt: The prompt text to send to the model.
        :param model: The model to use (default: "gpt-4").
        :param temperature: Sampling temperature (default: 0.7).
        :return: The completion text.
        """
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=150
        )
        return response.choices[0].message['content'].strip()

    def generate_streaming_completion(self, prompt: str, model: str = "gpt-4"):
        """
        Sends a completion request to the OpenAI API with streaming response.

        :param prompt: The prompt text to send to the model.
        :param model: The model to use (default: "gpt-4").
        :return: Generator that streams the completion text.
        """
        stream = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in stream:
            if 'content' in chunk.choices[0].delta:
                yield chunk.choices[0].delta['content']

# Example Usage
if __name__ == "__main__":
    # Load API key from environment variables or any secure storage
    api_key = os.getenv("OPENAI_API_KEY")
    organization_id = os.getenv("OPENAI_ORG_ID")  # Optional: specify your organization ID
    project_id = os.getenv("OPENAI_ORG_ID")  # Optional: specify your project ID

    # Initialize OpenAI client
    client = OpenAIClient(api_key, organization_id, project_id)

    # Regular completion
    prompt = "What is the meaning of life?"
    result = client.generate_completion(prompt)
    print(f"Completion: {result}")

    # Streaming completion
    print("Streaming completion:")
    for content in client.generate_streaming_completion("Describe the solar system."):
        print(content, end="")