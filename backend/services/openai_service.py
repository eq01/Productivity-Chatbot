from datetime import datetime

import openai
from backend.config import Config
from typing import List

openai.api_key = Config.OPENAI_API_KEY

class OpenAIService:
    def __init__(self):
        self.model = "gpt-4o-mini"
        self.conversation_history = [
            {"role": "system", "content": "You are a supportive productivity assistant"}
        ]

    def chat(self, message: str) -> str:
        """Handle general chat interactions"""

        self.conversation_history.append({"role": "system", "content": message})

        response = openai.chat.completions.create(
            model=self.model,
            messages=self.conversation_history
        )

        reply = response.choices[0].message.content
        self.conversation_history.append({"role": "system", "content": reply})

        return reply

    def generate_daily_summary(self, tasks: List[dict]) -> str:
        """Generate the daily summary of the tasks"""

        today = datetime.now().date()

        #today's tasks
        today_tasks = [t for t in tasks if t.get('due_date') == today.isoformat() or not t.get('due_date')]
        completed = [t for t in today_tasks if t['status'] == 'done']
        incomplete = [t for t in today_tasks if t['status'] != 'done']

        context = f"""Generate an encouraging end-of-day summary for the user.
**Tasks Completed Today ({len(completed)}):**
{self._format_tasks(completed)}

**Tasks Not Completed ({len(incomplete)}):**
{self._format_tasks(incomplete)}

**Total Tasks Today:** {len(today_tasks)}

Provide:
1. Congratulate them on what they accomplished
2. If tasks incomplete, gentle encouragement (no guilt!)
3. One insight about their productivity today
4. Motivational closing

Keep it warm, supportive, and concise (150-200 words)."""

        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a supportive "
                                              "productivity coach who celebrates wins and encourages growth."},
                {"role": "user", "content": context}
            ]
        )
        return response.choices[0].message.content

    def _format_tasks(self, tasks: List[dict]) -> str:
        if not tasks:
            return "None"

        formatted = []
        for task in tasks:
            task_str = f"- {task.get('title')}"
            if task.get('duration_est'):
                task_str += f" ({task['duration_est']} min"
            formatted.append(task_str)

        return "\n".join(formatted)
