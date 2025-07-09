import json
import os
import re
import time
from dotenv import load_dotenv
from langchain_community.utilities import SearchApiAPIWrapper
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_community.tools import Tool, DuckDuckGoSearchResults
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# .env 파일에서 환경변수 로드
load_dotenv()

# Google API 키 설정 (환경변수에서 가져오거나 기본값 사용)
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

#크롬 웹 드라이버 경로
driver_path = 'chromedriver-linux64/chromedriver'

if GOOGLE_CSE_ID and GOOGLE_API_KEY:
    os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

options = webdriver.ChromeOptions()
options.binary_location = '/usr/bin/google-chrome'
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')  
options.add_argument('--disable-gpu')  
options.add_argument("--ignore-certificate-errors")

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Google Search API 래퍼 초기화 (API 키가 있을 때만)
search = None
if GOOGLE_CSE_ID and GOOGLE_API_KEY:
    try:
        # 환경변수를 직접 설정
        os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
        os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
        search = GoogleSearchAPIWrapper()
        print(f"Google Search API 초기화 성공: CSE_ID={GOOGLE_CSE_ID[:10]}...")
    except Exception as e:
        print(f"Google Search API 초기화 실패: {e}")

#Google Search API를 활용하여 인터넷 검색 수행
def search_internet(search_term):
    if search is None:
        return "Google Search API가 설정되지 않았습니다. GOOGLE_CSE_ID와 GOOGLE_API_KEY를 설정해주세요."
    #검색 결과를 문자열로 반환
    try:
        return str(search.results(search_term, 10))
    except Exception as e:
        return f"검색 중 오류 발생: {str(e)}"

def is_clickable(tag):
    if tag.name == "a" and tag.get("href"):
        return True
    if tag.name == "button":
        return True
    if tag.name == "input" and tag.get("type") in ["submit", "button"]:
        return True
    if tag.get("onclick"):
        return True
    return False

'''
navigate_website
해당 url 웹 페이지의 텍스트 내용을 추출하여 반환
'''
def navigate_website(url):
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    try:
        #웹 사이트 접속
        driver.get(url)
        new_url = driver.current_url
        
        #HTTP 요청 및 응답 처리
        response = requests.get(url, verify = False)
        response.raise_for_status()  # HTTP 오류 발생시 예외 처리
        
        # time.sleep(2)
        #HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        #텍스트 요소 추출
        texts = soup.find_all(['p', 'h1', 'h2', 'h3', 'div', 'span']) #특정 태그들에서 텍스트 추출
        # clean_texts = [tag.get_text(strip=True) for tag in texts if tag.get_text(strip=True)]
        
        # scirpt 태그 제거
        remove  = soup.find_all(['script'])
        remove_texts_set = set(remove)
        filtered_texts = [elem for elem in texts if elem not in remove_texts_set]
        
        #텍스트 정리
        clean_texts = set(tag.get_text(strip=True) for tag in filtered_texts if tag.get_text(strip=True))

        #반환 값 처리 (현재 URL, 스크래핑된 텍스트 내용,추가 네비게이션 안내 메시지)
        #"찾고자 하는 정보가 없다면 clickable elements 찾아서 네비게이션 하세요"
        return f"Current URL: {new_url}, Scrape text from the url result: {clean_texts}\
                If there is no information you're looking for, find clickable elements from this page and navigate it again."
    
    #HTTP 요청 오류 처리
    except requests.RequestException as e:
        return str(e)  

    except Exception as e:
        return "An error occurred: {}".format(e)

#클릭 가능한 요소를 찾는 함수
def get_clickable_elements(url: str):
    try:
        response = requests.get(url, verify = False)
        response.raise_for_status()  # Ensure we notice bad responses
        time.sleep(2)
        soup = BeautifulSoup(response.text, 'html.parser')
        clickable_elements = soup.find_all(is_clickable)

        element_details = []

        #반복하면서 클릭 가능한 요소를 찾아서 반환
        for element in clickable_elements:
            #a 태그 처리
            if element.name == "a":
                href = element.get("href")
                text = element.get_text(strip=True)
                element_details.append({"url": href, "description": text})
            #button 태그 처리
            elif element.name == "button":
                text = element.get_text(strip=True)
                onclick_url = element.get("onclick")  # Extract URL from onclick if present
                element_details.append({"url": onclick_url, "description": text})
            #input 태그 혹은 클릭 가능한 모든 요소들을 찾는다.
            elif element.name == "input" and element.get("type") in ["submit", "button"]:
                value = element.get("value")  # Button label
                onclick_url = element.get("onclick")  # Extract URL from onclick if present
                element_details.append({"url": onclick_url, "description": value})

        return "Find clickable elements successfully. Choose appropriate elements and corresponding url among: {}".format(clickable_elements)
    except requests.RequestException as e:
        return str(e)  

