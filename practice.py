import requests

api_key ='2baabd95-7f94-4b54-9ee5-ae3a680c9b9a'
word = 'potato'
url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}'

res = requests.get(url)

definitions = res.json()

for definition in definitions:
    print(definition)