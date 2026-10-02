import time
from google import genai

client = genai.Client()


def generate_ai_response(prompt: str):
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )

            return response.text

        except Exception as e:
            if attempt == 2:
                raise e

            time.sleep(5)