'''
def get_clickable_elements(url):
    try:
        response = requests.get(url, verify = False)
        response.raise_for_status()  # Ensure we notice bad responses
        # time.sleep(2)
        soup = BeautifulSoup(response.text, 'html.parser')
        clickable_elements = soup.find_all(is_clickable)
        
        
        return "Find clickable elements successfully. Choose appropriate elements and corresponding url among: {}".format(clickable_elements)
    except requests.RequestException as e:
        return str(e)  
'''

'''
GPT 호출 함수
Client: GPT API 호출을 위한 클라이언트
initial_question: 첫번쨰 질문
subsequent_questions: 이후 질문
llm: 사용할 GPT 모델
web: 웹 사이트 내비게이션 사용 여부
navigation: 내비게이션 사용 여부
T: 온도 값
'''
def run_gpt(client, initial_question, subsequent_questions, llm, web = True, navigation = False, T = 1):
    messages = [{"role": "user", "content": initial_question}]
    
    def process_llm_response(messages, tools, navigation = False):
        #삼항 연산자: navigation 값이 True일 경우 gpt_tools를 사용하고, False일 경우 gpt_tools[0]을 사용한다.
        #gpt_tools[0]은 인터넷 검색 도구만 존재하는 경우로 WebSearchAgent 사용 시 사용된다.
        tools = gpt_tools if navigation else [gpt_tools[0]]
        
        #무한 반복문으로 Agent 동작
        while True:
            #Temperture 값이 존재할 경우
            if T:
                #GPT API 호출
                response = client.chat.completions.create(
                    model=llm,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    max_tokens = 3000,
                    temperature=T,
                )
            #Temperture 값이 존재하지 않을 경우
            else:
                response = client.chat.completions.create(
                    model=llm,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    max_tokens = 3000
                )                
            '''
            response값은 다음과 같이 구성되어있다.
            response = {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "웹사이트를 확인해보겠습니다.",
                            "tool_calls": [
                                {
                                    "id": "call_123",
                                    "type": "function",
                                    "function": {
                                        "name": "navigate_website",
                                        "arguments": '{"url": "https://www.cs.cornell.edu/"}'
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
            '''
            #response값중 message 부분만을 가져온다.
            response_message = response.choices[0].message
            
            #도구 호출 정보를 조회한다.
            tool_calls = response_message.tool_calls

            #도구 호출 정보가 없을 경우 종료
            if not tool_calls:
                return response_message, messages  

            available_functions = {
                #키: 함수 객체
                "search_internet": search_internet,
                "navigate_website": navigate_website,
                "get_clickable_elements": get_clickable_elements,
            }
                           
            messages.append(response_message)
            
            #GPT가 선택한 도구들 (함수들)을 반복문을 돌리면서 실행한다.
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)

                if function_name == "navigate_website":
                    function_response = function_to_call(
                        url=function_args.get("url")
                    )
                elif function_name == "get_clickable_elements":
                    function_response = function_to_call(
                        url=function_args.get("url")
                    )      
                        
                else:
                    function_response = function_to_call(
                        search_term=function_args.get("search_term"),
                    )
                    
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
                
            continue

    #gpt가 사용 가능한 도구들 정의
    gpt_tools = [
        #인터넷 검색
        {
            "type": "function",
            "function": {
                "name": "search_internet",
                "description": "Search internet if needed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_term": {
                            "type": "string",
                            "description": "Appropriate search term for you to solve the question",
                        },
                    },
                    "required": ["search_term"],
                },
            },
        },
        #클릭 가능한 요소 찾기
        {
            "type": "function",
            "function": {
                "name": "get_clickable_elements",
                "description": """When you go to the website and decide which button to click to get information,
                                use this function to get all clickable elements and the corresponding url""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL of the website to navigate",
                        }
                    },
                    "required": ["url"],
                },
            },
        },
        #웹 사이트 내비게이션
        {
            "type": "function",
            "function": {
                "name": "navigate_website",
                "description": "Navigate to a website and fetch content of the page",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": """URL of the website to navigate.
                            If the output of this function does not have information you're looking for, find clickable elements and navigate it again""",
                        }
                    },
                    "required": ["url"],
                },
            },
        }
    ]

    #web SearchAgent 사용 시
    if web:
        response_message, messages = process_llm_response(messages, gpt_tools, navigation = navigation )
        final_responses = [response_message.content]
        
        #이후 질문들에 대해서도 반복문을 돌리면서 실행한다.
        for question in subsequent_questions:
            messages.append({"role": "user", "content": question})
            response_message, messages = process_llm_response(messages, gpt_tools, navigation = navigation )
            final_responses.append(response_message.content)
            
        final_response = final_responses[-1]
    
    #web SearchAgent 사용 안할 시 (gpt_tools 빈 리스트)
    #즉, 일반 LLM과 동일하다
    else:
        response_message, messages = process_llm_response(messages, [], navigation=navigation)
        final_responses = [response_message.content]

        for question in subsequent_questions:
            messages.append({"role": "user", "content": question})
            response_message, messages = process_llm_response(messages, [], navigation=navigation)
            final_responses.append(response_message)

        final_response = final_responses[-1]

    return final_response, final_responses, messages

