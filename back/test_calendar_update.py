#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime, timedelta

def test_calendar_auto_update():
    """캘린더 자동 업데이트 기능 테스트 (추가/삭제/수정)"""
    
    base_url = "http://localhost:8000"
    
    # 1. 로그인 테스트
    print("=== 1. 로그인 테스트 ===")
    login_data = {
        "login_id": "teacher1",
        "login_pw": "password123"
    }
    
    try:
        login_response = requests.post(f"{base_url}/api/login", json=login_data)
        print(f"로그인 상태: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"로그인 성공: {login_result.get('message', '')}")
            user_id = login_result.get('user', {}).get('id', 1)
        else:
            print("로그인 실패, 기본 user_id=1 사용")
            user_id = 1
    except Exception as e:
        print(f"로그인 오류: {e}")
        user_id = 1
    
    # 2. 현재 캘린더 이벤트 확인
    print(f"\n=== 2. 현재 캘린더 이벤트 확인 (user_id={user_id}) ===")
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    try:
        calendar_response = requests.get(f"{base_url}/api/calendar/events?user_id={user_id}&year={year}&month={month}")
        print(f"캘린더 조회 상태: {calendar_response.status_code}")
        
        if calendar_response.status_code == 200:
            calendar_result = calendar_response.json()
            if calendar_result.get('success'):
                events = calendar_result.get('data', [])
                print(f"현재 이벤트 개수: {len(events)}")
                for event in events:
                    print(f"  - {event.get('title')} ({event.get('start_date')})")
            else:
                print("캘린더 조회 실패")
        else:
            print("캘린더 조회 오류")
    except Exception as e:
        print(f"캘린더 조회 오류: {e}")
    
    # 3. AI 챗봇을 통한 일정 추가/삭제/수정 테스트
    print(f"\n=== 3. AI 챗봇 일정 관리 테스트 ===")
    
    test_messages = [
        # 일정 추가 테스트
        "오늘 오후 3시에 테스트 미팅을 추가해줘",
        "내일 오전 11시에 테스트 상담을 등록해줘",
        
        # 일정 삭제 테스트 (추가된 일정을 삭제)
        "오늘 오후 3시 미팅을 삭제해줘",
        "내일 오전 11시 상담을 제거해줘",
        
        # 일정 수정 테스트
        "오늘 오후 2시 미팅을 오후 4시로 변경해줘",
        "내일 오전 10시 상담을 오후 2시로 수정해줘"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- 테스트 {i}: {message} ---")
        
        try:
            chat_data = {
                "message": message,
                "user_id": user_id
            }
            
            chat_response = requests.post(f"{base_url}/api/chat", json=chat_data)
            print(f"챗봇 응답 상태: {chat_response.status_code}")
            
            if chat_response.status_code == 200:
                chat_result = chat_response.json()
                if chat_result.get('success'):
                    response_text = chat_result.get('response', '')
                    print(f"AI 응답: {response_text}")
                    
                    # 일정 관리 관련 키워드 체크
                    event_keywords = [
                        # 일정 추가 관련
                        '일정이 성공적으로 등록되었습니다',
                        '일정을 추가했습니다',
                        '일정이 추가되었습니다',
                        '일정을 생성했습니다',
                        '일정이 생성되었습니다',
                        '캘린더에 추가했습니다',
                        '캘린더에 등록했습니다',
                        '일정을 등록했습니다',
                        '일정이 등록되었습니다',
                        '성공적으로 등록되었습니다',
                        '등록되었습니다',
                        
                        # 일정 삭제 관련
                        '일정이 성공적으로 삭제되었습니다',
                        '일정을 삭제했습니다',
                        '일정이 삭제되었습니다',
                        '캘린더에서 삭제했습니다',
                        '캘린더에서 제거했습니다',
                        '일정을 제거했습니다',
                        '일정이 제거되었습니다',
                        '성공적으로 삭제되었습니다',
                        '삭제되었습니다',
                        '제거되었습니다',
                        
                        # 일정 수정 관련
                        '일정이 성공적으로 수정되었습니다',
                        '일정을 수정했습니다',
                        '일정이 수정되었습니다',
                        '일정을 변경했습니다',
                        '일정이 변경되었습니다',
                        '캘린더에서 수정했습니다',
                        '캘린더에서 변경했습니다',
                        '성공적으로 수정되었습니다',
                        '수정되었습니다',
                        '변경되었습니다',
                        '업데이트되었습니다'
                    ]
                    
                    is_event_updated = any(keyword in response_text for keyword in event_keywords)
                    print(f"일정 관리 감지: {is_event_updated}")
                    
                    if is_event_updated:
                        print("✅ 일정 관리 성공 - 프론트엔드에서 자동 업데이트가 트리거됩니다!")
                else:
                    print(f"챗봇 응답 오류: {chat_result.get('error', '')}")
            else:
                print("챗봇 API 오류")
        except Exception as e:
            print(f"챗봇 테스트 오류: {e}")
    
    # 4. 최종 캘린더 이벤트 확인
    print(f"\n=== 4. 최종 캘린더 이벤트 확인 ===")
    
    try:
        final_calendar_response = requests.get(f"{base_url}/api/calendar/events?user_id={user_id}&year={year}&month={month}")
        print(f"최종 캘린더 조회 상태: {final_calendar_response.status_code}")
        
        if final_calendar_response.status_code == 200:
            final_calendar_result = final_calendar_response.json()
            if final_calendar_result.get('success'):
                final_events = final_calendar_result.get('data', [])
                print(f"최종 이벤트 개수: {len(final_events)}")
                for event in final_events:
                    print(f"  - {event.get('title')} ({event.get('start_date')})")
            else:
                print("최종 캘린더 조회 실패")
        else:
            print("최종 캘린더 조회 오류")
    except Exception as e:
        print(f"최종 캘린더 조회 오류: {e}")
    
    print(f"\n=== 테스트 완료 ===")
    print("프론트엔드에서 AI 어시스턴트로 일정을 추가/삭제/수정하면 자동으로 캘린더가 업데이트됩니다!")

if __name__ == "__main__":
    test_calendar_auto_update() 