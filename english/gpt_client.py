# english/gpt_client.py

import os                       # 환경변수 불러오기용
import requests                 # GPT API 호출용 HTTP 클라이언트
from dotenv import load_dotenv  # .env 파일에서 환경변수 로딩

# .env 파일 로드
load_dotenv()

# Azure OpenAI 설정값 불러오기 (영어 전용)
api_key = os.getenv("AZURE_OAI_KEY_ENGLISH")                   # Azure OpenAI 키
api_version = os.getenv("AZURE_OAI_API_VERSION")               # API 버전
endpoint = os.getenv("AZURE_OAI_ENDPOINT_ENGLISH")             # 엔드포인트 주소
deployment = os.getenv("AZURE_OAI_DEPLOYMENT_ENGLISH")         # 배포 이름 (모델 ID)

# ✅ 커스텀 예외 클래스 정의
class GPTCallFailed(Exception):
    """
    Azure OpenAI 호출 실패 시 발생하는 예외 클래스입니다.
    상태 코드, 메시지, 응답 본문을 함께 저장하여
    외부에서 더 구체적인 디버깅이 가능하게 합니다.
    """
    def __init__(self, status_code, message, full_response=None):
        self.status_code = status_code
        self.message = message
        self.full_response = full_response
        super().__init__(f"[{status_code}] {message}")

# ✅ GPT 호출 함수
def call_gpt(messages, temperature=0.7, max_tokens=1000) -> str:
    """
    Azure OpenAI GPT 모델에 메시지를 전달하고 응답을 받아옵니다.

    Parameters:
        - messages (list[dict]): GPT에 전달할 메시지 목록
        - temperature (float): 창의성 정도
        - max_tokens (int): 생성할 최대 토큰 수
    Returns:
        - str: 생성된 GPT 응답 텍스트
    Raises:
        - ValueError: 필수 환경변수 누락 시
        - GPTCallFailed: 요청 실패 또는 응답 파싱 오류 시
    """

    # 필수 설정값 누락 여부 확인
    if not endpoint or not deployment or not api_key:
        raise ValueError("❌ .env 설정이 누락되었습니다.")

    # 호출할 API 주소 구성
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"

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

    # GPT 호출 실행
    response = requests.post(url, headers=headers, json=payload)

    # 성공적으로 응답을 받은 경우
    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise GPTCallFailed(200, "응답 파싱 실패", response.json())

    # 실패한 경우 상세 로그 출력 후 예외 발생
    raise GPTCallFailed(response.status_code, "GPT 요청 실패", response.text)