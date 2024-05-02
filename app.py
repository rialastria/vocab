import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import (
    Flask, 
    request, 
    render_template, 
    redirect, 
    url_for, 
    jsonify
) 

from pymongo import MongoClient
import requests
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]


# password = 'sparta'
# cxn_str = f'mongodb+srv://test:{password}@cluster0.atiyrt3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
# client = MongoClient(cxn_str)

# db = client.dbsparta_plus_chp8

# @app.route('/practice')
# def practice():
#     return render_template('practice.html')

@app.route('/')
def main():
    words_result = db.words.find({}, {'_id': False})
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word': word['word'],
            'definition': definition,
        })

    msg = request.args.get('msg')    
    return render_template('index.html', words=words, msg=msg)


    

@app.route('/detail/<keyword>',methods=['GET', 'POST'])
def detail(keyword):
    api_key = "2baabd95-7f94-4b54-9ee5-ae3a680c9b9a"
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    # print(keyword)
    # return render_template('detail.html', word=keyword)
    response = requests.get(url)
    definitions = response.json()
     
    if not definitions:
        return redirect(url_for(
            'eror',
            msg=f'Your word, "{keyword}", Could not find the word',
            word=keyword
          
        ))
    
    if type(definitions[0]) is str:
         suggestions = ', '.join(definitions)
         return redirect(url_for(
            'eror',
            msg=f'Your word, "{keyword}", Could not find the word',
            suggestions=suggestions,
            word=keyword
        ))


    status = request.args.get('status_give','new')
    return render_template(
        'detail.html',
        word=keyword,
        definitions=definitions,
        status=status
    )

@app.route('/eror',methods=['GET', 'POST'])
def eror():
    keyword = request.args.get('word')
    msg = request.args.get('msg')
    suggestions = request.args.get('suggestions')

    if suggestions:
        return render_template('eror.html', msg=msg, suggestions=suggestions.split(","),keyword=keyword)
    else:
        return render_template('eror.html', msg=msg, keyword=keyword)
    


@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')
    doc = {
        'word': word,
        'definitions': definitions,
        'date': datetime.now().strftime('%Y%m%d')
    }

    db.words.insert_one(doc)

    return jsonify({
        'result': 'success',
        'msg': f'the word, {word}, was saved!!!',
    })
@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word':word})
    db.examples.delete_many({'word': word})
    return jsonify({
        'result': 'success',
        'msg': f'the word, {word}, was delete',

    })

@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    word = request.args.get('word')
    example_data = db.examples.find({'word': word})
    examples = []
    for example in example_data:
        examples.append({
            'example': example.get('example'),
            'id': str(example.get('_id')),
        })

    return jsonify({
        'result': 'success',
        'examples': examples
        })

@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    word = request.form.get('word')
    example = request.form.get('example')
    doc = {
        'word': word,
        'example': example,
    }
    db.examples.insert_one(doc)

    return jsonify({
        'result': 'success',
        'msg': f'Your ex, {example},for the word, {word}, was saved!',
        
        })


@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    id = request.form.get('id')
    word = request.form.get('word')
    db.examples.delete_one({'_id': ObjectId(id)})
    

    return jsonify({
        'result': 'success',
        'msg': f'Your ex for the word, {word}, was deleted!',
        })



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)