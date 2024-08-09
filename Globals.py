from openai import OpenAI
from Prompter import Prompter

prompter = Prompter()
open_ai_client = OpenAI()
solved = False
thought_id = 1
current_request_cost = 0.0

workers = []
execution_logs = ""
