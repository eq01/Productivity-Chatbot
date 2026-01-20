import openai
import json
from datetime import datetime, timedelta
from backend.config import Config

openai.api_key = Config.OPENAI_API_KEY

class NLPParser:
    """Parse natural language into structured task data"""

    @staticmethod
    def parse_task(usr_input: str) -> dict:
        """Uses OpenAI API to parse natural language into structured task data"""

        functions = [
            {
                "name": "create_task",
                "description": "Extract task information from natural language input",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The main task title/description"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in YYYY-MM-DD format. Parse relative dates like 'tomorrow', "
                                           "'next Monday', 'in 3 days'"
                        },
                        "due_time": {
                            "type": "string",
                            "description": "Due time in HH:MM format (24-hour). Parse times like '3pm', 'at noon', "
                                           "'in the morning'"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Task priority based on urgency words like 'urgent', 'important', 'ASAP'"

                        },
                        "task_type": {
                            "type": "string",
                            "enum": ["personal", "work", "quick"],
                            "description": "Type: 'personal' for errands/self-care, 'work' for job/school, 'quick' for "
                                           "tasks under 10 minutes"

                        },
                        "duration_estimate": {
                            "type": "string",
                            "description": "Estimated duration in minutes. Parse from phrases like '30 minutes', '2 hours', "
                                           "'quick task' (5-10 min)"
                        }
                    },
                    "required": ["title"]
                }

            }
        ]

        today = datetime.now()
        sys_message = f"""You are a task parser. Current date is {today.strftime('%Y-%m-%d')} ({today.strftime('%A')}).
Parse the user's input into structured task data.

Guidelines:
- Extract the main action/task as the title
- Parse relative dates: 'tomorrow' = {(today + timedelta(days=1)).strftime('%Y-%m-%d')}, 'next week' = add & days
- Parse times: '3pm' = '15:00', 'noon' = '12:00', 'morning' = '9:00'
- Determine priority: 'urgent'/'ASAP'/'important' = high, otherwise medium
- Classify task_type:
  * 'personal' - personal errands, self-care, hobbies
  * 'work' - job tasks, school assignments, meetings
  * 'quick' - any task under 10 minutes
- Estimate duration in minutes (quick=5-10, short=15-30, medium=45-90, long=120+)
- If no date/time/duration specified, leave those fields out"""
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": sys_message},
                    {"role": "user", "content": usr_input}
                ],
                functions=functions,
                function_call={"name": "create_task"}
            )

            function_call = response.choices[0].message.function_call
            parsed_data = json.loads(function_call.arguments)

            return parsed_data

        except Exception as e:
            print(f"NLP Parse error: {e}")
            return {
                "title": usr_input,
                "priority": "medium",
                "task_type": "personal"
            }