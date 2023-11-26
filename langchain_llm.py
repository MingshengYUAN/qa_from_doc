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
			'http://37.224.68.132:24267/tonomus_llm/mistral_7b_instruct_generate',
			json = {"prompt":prompt}
			).json()["response"]
		return response
	@property
	def _identifying_params(self) -> Mapping[str, Any]:
		"""Get the identifying parameters."""
		return {"n": self.n}


