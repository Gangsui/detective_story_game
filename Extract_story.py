import json
import re

def parse_time_range(time_range_str):
    # time_range_str 예: "0 ~ 5 min action and setting"
    # 정규 표현식을 사용해 범위를 파싱
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
    # 1. current_time에 맞는 time segment 찾기
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
        # 해당하는 시간대가 없을 경우 빈 값 반환
        return "", [], []

    # 2. 해당 time segment에서 current_location에 있는 actions 추출
    characters_info = matched_segment.get("characters", [])
    location_descriptions = []
    characters_in_location = set()  # 해당 장소에서 발견된 인물들 저장

    for char_data in characters_info:
        name = char_data.get("name", "")
        actions = char_data.get("actions", [])
        for action in actions:
            locations = action.get("locations", [])
            if current_location in locations:
                # 해당 액션이 현재 장소에 있다면 description 수집
                desc = action.get("description", "")
                if desc:
                    location_descriptions.append(f"{name}: {desc}")
                # 이 인물이 현재 장소에 있음
                characters_in_location.add(name)

    # 3. relationship_data를 기반으로 해당 인물들의 role, personality 추출
    #    그리고 인물들 사이 관계도 필요한 경우 추출
    detailed_characters = []
    char_name_to_data = {}

    # relationship_data 구조:
    # {
    #   "characters": [
    #     {
    #       "name": ...,
    #       "role": ...,
    #       "personality": ...,
    #       "relationships": [
    #          {
    #             "characters": [...],
    #             "description": ...
    #          },
    #          ...
    #        ]
    #     },
    #     ...
    #   ]
    # }

    rel_characters = relationship_data.get("characters", [])
    for c in rel_characters:
        cname = c.get("name", "")
        if cname in characters_in_location:
            # 해당 캐릭터 정보 저장
            char_name_to_data[cname] = {
                "name": cname,
                "role": c.get("role", ""),
                "personality": c.get("personality", ""),
                "relationships": c.get("relationships", [])
            }

    # 4. 같은 장소에 여러 인물이 있으면 이들 사이의 relationship description 추출
    # characters_in_location에 있는 모든 조합을 확인해서 relationships에서 매칭되는 경우 가져오기
    characters_in_location_list = list(characters_in_location)
    relationship_descriptions = []
    for i in range(len(characters_in_location_list)):
        for j in range(i+1, len(characters_in_location_list)):
            char_a = characters_in_location_list[i]
            char_b = characters_in_location_list[j]
            # char_a, char_b 관계 체크
            # char_a의 relationship에서 char_b가 등장하는지 확인
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

    # detailed_characters 만들기
    for c in characters_in_location_list:
        cdata = char_name_to_data.get(c, {})
        detailed_characters.append({
            "name": cdata.get("name", c),
            "role": cdata.get("role", ""),
            "personality": cdata.get("personality", "")
        })

    # 최종 description은 location_descriptions를 합쳐서 하나의 텍스트로 만들거나, 리스트로 반환할 수 있다.
    final_description = "\n".join(location_descriptions)

    return final_description, detailed_characters, relationship_descriptions


# 예시 사용 방법:
# story.json 로드
# with open('story_English.json', 'r', encoding='utf-8') as f:
#     story_data = json.load(f)

# relationship.json 로드
# with open('relation.json', 'r', encoding='utf-8') as f:
#     relationship_data = json.load(f)

# current_time = 7
# current_location = "1st floor study"
# desc, chars, rels = get_description_and_relationships(current_time, current_location, story_data, relationship_data)

# print("Description:\n", desc)
# print("Characters at location:\n", chars)
# print("Relationships:\n", rels)
