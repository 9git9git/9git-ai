# english/gpt_client.py

import os                       # 환경변수 불러오기용
import requests                 # GPT API 호출용 HTTP 클라이언트
from dotenv import load_dotenv  # .env 파일에서 환경변수 로딩

# .env 파일 로드
load_dotenv()

# Azure OpenAI 설정값 불러오기
api_key = os.getenv("AZURE_OAI_KEY_ENGLISH")                     # Azure OpenAI 키
api_version = os.getenv("AZURE_OAI_API_VERSION")                 # API 버전
endpoint = os.getenv("AZURE_OAI_ENDPOINT_ENGLISH")               # 엔드포인트 주소
deployment = os.getenv("AZURE_OAI_DEPLOYMENT_ENGLISH")           # 배포 이름 (모델 ID)


# ✅ GPT 호출 함수
def call_gpt(messages, temperature=0.7, max_tokens=1000) -> str:
    """
    GPT 모델에 메시지 리스트를 전달하여 응답을 받아옵니다.
    - messages: 시스템/사용자 대화 이력 (list of dict)
    - temperature: 창의성 조절 파라미터 (기본 0.7)
    - max_tokens: 최대 토큰 수 (기본 1000)
    """

    # 필수 환경변수 누락 시 오류 발생
    if not endpoint or not deployment or not api_key:
        raise ValueError("❌ .env 설정이 누락되었습니다.")

    # 호출할 API 주소 구성
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    print(f"📡 호출 URL: {url}")

    # 요청 헤더 설정
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    # GPT API 요청 페이로드 구성
    payload = {
        "messages": messages,     # 메시지 리스트
        "temperature": temperature,
        "top_p": 0.95,
        "max_tokens": max_tokens
    }

    # 프롬프트가 잘 들어오는지 test용 
    # print("\n📢 [SYSTEM + USER PROMPT] =====================")
    # for msg in messages:
    #    print(f"[{msg['role']}] {msg['content']}\n")
    # print("================================================\n")

    # GPT 호출 실행
    response = requests.post(url, headers=headers, json=payload)

    # 성공적으로 응답을 받은 경우
    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print("❌ GPT 응답 파싱 오류:", e)
            print("📨 응답 원문:", response.json())
            raise

    # 실패한 경우 상세 로그 출력 후 예외 발생
    else:
        print(f"❌ GPT 호출 실패 {response.status_code}")
        print("📤 요청:", messages)
        print("📨 응답:", response.text)
        raise Exception("GPT 요청 실패")