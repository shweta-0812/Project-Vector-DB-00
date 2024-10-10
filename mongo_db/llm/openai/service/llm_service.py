import openai
from common_utils import get_env_key

OPENAI_API_KEY = get_env_key('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY


def generate_llm_response(query: str, context: str):
    """Generate system response using OpenAI's completion"""
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a airbnb listing recommendation system."},
            {
                "role": "user",
                "content": f"Answer this user query: {query} with the following context:\n{context}"
            }
        ]
    )

    system_response = completion.choices[0].message.content

    # Print User Question, System Response, and Source Information
    print(f"- User Question:\n{query}\n")
    print(f"- System Response:\n{system_response}\n")

    # Return structured response and source info as a string
    return system_response
