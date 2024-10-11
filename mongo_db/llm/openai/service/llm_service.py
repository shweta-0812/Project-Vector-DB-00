from pprint import pprint
import openai
import json
from llmlingua import PromptCompressor
from common_utils import get_env_key

OPENAI_API_KEY = get_env_key('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

llm_lingua = PromptCompressor(
    model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
    model_config={"revision": "main"},
    use_llmlingua2=True,
    device_map="cpu",  # run on CPU
)


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


def compress_query_prompt(query: str):
    demonstration_str = query['demonstration_str']
    instruction = query['instruction']
    question = query['question']

    # 6x Compression
    compressed_prompt = llm_lingua.compress_prompt(
        demonstration_str.split("\n"),
        instruction=instruction,
        question=question,
        target_token=500,
        rank_method="longllmlingua",
        context_budget="+100",
        dynamic_context_compression_ratio=0.4,
        reorder_context="sort",
    )

    return json.dumps(compressed_prompt, indent=4)


def get_compressed_context_for_query(query: str, context: str):
    # Prepare information for compression
    query_info = {
        'demonstration_str': context,  # Results from information retrieval process
        'instruction': "Write a high-quality answer for the given question using only the provided search results.",
        'question': query  # User query
    }

    # Compress the query prompt using predefined function
    compressed_prompt = compress_query_prompt(query_info)

    # Optional: Print compressed prompts for debugging
    print("Compressed Prompt:\n")
    pprint(compressed_prompt)
    print("\n" + "=" * 80 + "\n")

    return compressed_prompt
