'''

streamlit run qa_from_doc_ui.py --server.port 3626 --server.address 0.0.0.0

'''

import streamlit as st
import pandas as pd
from io import StringIO
import os

from document_qa import build_rag_chain_from_doc

save_folder = 'uploaded'

try:
	os.system(f"mkdir {save_folder}")
except:
	pass

rag_chain = None

st.title("AraMUS Document QA")

uploaded_file = st.file_uploader("Choose a file")

if st.button('Update the QA engine by the file'):

	try:

		save_path = os.path.join(save_folder, uploaded_file.name)
		with open(save_path, mode='wb') as w:
			w.write(uploaded_file.getvalue())

		st.session_state["rag_chain"] = build_rag_chain_from_doc(
			document_path = save_path,
			)

		message = f'Thank you for uploading {uploaded_file.name}. I have read this document and ready to answer your questions.'
		st.session_state.messages.append({"role": "assistant", "content": message})

	except Exception as e:

		message = f"Opps, error {e}"
		st.session_state.messages.append({"role": "assistant", "content": message})


if "messages" not in st.session_state:
	st.session_state["messages"] = []

for msg in st.session_state.messages[-10:]:
	st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

	st.session_state.messages.append({"role": "user", "content": prompt})
	st.chat_message("user").write(prompt)

	if "rag_chain" not in st.session_state:
		response = "Please upload your document ana update the QA engine before asking a question."
	else:
		response = st.session_state["rag_chain"].invoke(prompt)

	st.session_state.messages.append({"role": "assistant", "content": response})
	st.chat_message("assistant").write(response)