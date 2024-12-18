# detective_story_game

## 전체 개요
- 이 게임은 탐정 스토리 게임으로, 사용자가 추리와 선택을 통해 살인을 막거나 범인을 찾아내는 흐름을 갖는다.
- 게임은 시간(0분~50분)과 장소를 기반으로 진행되며, 사용자는 특정 시간대에 특정 장소를 방문해서 사건의 단서를 얻거나 NPC와 대화를 통해 정보를 파악한다.
- 사용자가 이야기 속 사건들을 파악하고 선택한 행동에 따라 스토리가 Azure OpenAI(이하 Gemma)와의 상호작용으로 동적으로 변한다.
- OpenAI 에게는 JSON형태의 스토리 파일(`json/story.json`)과 관계 파일(`json/relationship.json`)을 전달하여, 사용자의 명령과 행동에 따라 적합한 서술을 생성하게 한다.
- 사용자는 총 3번의 기회(타임라인 리셋)가 있으며, 각 리셋 시 시나리오 시작 시간이 10분씩 줄어든다(50분 → 40분 → 30분 식).

## 진행 방식
1. 게임을 시작하면 `json/story.json`을 로드하고 초기 상황(time range에 해당하는)의 스토리를 사용자에게 설명.
2. 사용자는 제시된 장소 목록 중에서 이동할 위치를 선택할 수 있다. 예:
   - ['1st floor Kitchen', '1st floor Storage room', '1st floor entrance', '1st floor hallway', '1st floor kitchen', '1st floor study', '2nd floor Garden', "2nd floor Han Soo-min's room", "2nd floor Jung Yoo-jin's room", "2nd floor Lee Jae-hoon's room", "2nd floor Lee Jun-hyung's room", "2nd floor Park Hyun-woo's room", '2nd floor hallway', 'Basement', 'Garden', 'Kitchen', 'Secret passage', 'Security room']
3. 사용자가 시간을 진행시키거나 장소를 이동하며 선택한 액션에 따라 해당 시점(time_range)과 장소(location)에 맞는 JSON 데이터를 사용해 Azure OpenAI에 프롬프트를 전달. ChatGPT는 해당 정보를 토대로 스토리 전개를 출력한다.
4. 스토리 진행 후, 내부적으로 summary(현재까지 플레이의 진행 상황 요약)를 ChatGPT로부터 받아 저장하되, 이 summary는 사용자에게 직접 보여주지 않는다. 다만 이 요약 정보는 추후 맥락 유지에 사용된다.
5. 사용자는 스토리 결과를 보고 다음 행동을 결정한다. 3회 정도 반복한 후, 시나리오의 시간 범위가 줄어들고(0~40 → 0~30), 다시 같은 흐름을 반복한다.
6. 최종적으로 사용자가 살인자를 특정하거나, 살인을 막으면 게임 종료.