def run_local_llm(client, initial_question, subsequent_questions, llm="llama3:70b", web=True, navigation=False, T=1):
    #초기 messages 생성
    messages = [{"role": "user", "content": initial_question}]
    
    def process_llm_response(messages, tools, navigation=False):
        #삼항 연산자: navigation 값이 True일 경우 local_tools를 사용하고, False일 경우 local_tools[0]을 사용한다.
        #local_tools[0]은 인터넷 검색 도구만 존재하는 경우로 WebSearchAgent 사용 시 사용된다.
        tools = local_tools if navigation else [local_tools[0]]
        
        #무한 반복문으로 Agent 동작
        while True:
            #메시지를 Ollama 형식으로 변환
            prompt = ""
            for msg in messages:
                if msg["role"] == "user":
                    prompt += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"
                elif msg["role"] == "tool":
                    prompt += f"Tool Result: {msg['content']}\n"
            
            #도구 사용 안내 추가
            if tools and web:
                tool_descriptions = ""
                for tool in tools:
                    tool_descriptions += f"\n- {tool['function']['name']}: {tool['function']['description']}"
                prompt += f"\n\nAvailable tools:{tool_descriptions}\n\nYou can use these tools to help answer the question. If you need to use a tool, respond with the tool name and parameters in JSON format."
            
            prompt += "Assistant: "
            
            # 디버깅: 프롬프트 출력
            print(f"\n=== LLM 입력 프롬프트 (길이: {len(prompt)}) ===")
            print(prompt[-1000:] if len(prompt) > 1000 else prompt)  # 마지막 1000자만 출력
            print("=" * 50)
            
            try:
                #Ollama API 호출
                response = client.generate(
                    model=llm,
                    prompt=prompt,
                    options={
                        "temperature": T,
                        "num_predict": 3000,
                        "num_ctx": 256000  # 컨텍스트 크기를 8192로 설정
                    }
                )
                
                #응답 추출
                assistant_response = response['response']
                
                #도구 호출이 있는지 확인 (간단한 JSON 파싱)
                import re
                import json
                
                #도구 호출 패턴 찾기 (더 유연한 패턴)
                tool_calls = []
                
                print(f"LLM 응답: {assistant_response}")
                
                # JSON 형태의 도구 호출 찾기 (backtick 제거)
                clean_response = assistant_response.replace('`', '').replace('```', '')
                
                # 패턴 1: parameters/params 키가 있는 경우
                json_tool_pattern1 = r'"tool":\s*"(\w+)"[^}]*"(parameters|params)":\s*(\{[^}]*\})'
                json_matches1 = re.findall(json_tool_pattern1, clean_response)
                if json_matches1:
                    print(f"JSON 패턴 매치 (parameters): {json_matches1}")
                    for tool_name, param_key, params in json_matches1:
                        tool_calls.append((tool_name, params))
                
                # 패턴 2: 직접 매개변수가 있는 경우 (url, search_term 등)
                if not tool_calls:
                    json_tool_pattern2 = r'"tool":\s*"(\w+)"[^}]*"(\w+)":\s*"([^"]*)"'
                    json_matches2 = re.findall(json_tool_pattern2, clean_response)
                    if json_matches2:
                        print(f"JSON 패턴 매치 (직접 매개변수): {json_matches2}")
                        for tool_name, param_key, param_value in json_matches2:
                            # 단일 매개변수를 JSON 객체로 변환
                            if param_key == "url":
                                params = f'{{"url": "{param_value}"}}'
                            elif param_key in ["search_term", "query"]:
                                params = f'{{"search_term": "{param_value}"}}'
                            else:
                                params = f'{{"{param_key}": "{param_value}"}}'
                            tool_calls.append((tool_name, params))
                
                # 패턴 3: "Tool: name\nParameters: {...}" 형태
                if not tool_calls:
                    tool_pattern3 = r'Tool:\s*(\w+)\s*\nParameters:\s*(\{[^}]*\})'
                    tool_matches3 = re.findall(tool_pattern3, clean_response)
                    if tool_matches3:
                        print(f"Tool/Parameters 패턴 매치: {tool_matches3}")
                        for tool_name, params in tool_matches3:
                            tool_calls.append((tool_name, params))
                
                # 함수 형태의 도구 호출 찾기
                if not tool_calls:
                    func_pattern = r'(\w+)\s*\(\s*(\{[^}]*\})\s*\)'
                    func_matches = re.findall(func_pattern, clean_response)
                    print(f"함수 패턴 매치: {func_matches}")
                    for tool_name, params in func_matches:
                        tool_calls.append((tool_name, params))
                
                print(f"최종 도구 호출: {tool_calls}")
                
                if not tool_calls or not web:
                    #도구 호출이 없으면 일반 응답으로 처리
                    messages.append({"role": "assistant", "content": assistant_response})
                    return assistant_response, messages
                
                #도구 호출 처리
                available_functions = {
                    "search_internet": search_internet,
                    "navigate_website": navigate_website,
                    "get_clickable_elements": get_clickable_elements,
                }
                
                messages.append({"role": "assistant", "content": assistant_response})
                
                #각 도구 호출 처리
                for tool_name, tool_args_str in tool_calls:
                    if tool_name in available_functions:
                        try:
                            print(f"\n=== 도구 호출 처리 ===")
                            print(f"도구 이름: {tool_name}")
                            print(f"도구 인수: {tool_args_str}")
                            
                            #JSON 파싱
                            tool_args = json.loads(tool_args_str)
                            function_to_call = available_functions[tool_name]
                            
                            if tool_name == "navigate_website":
                                function_response = function_to_call(url=tool_args.get("url"))
                                print(f"웹사이트 접속: {tool_args.get('url')}")
                            elif tool_name == "get_clickable_elements":
                                function_response = function_to_call(url=tool_args.get("url"))
                                print(f"클릭 가능한 요소 찾기: {tool_args.get('url')}")
                            else:
                                # search_internet의 경우 search_term 또는 query 사용
                                search_term = tool_args.get("search_term") or tool_args.get("query")
                                function_response = function_to_call(search_term=search_term)
                                print(f"검색 실행: {search_term}")
                            
                            print(f"도구 응답 길이: {len(function_response)}")
                            print(f"도구 응답 (처음 200자): {function_response[:200]}...")
                            
                            messages.append({
                                "role": "tool",
                                "name": tool_name,
                                "content": function_response,
                            })
                            
                        except (json.JSONDecodeError, KeyError) as e:
                            error_msg = f"도구 호출 파싱 오류: {str(e)}"
                            messages.append({
                                "role": "tool",
                                "name": tool_name,
                                "content": error_msg,
                            })
                
                continue
                
            except Exception as e:
                error_response = f"오류 발생: {str(e)}"
                messages.append({"role": "assistant", "content": error_response})
                return error_response, messages

    #local_llm이 사용 가능한 도구들 정의
    local_tools = [
        #인터넷 검색
        {
            "type": "function",
            "function": {
                "name": "search_internet",
                "description": "Search internet if needed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_term": {
                            "type": "string",
                            "description": "Appropriate search term for you to solve the question",
                        },
                    },
                    "required": ["search_term"],
                },
            },
        },
        #클릭 가능한 요소 찾기
        {
            "type": "function",
            "function": {
                "name": "get_clickable_elements",
                "description": """When you go to the website and decide which button to click to get information,
                                use this function to get all clickable elements and the corresponding url""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL of the website to navigate",
                        }
                    },
                    "required": ["url"],
                },
            },
        },
        #웹 사이트 내비게이션
        {
            "type": "function",
            "function": {
                "name": "navigate_website",
                "description": "Navigate to a website and fetch content of the page",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": """URL of the website to navigate.
                            If the output of this function does not have information you're looking for, find clickable elements and navigate it again""",
                        }
                    },
                    "required": ["url"],
                },
            },
        }
    ]

    #web SearchAgent 사용 시
    if web:
        response_message, messages = process_llm_response(messages, local_tools, navigation=navigation)
        final_responses = [response_message]
        
        #이후 질문들에 대해서도 반복문을 돌리면서 실행한다.
        for question in subsequent_questions:
            messages.append({"role": "user", "content": question})
            response_message, messages = process_llm_response(messages, local_tools, navigation=navigation)
            final_responses.append(response_message)
            
        final_response = final_responses[-1]
    
    #web SearchAgent 사용 안할 시 (local_tools 빈 리스트)
    #즉, 일반 LLM과 동일하다
    else:
        response_message, messages = process_llm_response(messages, [], navigation=navigation)
        final_responses = [response_message]

        for question in subsequent_questions:
            messages.append({"role": "user", "content": question})
            response_message, messages = process_llm_response(messages, [], navigation=navigation)
            final_responses.append(response_message)

        final_response = final_responses[-1]

    return final_response, final_responses, messages


