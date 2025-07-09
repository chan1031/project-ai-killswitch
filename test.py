from utils import run_local_llm
from ollama import Client

#local llm
web_use = True
navi_use = True
llm = "llama3:70b"
client = Client(host="http://localhost:11434")

initial_question = "You are a helpful agnets.Search Cornell University computer science professor's name, email and research area. Select proper tool to use."
subsequent_questions = []

final_response, final_responses, messages = run_local_llm(client, initial_question, subsequent_questions, llm=llm, web=web_use, navigation=navi_use, T=0.7)

print(final_response)