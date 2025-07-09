#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ollama
from utils import run_local_llm

def test_local_llm():
    """
    run_local_llm 함수를 테스트하는 함수
    """
    print("=== run_local_llm 함수 테스트 시작 ===")
    
    # Ollama 클라이언트 생성
    client = ollama.Client()
    
    # 테스트 질문
    initial_question = "Python이 뭐야?"
    subsequent_questions = ["그럼 JavaScript는?"]
    
    print(f"초기 질문: {initial_question}")
    print(f"추가 질문: {subsequent_questions}")
    print("-" * 50)
    
    try:
        # run_local_llm 함수 호출
        final_response, final_responses, messages = run_local_llm(
            client=client,
            initial_question=initial_question,
            subsequent_questions=subsequent_questions,
            llm="llama3:70b",
            web=False,  # 1단계에서는 웹 기능 비활성화
            navigation=False,
            T=0.7
        )
        
        print("✅ 함수 실행 성공!")
        print("\n=== 결과 ===")
        print(f"최종 응답: {final_response}")
        print(f"모든 응답 개수: {len(final_responses)}")
        print(f"메시지 개수: {len(messages)}")
        
        print("\n=== 모든 응답들 ===")
        for i, response in enumerate(final_responses, 1):
            print(f"{i}. {response[:100]}{'...' if len(response) > 100 else ''}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print(f"오류 타입: {type(e).__name__}")
        
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_local_llm() 