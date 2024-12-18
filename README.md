# detective_story_game

## Overview
- This game is a detective story game where the user prevents a murder or finds the culprit through deduction and choices.
- The game progresses based on time (0 minutes to 50 minutes) and location, where the user visits specific locations at specific times to gather clues or interact with NPCs to obtain information.
- The story dynamically changes based on the user's actions and interactions with Azure OpenAI (referred to as Gemma).
- OpenAI is provided with a story file (`json/story.json`) and a relationship file (`json/relationship.json`) in JSON format to generate appropriate narratives based on the user's commands and actions.
- The user has a total of 3 chances (timeline resets), and with each reset, the scenario start time decreases by 10 minutes (50 minutes → 40 minutes → 30 minutes).

## How to Play
1. When the game starts, `json/story.json` is loaded, and the initial situation (corresponding to the time range) is explained to the user.
2. The user can choose a location to move to from the presented list of locations. For example:
   - ['1st floor Kitchen', '1st floor Storage room', '1st floor entrance', '1st floor hallway', '1st floor kitchen', '1st floor study', '2nd floor Garden', "2nd floor Han Soo-min's room", "2nd floor Jung Yoo-jin's room", "2nd floor Lee Jae-hoon's room", "2nd floor Lee Jun-hyung's room", "2nd floor Park Hyun-woo's room", '2nd floor hallway', 'Basement', 'Garden', 'Kitchen', 'Secret passage', 'Security room']
3. As the user progresses time or moves locations, the appropriate JSON data for the time range and location is used to prompt Azure OpenAI. ChatGPT outputs the story development based on this information.
4. After the story progresses, a summary (a summary of the current play progress) is internally received from ChatGPT and saved. This summary is not directly shown to the user but is used to maintain context in the future.
5. The user decides the next action based on the story outcome. After about 3 repetitions, the scenario's time range decreases (0~40 → 0~30), and the same flow is repeated.
6. The game ends when the user identifies the murderer or prevents the murder.

