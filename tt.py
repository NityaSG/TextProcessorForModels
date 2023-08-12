from flask import Flask, request, jsonify
import requests
import os
import PyPDF2
import json
import openai
from pytesseract import image_to_string

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
         },#,
        # 'email':{
        #     'type':'string',
        #     'description':'email id present of the document'
        # },
        'medic info':{
            'type':"string",
            'description':'emedically relevant information about the person. Short precise and concise medical knowldege about the person'
        },
        'summary':{
            'type':'string',
            'description':'brief summary and analysis about the report provided'
         }#,
        # 'fitness':{
        #     'type':'string',
        #     'description':'is the person fit for ml engineer role? if yes then why?'
        # }
    
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
         },#,
        # 'email':{
        #     'type':'string',
        #     'description':'email id present of the document'
        # },
        'medical_info':{
            'type':"string",
            'description':'emedically relevant information about the person. Short precise and concise medical knowldege about the person'
        },
        'summary':{
            'type':'string',
            'description':'brief summary and analysis about the report provided'
         }#,
        # 'fitness':{
        #     'type':'string',
        #     'description':'is the person fit for ml engineer role? if yes then why?'
        # }
    
    },
    "required":["name","medical_info","summary"]
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
        
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 400



if __name__ == '__main__':
    app.run(debug=True)
