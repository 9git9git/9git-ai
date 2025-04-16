# english/ai_search.py

import os                # 환경변수에서 API 키, 엔드포인트 등을 불러오기 위해 사용
import requests          # Azure AI Search REST API를 호출하기 위한 HTTP 클라이언트
import json              # JSON 직렬화 및 역직렬화를 위한 모듈
from datetime import datetime, timezone  # UTC 기반의 타임스탬프 생성을 위해 사용
from uuid import uuid4   # 각 문서에 고유한 ID 부여를 위해 사용


# 🔍 영어 시험 정보를 Azure AI Search에서 검색 (RAG)
def search_notice(query: str) -> str:
    """
    사용자 질문(query)에 대해 Azure AI Search에서
    영어 전용 시험 정보(englishnoticeindex) 인덱스를 조회하고,
    summary 필드의 텍스트를 정리하여 반환합니다.
    """

    # .env에서 Azure Search 환경변수 불러오기
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")                     # Search 서비스 엔드포인트
    api_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")                     # Search 서비스 관리용 API 키
    index_name = os.getenv("AZURE_SEARCH_INDEX_NOTICE_ENGLISH")       # 영어 시험 정보를 담은 인덱스 

    # REST API 호출을 위한 URL 구성
    url = f"{endpoint}/indexes/{index_name}/docs/search?api-version=2023-07-01-preview"

    # 요청 헤더 설정 (API 인증 및 Content-Type 명시)
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    # 요청 본문: 검색어와 summary 필드만 추출
    body = {
        "search": query,
        "select": "summary"
    }

    # 검색 요청 실행 및 응답 수신 (실제 POST 요청 전송)
    response = requests.post(url, headers=headers, json=body)
    result = response.json()  # 응답 결과를 JSON 형태로 파싱

    # 응답 결과에서 summary 필드를 추출해 문자열로 정리
    if "value" in result and len(result["value"]) > 0:
        return "\n---\n".join([
            doc["summary"]
            for doc in result["value"]
            if doc.get("summary")   # summary가 존재하는 문서만 필터링
        ])
    else:
        return "검색 결과가 없습니다."  # 결과가 없을 경우 기본 메시지 반환


# 💾 GPT 응답을 Azure Search에 저장하는 함수
def upload_to_index(index_name: str, data: dict):
    """
    GPT가 생성한 응답 요약 데이터를 지정한 인덱스(englishtutorindex)에 업로드합니다.
    Azure AI Search의 index API를 사용하여 데이터 삽입을 수행합니다.
    """

    # .env에서 업로드 API 설정값 불러오기
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")

    # 업로드용 REST API URL 구성
    url = f"{endpoint}/indexes/{index_name}/docs/index?api-version=2025-03-01-preview"

    # 요청 헤더 설정
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    # 필수 필드 자동 보완(필수 필드가 누락되었을 경우를 대비하여 기본값 설정)
    data.setdefault("id", str(uuid4()))                                      # 문서 고유 ID
    data.setdefault("created_at", datetime.now(timezone.utc).isoformat())    # UTC 타임스탬프(생성시각)
    data.setdefault("mode", "summary")                                       # 저장 모드 기본값

    # 업로드용 JSON payload 구성 (action은 'upload')
    payload = {
        "value": [
            {
                "@search.action": "upload",
                **data  # data 딕셔너리 전체를 삽입
            }
        ]
    }

    # 실제 POST 요청 전송 (데이터 업로드)
    response = requests.post(
        url,
        headers=headers, 
        data=json.dumps(payload, ensure_ascii=False)  # 한글 깨짐 방지를 위해 ensure_ascii=False 설정
    )

    # 결과 확인 및 출력
    if response.status_code != 200:
        print(f"❌ 저장 실패 {response.status_code} - {response.text}")  # 실패 시 상세 에러 메시지 출력
    else:
        print(f"✅ 저장 성공: {index_name}")  # 성공 시 저장된 인덱스명 출력