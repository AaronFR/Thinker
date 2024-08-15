from openai import OpenAI

open_ai_client = OpenAI()
is_solved = False
current_thought_id = 1
current_request_cost = 0.0

workers = []