'''
def run_claude(client, initial_question, subsequent_questions, llm, web=True, navigation=False, T= None):
    messages = [{"role": "user", "content": initial_question}]
    claude_tools = [{
                "name": "search_internet",
                "description":  "Search internet if you needed.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "search_term": {
                            "type": "string",
                            "description": "Appropriate search term for you to solve the question"
                        }
                    },
                    "required": ["search_term"]
                }
            },
            {
                "name": "get_clickable_elements",
                "description":  """When you go to the website and decide which button to click to get information,
                                use this function to get all clickable elements and the corresponding url""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Website url to navigate"
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "navigate_website",
                "description":  "Navigate to a website and fetch content of the page",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": """URL of the website to navigate.
                                            If the output of this function does not have information you're looking for,
                                            find clickable elements and navigate it again"""
                        },

                    },
                    "required": ["url"]
                }
            }

    ]

    def process_llm_response(messages, claude_tools, navigation=False):
        if len(claude_tools) != 0:
            tools = claude_tools if navigation else [claude_tools[0]]
            
        while True:

            if len(claude_tools) != 0:
                if T :
                    response = client.messages.create(
                        model=llm,
                        max_tokens=3000,
                        tools= tools,  # Assuming the platform allows to pass tools like this
                        messages=messages,
                        temperature = T
                    )
                else:
                    response = client.messages.create(
                        model=llm,
                        max_tokens=3000,
                        tools= tools,  # Assuming the platform allows to pass tools like this
                        messages=messages
                    )
            else:
                response = client.messages.create(
                    model=llm,
                    max_tokens=3000,
                    messages=messages
                )               
            
            if response.stop_reason != "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                return response, messages  


            tool_use = response.content[-1]
            tool_name = tool_use.name
            tool_input = tool_use.input
            messages.append({"role": "assistant", "content": response.content})

            available_functions = {
                "search_internet": search_internet,
                "navigate_website": navigate_website,
                "get_clickable_elements": get_clickable_elements
            }

            if tool_name in available_functions:
                function_response = available_functions[tool_name](**tool_input)
                    
                tool_response = {
                    "role": "user",
                    "content": [
                        {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": function_response
                        }
                    ]
                }
                messages.append(tool_response)

    if web:
        final_responses = []
        response, messages = process_llm_response(messages, claude_tools, navigation=navigation)
        final_responses.append(response)

        for question in subsequent_questions:
            messages.append({"role": "user", "content": question})
            response, messages = process_llm_response(messages, claude_tools, navigation=navigation)
            final_responses.append(response)

        final_response = final_responses[-1]

    else:
        final_responses = []
        response_message, messages = process_llm_response(messages, [], navigation=navigation)
        final_responses.append(response_message)

        for question in subsequent_questions:
            messages.append({"role": "user", "content": question})
            response_message, messages = process_llm_response(messages, [], navigation=navigation)
            final_responses.append(response_message)

        final_response = final_responses[-1]

    return final_response.content[0].text, final_responses, messages



def run_gemini(client, question, subsequent_questions, llm, web=True, navigation=False):
    chat = client.start_chat(enable_automatic_function_calling=web)
    response = chat.send_message(question)
    return response.text

'''
