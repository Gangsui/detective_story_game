import os
from dotenv import load_dotenv
import openai

load_dotenv()  # .env 파일에 있는 환경변수 로드

openai.api_type = "azure"
openai.api_base = os.getenv("OPENAI_ENDPOINT")
openai.api_version = os.getenv("OPENAI_API_VERSION")
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_story_from_openai(prompt: str) -> str:
    """
    이 함수는 전달받은 prompt를 Azure OpenAI ChatCompletion 엔진에 보내고,
    응답(스토리 전개)을 story_output으로 반환한다.
    """
    response = openai.ChatCompletion.create(
        engine=os.getenv("OPENAI_DEPLOYMENT_NAME"),
        messages=[
            {"role": "system", "content": "You are ChatGPT, a narrative AI assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    story_output = response.choices[0].message.content.strip()
    return story_output

# 사용 예시
# prompt_text = "Current Time: 10\nCurrent Location: 1st floor study\n...\n"
# story_output = get_story_from_openai(prompt_text)
# print(story_output)
