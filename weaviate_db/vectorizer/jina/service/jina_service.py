import requests
from dotenv import load_dotenv, find_dotenv
from common_utils import get_env_key

_ = load_dotenv(find_dotenv())  # read local .env file

JINA_EMBEDDINGS_URL = get_env_key('JINA_EMBEDDINGS_URL')
JINA_EMBEDDINGS_BEARER_TOKEN = get_env_key('JINA_EMBEDDINGS_BEARER_TOKEN')


# text_list = [
#             "Organic skincare for sensitive skin with aloe vera and chamomile: Imagine the soothing embrace of nature with our organic skincare range, crafted specifically for sensitive skin. Infused with the calming properties of aloe vera and chamomile, each product provides gentle nourishment and protection. Say goodbye to irritation and hello to a glowing, healthy complexion.", # noqa : E501
#             "Bio-Hautpflege für empfindliche Haut mit Aloe Vera und Kamille: Erleben Sie die wohltuende Wirkung unserer Bio-Hautpflege, speziell für empfindliche Haut entwickelt. Mit den beruhigenden Eigenschaften von Aloe Vera und Kamille pflegen und schützen unsere Produkte Ihre Haut auf natürliche Weise. Verabschieden Sie sich von Hautirritationen und genießen Sie einen strahlenden Teint.", # noqa : E501
#             "Cuidado de la piel orgánico para piel sensible con aloe vera y manzanilla: Descubre el poder de la naturaleza con nuestra línea de cuidado de la piel orgánico, diseñada especialmente para pieles sensibles. Enriquecidos con aloe vera y manzanilla, estos productos ofrecen una hidratación y protección suave. Despídete de las irritaciones y saluda a una piel radiante y saludable.", # noqa : E501
#             "针对敏感肌专门设计的天然有机护肤产品：体验由芦荟和洋甘菊提取物带来的自然呵护。我们的护肤产品特别为敏感肌设计，温和滋润，保护您的肌肤不受刺激。让您的肌肤告别不适，迎来健康光彩。",
#             "新しいメイクのトレンドは鮮やかな色と革新的な技術に焦点を当てています: 今シーズンのメイクアップトレンドは、大胆な色彩と革新的な技術に注目しています。ネオンアイライナーからホログラフィックハイライターまで、クリエイティビティを解き放ち、毎回ユニークなルックを演出しましょう。" # noqa : E501
#         ]

def jina_text_to_vector(text_list):
    url = JINA_EMBEDDINGS_URL

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JINA_EMBEDDINGS_BEARER_TOKEN}'
    }

    data = {
        "model": "jina-embeddings-v3",
        "task": "text-matching",
        "dimensions": 1024,
        "late_chunking": False,
        "embedding_type": "float",
        "input": text_list
    }

    response = requests.post(url, headers=headers, json=data)
    # print(response.json())
    return response.json()
