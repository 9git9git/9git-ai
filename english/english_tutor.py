# english/english_tutor.py

import os
from uuid import uuid4
from datetime import datetime, timezone

from gpt_client import call_gpt
from ai_search import upload_to_index, search_notice

# 🧠 GPT 대화 히스토리 저장용 리스트 (세션 유지)
chat_memory = []

def handle_english_tutor(user_input: str) -> str:
    """
    🔹 영어 튜터 메인 핸들러 함수
    - 사용자 입력 기반 RAG 검색 → GPT 응답 → 요약 저장까지 수행
    """

    # 🔍 Azure Search에 저장할 인덱스 이름 (영어 전용)
    index_name = os.getenv("AZURE_SEARCH_INDEX_ENGLISH")

    # ✏️ 입력 전처리
    question = user_input.strip()

    # 📡 1. 시험 일정 등 유사 정보 검색 (RAG)
    rag_context = search_notice(query=question)
    print("🧾 검색 결과 (RAG):", rag_context)

    # 📋 2. 프롬프트 로딩(첫 호출이면 system prompt 등록, 아니면 user template만 불러옴)
    if not chat_memory:
        system_prompt, user_template = load_combined_prompt()
        chat_memory.append({"role": "system", "content": system_prompt})
    else:
        _, user_template = load_combined_prompt()

    # 🙋 사용자 메시지 구성(사용자 입력을 템플릿 기반 메시지로 포맷)
    user_message = format_prompt(template=user_template, context=rag_context, question=question)
    chat_memory.append({"role": "user", "content": user_message})

    # 🤖 3. GPT 호출 → 응답 받기
    result = call_gpt(messages=chat_memory)
    chat_memory.append({"role": "assistant", "content": result})

    # 📝 4. 응답을 한 문장 요약 생성 (한글)
    summary_prompt = [
        {"role": "system", "content": "다음 응답을 한 문장으로 요약해 주세요. 반드시 한국어로."},
        {"role": "user", "content": result}
    ]
    summary = call_gpt(messages=summary_prompt)

    # 💾 5. 요약 결과를 Azure AI Search에 저장
    upload_to_index(index_name, {
        "id": f"english-{str(uuid4())}",
        "mode": "summary",
        "category": "english",  # ✅ category 하드코딩 (다른 구조와 분리되었으므로 안전)
        "original": question,
        "summary": summary,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "user_choice": ""
    })

    return result

# 🔧 프롬프트 로더 (txt 파일에서 system + user template 분리)
def load_combined_prompt() -> tuple[str, str]:
    """
    📂 prompts/english.txt 파일을 불러와 system prompt와 user template를 분리
    - 구분자는 "🔸" 사용
    """
    prompt_path = os.path.join("prompts", "english.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 🔸 기준으로 프롬프트 분리
    if "🔸" in content:
        system_prompt, user_prompt = content.split("🔸", 1)
    else:
        system_prompt = content
        user_prompt = "{context}\n\n{question}"  # fallback 템플릿

    return system_prompt.strip(), user_prompt.strip()


# 💬 프롬프트 포맷팅: context와 question을 템플릿에 삽입
def format_prompt(template: str, context: str, question: str) -> str:
    """
    🔄 사용자 질문과 RAG context를 템플릿에 삽입
    """
    return template.replace("{context}", context).replace("{question}", question)