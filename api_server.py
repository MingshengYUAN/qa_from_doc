import time
import re 
import os
import requests
import logging
import argparse
import configparser
import numpy as np
from datetime import timedelta
from flask import Flask, request
from flasgger import Swagger
from flasgger.utils import swag_from
from swagger_template import template
from flask_session import *
from log_info import *
from document_qa_new import build_rag_chain_from_text, answer_from_doc

parser = argparse.ArgumentParser()
parser.add_argument('--port', default=3010)
parser.add_argument('--config_path', default='./conf/config.ini')
parser.add_argument('--log_path', default='./log/qa_from_doc.log')
args = parser.parse_args()

config_path = args.config_path
conf = configparser.ConfigParser()
conf.read(config_path, encoding='utf-8')

app = Flask(__name__)
swagger = Swagger(app, template=template)
# app.config["SESSION_PERMANENT"] = False
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
# app.config["SESSION_TYPE"] = "filesystem"
fh = logging.FileHandler(args.log_path)
fh.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(fh)


save_folder = 'uploaded'

try:
	os.system(f"mkdir {save_folder}")
except:
	pass

#####################

@app.route("/doc_input", methods=['POST'])
def doc_input():
    start = time.time()
    data = request.get_json()
    save_path = os.path.join(save_folder, data['filename']+".txt")
    try:
        with open(save_path, mode='w') as w:
            w.write(data['text'])
        logger.info(f"Save text status: Save Success")
        logger.info(f"Save path: {save_path}")
    except Exception as e:
        logger.info(f"Save text Error: {e}")

    # try:
    rag_chain =  build_rag_chain_from_text(token_name=data['filename'], text=data['text'], conf=conf)

    logger.info(f"Save chromadb status: Save Success")
    logger.info(f"Save name: {data['filename']}")
    return {"response": 'Save Success', "status": "Success!", "running_time": float(time.time() - start)}
    # except Exception as e:
    #     logger.info(f"Save chromadb Error: {e}")
    #     return {"response": "Save Error!", "status": "Fail!", "running_time": float(time.time() - start)}

###########################

@app.route("/qa_from_doc", methods=['POST'])
def qa_from_doc():
    start = time.time()
    data = request.get_json()
    print(f"data: {data}")
    new_question = data['question']
    text_name = data['filename']
    try:
        history_qa = data['messages']
    except:
        history_qa = []
    question = ''
    for i in history_qa:
        if i['role'] == 'user':
            question += i['content'] + '\n'
    question += new_question
    logger.info(f"Question: {question}")

    # try:
    response, fragment, score, document_name = answer_from_doc(text_name, question, conf)
    logger.info(f"Question Response: {response}")
    if response == "I don't know" or "I don't know" in response:
        response = "I’m sorry I currently do not have an answer to that question, please rephrase or ask me another question." 
        score = 0.0
    return {"response": response, "fragment": fragment, "score":score, "document_name": document_name , "status": "Success!", "running_time": float(time.time() - start)}
    # except Exception as e:
    #     logger.info(f"Answer question Error: {e}")
    #     return {"response": f"Error: {e}", "fragment": "", "status": "Fail!", "running_time": float(time.time() - start)}


#######################
if __name__=="__main__":
    app.run(port=args.port, host="0.0.0.0", debug=False)