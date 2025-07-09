#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# utils.py에서 필요한 함수들을 import
from utils import navigate_website, get_clickable_elements

def test_navigate_website():
    """
    navigate_website 함수를 테스트하는 함수
    """
    print("=== navigate_website 함수 테스트 시작 ===")
    
    # 테스트할 URL
    test_url = "https://www.cs.cornell.edu/"
    
    print(f"테스트 URL: {test_url}")
    print("-" * 50)
    
    try:
        # navigate_website 함수 호출
        result = navigate_website(test_url)
        
        print("✅ 함수 실행 성공!")
        print("\n=== 결과 ===")
        print(result)
        
        # 결과 분석
        if "Current URL:" in result:
            print("\n✅ URL 접속 성공")
        else:
            print("\n❌ URL 접속 실패")
            
        if "Scrape text from the url result:" in result:
            print("✅ 텍스트 스크래핑 성공")
        else:
            print("❌ 텍스트 스크래핑 실패")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print(f"오류 타입: {type(e).__name__}")
        
    print("\n=== 테스트 완료 ===")

def test_get_clickable_elements():
    """
    get_clickable_elements 함수를 테스트하는 함수
    """
    print("\n" + "="*60)
    print("=== get_clickable_elements 함수 테스트 시작 ===")
    
    # 테스트할 URL
    test_url = "https://www.cs.cornell.edu/"
    
    print(f"테스트 URL: {test_url}")
    print("-" * 50)
    
    try:
        # get_clickable_elements 함수 호출
        result = get_clickable_elements(test_url)
        
        print("✅ 함수 실행 성공!")
        print("\n=== 결과 ===")
        print(result)
        
        # 결과 분석
        if "Find clickable elements successfully" in result:
            print("\n✅ 클릭 가능한 요소 찾기 성공")
        else:
            print("\n❌ 클릭 가능한 요소 찾기 실패")
            
        # 클릭 가능한 요소 개수 확인
        if "Choose appropriate elements" in result:
            print("✅ 클릭 가능한 요소 목록 생성 성공")
        else:
            print("❌ 클릭 가능한 요소 목록 생성 실패")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print(f"오류 타입: {type(e).__name__}")
        
    print("\n=== 테스트 완료 ===")

def main():
    """
    모든 테스트를 실행하는 메인 함수
    """
    print("🚀 웹 스크래핑 함수 테스트 시작")
    print("="*60)
    
    # 1. navigate_website 테스트
    test_navigate_website()
    
    # 2. get_clickable_elements 테스트
    test_get_clickable_elements()
    
    print("\n" + "="*60)
    print("🎉 모든 테스트 완료!")

if __name__ == "__main__":
    main() 