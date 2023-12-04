import time
from log_info import logger
import numpy as np
import requests
import re 
from flask import Flask, request
from flasgger import Swagger
from flasgger.utils import swag_from
import os
from document_qa import build_rag_chain_from_doc, answer_from_doc
from swagger_template import template
from flask_session import *
from datetime import timedelta

#############

app = Flask(__name__)
swagger = Swagger(app, template=template)

# app.config["SESSION_PERMANENT"] = False
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
# app.config["SESSION_TYPE"] = "filesystem"

save_folder = 'uploaded'

try:
	os.system(f"mkdir {save_folder}")
except:
	pass

rag_chain = None

#####################

@app.route("/doc_input", methods=['POST'])
def doc_input():
    start = time.time()
    data = request.get_json()
    # print(data['text'])
    save_path = os.path.join(save_folder, data['text_name']+".txt")
    try:
        with open(save_path, mode='w') as w:
            w.write(data['text'])
        logger.info(f"Save text status: Save Success")
        logger.info(f"Save path: {save_path}")
    except Exception as e:
        logger.info(f"Save text Error: {e}")

    try:
        rag_chain =  build_rag_chain_from_doc(save_path, data['text_name'])

        logger.info(f"Save chromadb status: Save Success")
        logger.info(f"Save name: {data['text_name']}")
        return {"save_response": 'Save Success', "use_time": float(time.time() - start)}
    except Exception as e:
        logger.info(f"Save chromadb Error: {e}")
        return {"save_response": "Save Error!", "use_time": float(time.time() - start)}

###########################

@app.route("/qa_from_doc", methods=['POST'])
def qa_from_doc():
    start = time.time()
    data = request.get_json()
    question = data['question']
    text_name = data['text_name']
    try:
        response = answer_from_doc(text_name, question)
        logger.info(f"Question Response: {response}")
        return {"response": response, "use_time": float(time.time() - start)}
    except Exception as e:
        logger.info(f"Answer question Error: {e}")
        return {"response": f"Error: {e}", "use_time": float(time.time() - start)}


#######################

if __name__=="__main__":
    app.run(port=3273, host="0.0.0.0", debug=False)













