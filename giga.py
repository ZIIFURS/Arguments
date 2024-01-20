import requests
def rewr(text):
    url = 'https://api.aicloud.sbercloud.ru/public/v2/rewriter/predict'

    data = {
        "instances": [
            {
                "text": text[:1000],
                "temperature": 0.5,
                "top_k": 50,
                "top_p": 0.7,
                "range_mode": "bertscore"
            }
        ]
    }

    response = requests.post(url=url, json=data)

    return response.json()['prediction_best']['bertscore']


def summ(text):
    url = 'https://api.aicloud.sbercloud.ru/public/v2/summarizator/predict'

    data = {
        "instances": [
            {
                "text": text[:1000],
                "num_beams": 8,
                "num_return_sequences": 3,
                "length_penalty": 0.5
            }
        ]
    }

    response = requests.post(url=url, json=data)

    return response.json()['prediction_best']['bertscore']
