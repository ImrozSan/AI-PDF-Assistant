import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


def ask_ai(context, question):

    prompt = f"""
You are an AI PDF Assistant.

Answer ONLY using the PDF content.

If the answer is not found in the PDF, reply:
"I couldn't find that information in the uploaded PDF."

PDF:
{context[:3000]}

Question:
{question}
"""

    payload = {
        "model": "openai/gpt-oss-20b:fireworks-ai",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.3
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        message = data["choices"][0]["message"]
        print(data)

        content = message.get("content")

        if content:
            return content

        reasoning = message.get("reasoning_content")

        if reasoning:
            return reasoning

        return "❌ No answer was returned by the AI."

    except Exception as e:
        return f"❌ Error: {e}"