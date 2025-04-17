# english/main.py

from english_tutor import handle_english_tutor

def main():
    print("🔹 ENGLISH 챗봇 활성화")
    print("📢 실전형 영어 코치\n")
    print("'/exit' 입력 시 종료됩니다.\n")

    while True:
        user_input = input("사용자: ").strip()

        if user_input.lower() == "/exit":
            print("챗봇을 종료합니다.")
            break
        if not user_input:
            print("⚠️ 입력이 비어있습니다.\n")
            continue

        response = handle_english_tutor(user_input)
        print(f"\n💬 GPT 응답:\n{response}\n")

if __name__ == "__main__":
    main()