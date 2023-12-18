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
    save_path = os.path.join(save_folder, data['filename']+".txt")
    try:
        with open(save_path, mode='w') as w:
            w.write(data['text'])
        if os.path.exists('./uploaded/share.txt'):
            with open('./uploaded/share.txt', mode='a') as w:
                w.write(data['text'])
        else:
            # os.system("touch ./uploaded/share.txt")
            with open('./uploaded/share.txt', mode='w') as w:
                w.write(data['text'])

        logger.info(f"Save text status: Save Success")
        logger.info(f"Save path: {save_path}")
    except Exception as e:
        logger.info(f"Save text Error: {e}")

    # try:
    rag_chain =  build_rag_chain_from_doc(save_path, data['filename'], data['text'])

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
    question = data['question']
    text_name = data['filename']
    logger.info(f"Question: {question}")

    try:
        response = answer_from_doc(text_name, question)
        logger.info(f"Question Response: {response}")
        if response == "I don't know" or "I don't know" in response:
            response = "I’m sorry I currently do not have an answer to that question, please rephrase or ask me another question." 
        return {"response": response, "status": "Success!", "running_time": float(time.time() - start)}
    except Exception as e:
        logger.info(f"Answer question Error: {e}")
        return {"response": f"Error: {e}", "status": "Fail!", "running_time": float(time.time() - start)}


#######################

if __name__=="__main__":
    app.run(port=3273, host="0.0.0.0", debug=False)