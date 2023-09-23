from flask import Flask, request, jsonify
import requests
import os
import PyPDF2
import json
import openai
from pytesseract import image_to_string
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)

@app.route('/parse_pdf', methods=['POST'])
def parse_pdf():
    def extract_text_from_pdf(pdf_url):
        response = requests.get(pdf_url)
        response.raise_for_status()  # Raise an exception for unsuccessful responses (4xx, 5xx)

        with open('temp.pdf', 'wb') as file:
            file.write(response.content)

        text = ''
        with open('temp.pdf', 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()

        # Remove the temporary file
        os.remove('temp.pdf')

        return text
    
    def extract_info(text):
        funsions=[
    {
    'name':'extractinfo',
    'description':'extracts important information from the given text',
    'parameters':{
        'type':'object',
        'properties':{
            'name':{
                'type':'string',
            'description':'name of the report'
         },
        'medic info':{
            'type':"string",
            'description':'emedically relevant information about the person. Short precise and concise medical knowldege about the person'
        },
        'summary':{
            'type':'string',
            'description':'brief summary and analysis about the report provided'
         }
    
    }
    }
    }
]
        openai_response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo-0613',
        messages = [{'role': 'user', 'content': text}],
        functions = funsions,
        function_call = 'auto'
        )
        json_str = json.dumps(openai_response)
        json_obj = json.loads(json_str)
        arguments = json_obj['choices'][0]['message']['function_call']['arguments']
        return arguments



    data = request.get_json()

    if not data or not isinstance(data, list):
        return jsonify({'error': 'Invalid JSON format. Expecting a list of dictionaries.'}), 400

    if len(data) == 0 or 'pdf_url' not in data[0]:
        return jsonify({'error': 'PDF URL not provided in the request'}), 400

    pdf_url = data[0]['pdf_url']

    try:
        text = extract_text_from_pdf(pdf_url)
        text=extract_info(text)
        
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/parse_text', methods=['POST'])
def parse_img():
    
    def extract_info(text):
        funsions=[
    {
    'name':'extractinfo',
    'description':'extracts important information from the given text',
    'parameters':{
        'type':'object',
        'properties':{
            'name':{
                'type':'string',
            'description':'name of the report'
         },
        'medical_info':{
            'type':"string",
            'description':'Short summary of the report. retaining only useful informations like symptoms and reason. keep it extremely short'
        },
        'symptoms':{
             'type':'string',
             'description':'list of potential symptoms'
          }
    
    },
    "required":["name","medical_info","symptoms"]
    }
    }
]
        openai_response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo-0613',
        messages = [{'role': 'user', 'content': text}],
        functions = funsions,
        function_call = 'auto'
        )
        json_str = json.dumps(openai_response)
        json_obj = json.loads(json_str)
        arguments = json_obj['choices'][0]['message']['function_call']['arguments']
        return arguments



    data = request.get_json()

    if not data or not isinstance(data, list):
        return jsonify({'error': 'Invalid JSON format. Expecting a list of dictionaries.'}), 400

    if len(data) == 0 or 'info' not in data[0]:
        return jsonify({'error': 'PDF URL not provided in the request'}), 400

    text = data[0]['info']

    try:
        text=extract_info(text)
        output_json = json.loads(text)
        return jsonify(output_json)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/ayurved', methods=['POST'])
def ayurved():
    def extract_info(text):
        funsions=[
    {
    'name':'extractinfo',
    'description':'Returns informations about the given ayurvedic medicine',
    'parameters':{
        'type':'object',
        'properties':{
            'info':{
                'type':'string',
            'description':'Description of the given medicine'
        },
        'adv':{
            'type':'string',
            'description':'Advantages of the medicine'
        },
        'disadv':{
            'type':"string",
            'description':'disadvantage of the medicine'
        },
        'products':{
            'type':'string',
            'description':'name and links of medicine products from https://www.patanjaliayurved.net/'
        }

    }
    }
    }
]
        openai_response = openai.ChatCompletion.create(
        model = 'gpt-4-0613',
        messages = [{'role': 'user', 'content': text}],
        functions = funsions,
        function_call = 'auto'
        )
        json_str = json.dumps(openai_response)
        json_obj = json.loads(json_str)
        arguments = json_obj['choices'][0]['message']['function_call']['arguments']
        return arguments



    data = request.get_json()

    if not data or not isinstance(data, list):
        return jsonify({'error': 'Invalid JSON format. Expecting a list of dictionaries.'}), 400

    if len(data) == 0 or 'pdf_url' not in data[0]:
        return jsonify({'error': 'PDF URL not provided in the request'}), 400

    text = data[0]['pdf_url']

    try:
        text=extract_info(text)
        
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 400



if __name__ == '__main__':
    app.run(debug=True)
