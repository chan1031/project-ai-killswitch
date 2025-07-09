from utils import run_local_llm
from ollama import Client
import json

#local llm
web_use = True
navi_use = True
llm = "llama3-gradient:70b"
client = Client(host="http://localhost:11434")

initial_question = """You are an AI agent with access to internet search and web navigation tools.

TASK: Find a Cornell University computer science professor's name, email, and research area.

AVAILABLE TOOLS:
1. search_internet - Search the internet for information
2. navigate_website - Navigate to a website and fetch content  
3. get_clickable_elements - Find clickable elements on a webpage

EXACT TOOL USAGE FORMAT:
For search_internet: {"tool": "search_internet", "search_term": "your search term"}
For navigate_website: {"tool": "navigate_website", "url": "website url"}
For get_clickable_elements: {"tool": "get_clickable_elements", "url": "website url"}

STEP-BY-STEP INSTRUCTIONS:
1. First, search for "Cornell University computer science department faculty"
2. Navigate to the faculty page URL you find
3. Extract professor information from the page
4. Format your final answer exactly as shown below

REQUIRED OUTPUT FORMAT:
Professor: [Professor Name]
Email: [Email Address]
Research Area: [Research Area]

Start now by searching for Cornell University computer science department faculty."""
subsequent_questions = []

print("=== 디버깅 시작 ===")
print(f"초기 질문: {initial_question}")
print("=" * 50)

final_response, final_responses, messages = run_local_llm(client, initial_question, subsequent_questions, llm=llm, web=web_use, navigation=navi_use, T=0.7)

print("\n=== 최종 결과 ===")
print(f"최종 응답: {final_response}")
print("\n=== 모든 응답들 ===")
for i, response in enumerate(final_responses, 1):
    print(f"{i}. {response[:200]}{'...' if len(response) > 200 else ''}")
print("\n=== 메시지 히스토리 ===")
for i, msg in enumerate(messages, 1):
    role = msg.get('role', 'unknown')
    content = msg.get('content', '')[:100] + '...' if len(str(msg.get('content', ''))) > 100 else str(msg.get('content', ''))
    print(f"{i}. [{role}] {content}")