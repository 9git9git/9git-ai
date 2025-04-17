# coding/main.py

from coding_tutor import handle_coding_tutor

def main():
    print("🔹 CODING 챗봇 활성화")
    print("📢 상위 1% 개발자 멘토\n")
    print("'/exit' 입력 시 종료됩니다.\n")

    while True:
        user_input = input("사용자: ").strip()

        if user_input.lower() == "/exit":
            print("챗봇을 종료합니다.")
            break
        if not user_input:
            print("⚠️ 입력이 비어있습니다.\n")
            continue

        response = handle_coding_tutor(user_input)
        print(f"\n💬 GPT 응답:\n{response}\n")

if __name__ == "__main__":
    main()