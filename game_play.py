import os
import json
import re
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
        max_tokens=1000,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    story_output = response.choices[0].message.content.strip()
    return story_output


def parse_time_range(time_range_str):
    match = re.search(r"(\d+)\s*~\s*(\d+)", time_range_str)
    if match:
        start = int(match.group(1))
        end = int(match.group(2))
        return start, end
    return None, None

def get_description_and_relationships(current_time, current_location, story_data, relationship_data):
    """
    주어진 시간(current_time)과 장소(current_location)에 해당하는 스토리 description을 추출하고,
    해당 시점 같은 장소에 있는 인물들의 role, personality, relationships를 반환한다.
    """
    time_segments = story_data.get("time_segments", [])
    matched_segment = None
    for segment in time_segments:
        tr = segment.get("time_range", "")
        start, end = parse_time_range(tr)
        if start is not None and end is not None:
            if start <= current_time < end:
                matched_segment = segment
                break

    if not matched_segment:
        return "", [], []

    characters_info = matched_segment.get("characters", [])
    location_descriptions = []
    characters_in_location = set()

    for char_data in characters_info:
        name = char_data.get("name", "")
        actions = char_data.get("actions", [])
        for action in actions:
            locations = action.get("locations", [])
            if current_location in locations:
                desc = action.get("description", "")
                if desc:
                    location_descriptions.append(f"{name}: {desc}")
                characters_in_location.add(name)

    detailed_characters = []
    char_name_to_data = {}

    rel_characters = relationship_data.get("characters", [])
    for c in rel_characters:
        cname = c.get("name", "")
        if cname in characters_in_location:
            char_name_to_data[cname] = {
                "name": cname,
                "role": c.get("role", ""),
                "personality": c.get("personality", ""),
                "relationships": c.get("relationships", [])
            }

    characters_in_location_list = list(characters_in_location)
    relationship_descriptions = []
    for i in range(len(characters_in_location_list)):
        for j in range(i+1, len(characters_in_location_list)):
            char_a = characters_in_location_list[i]
            char_b = characters_in_location_list[j]
            data_a = char_name_to_data.get(char_a)
            data_b = char_name_to_data.get(char_b)
            if data_a and data_b:
                # a->b
                for rel in data_a["relationships"]:
                    related_chars = rel.get("characters", [])
                    if char_b in related_chars:
                        relationship_descriptions.append(f"{char_a} - {char_b}: {rel.get('description','')}")
                # b->a
                for rel in data_b["relationships"]:
                    related_chars = rel.get("characters", [])
                    if char_a in related_chars:
                        relationship_descriptions.append(f"{char_b} - {char_a}: {rel.get('description','')}")

    for c in characters_in_location_list:
        cdata = char_name_to_data.get(c, {})
        detailed_characters.append({
            "name": cdata.get("name", c),
            "role": cdata.get("role", ""),
            "personality": cdata.get("personality", "")
        })

    final_description = "\n".join(location_descriptions)
    return final_description, detailed_characters, relationship_descriptions


def show_intro():
    intro_path = os.path.join("Prompt", "intro_prompt.txt")
    with open(intro_path, "r", encoding="utf-8") as f:
        intro_text = f.read()
    print(intro_text)


def parse_openai_response(response_text: str):
    # 응답에서 Current Time, Current Location, Story, summary 추출
    # 응답 형식 예:
    # Current Time: 10
    # Current Location: 1st floor study
    # Story:
    # ... (story content) ...
    # summary:
    # ... (summary content) ...
    time_match = re.search(r"Current Time:\s*(\d+)", response_text)
    loc_match = re.search(r"Current Location:\s*(.*)", response_text)
    story_index = response_text.find("Story:")
    summary_index = response_text.find("summary:")

    if story_index != -1 and summary_index != -1:
        story_content = response_text[story_index+6:summary_index].strip()
    else:
        story_content = response_text

    if summary_index != -1:
        summary_content = response_text[summary_index+8:].strip()
    else:
        summary_content = ""

    current_time = int(time_match.group(1)) if time_match else 0
    current_location = loc_match.group(1).strip() if loc_match else "Unknown Location"

    return current_time, current_location, story_content, summary_content


def run_game_loop():
    # story.json, relation.json 로드
    with open("./json/story_English.json", "r", encoding="utf-8") as f:
        story_data = json.load(f)

    with open("./json/relationship.json", "r", encoding="utf-8") as f:
        relationship_data = json.load(f)

    show_intro()

    current_time = 0
    current_location = "1st floor entrance"
    summary = ""
    actions_per_segment = 2
    actions_taken = 0
    max_time = 50
    attempt = 1

    # 여기서 prompt를 코드 내에서 직접 정의하여 summary를 포함하도록 한다.
    # Relationships, Summary, User Action, Description, Current Time, Current Location, Story를 모두 제공하고
    # 마지막에 모델에게 Current Time, Current Location, Story, summary를 반환하도록 요청한다.
    def build_prompt(ct, cl, summ, ua, desc, rel_str):
        # Prompt 내부에서 instructions 추가
        # 최종적으로 모델이 Current Time, Current Location, Story, summary를 출력하도록 유도
        return f"""
You are ChatGPT, a narrative AI that continues a detective story. Describe events and characters as if they truly exist.

Current Time: {ct} minutes
Current Location: {cl}
Summary:
{summ}

User Action:
{ua}

Description:
{desc}

Relationships (for AI context only, do not reveal to user):
{rel_str}

Instructions:
- Use the given Summary and User Action to inform the ongoing narrative.
- The Relationships information is for context only. Do not show it directly.
- Continue the story naturally and immersively.
- Do not reveal the internal summary or meta info directly.
- At the end of your response, format your answer as:

Current Time: [updated time]
Current Location: [updated location]
Story:
[continued story here]
summary:
[updated summary here]

Make sure to include 'summary:' at the end and provide the updated summary.
"""

    while True:
        user_action = input("\nYour action: ")
        actions_taken += 1

        if "move to " in user_action.lower():
            new_loc = user_action[8:].strip()
            current_location = new_loc

        desc, chars, rels = get_description_and_relationships(current_time, current_location, story_data, relationship_data)
        rel_str = "\n".join(rels)

        summary += f"At {current_time} min, user did '{user_action}'.\n"

        prompt = build_prompt(current_time, current_location, summary, user_action, desc, rel_str)

        response_text = get_story_from_openai(prompt)
        new_time, new_location, story_content, new_summary = parse_openai_response(response_text)

        # 모델 응답에서 받은 summary를 갱신
        if new_summary:
            summary = new_summary

        print("\nOutput\n")
        print(f"Current Time: {new_time}")
        print(f"Current Location: {new_location}")
        print("Story:")
        print(story_content)


        current_time = new_time
        current_location = new_location

        if current_time >= max_time:
            print("\nYou failed to solve the case before time ran out.")
            attempt += 1
            if attempt <= 3:
                max_time -= 10
                current_time = 0
                current_location = "1st floor entrance"
                summary = ""
                actions_taken = 0
                print(f"New Attempt: {attempt}, New Max Time: {max_time} minutes.\n")
            else:
                print("No more attempts left. Game Over.")
                break


if __name__ == "__main__":
    run_game_loop()
