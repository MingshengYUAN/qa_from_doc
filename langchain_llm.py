from typing import Any, List, Mapping, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
import requests

class CustomLLM(LLM):
	n: int
	@property
	def _llm_type(self) -> str:
		return "custom"
	def _call(
		self,
		prompt: str,
		stop: Optional[List[str]] = None,
		run_manager: Optional[CallbackManagerForLLMRun] = None,
		**kwargs: Any,
	) -> str:
		if stop is not None:
			raise ValueError("stop kwargs are not permitted.")
		response = requests.post(
			# 'http://37.224.68.132:24267/tonomus_llm/mistral_7b_instruct_generate',
			'http://37.224.68.132:27090/generate',
			json = {"prompt":prompt, "stream": False, "max_tokens":1024, "temperature":0}
			).json()["response"][0]
		return response
	@property
	def _identifying_params(self) -> Mapping[str, Any]:
		"""Get the identifying parameters."""
		return {"n": self.n}


