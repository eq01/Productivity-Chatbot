import streamlit as st
import requests
from datetime import datetime

API_BASE_URL = "http://localhost:5000/api"

# page title
st.set_page_config(page_title="Productivity Assistant", layout="wide")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {}
if 'day_complete' not in st.session_state:
    st.session_state.day_complete = False

# Some helpers

def add_task(user_input):
    response = requests.post(f"{API_BASE_URL}/tasks/", json={"input": user_input})
    return response.json()

def get_tasks():
    response = requests.get(f"{API_BASE_URL}/tasks/")
    return response.json()

def toggle_task(task, new_status):
    requests.put(f"{API_BASE_URL}/tasks/{task}", json={"status": new_status})

def get_summary():
    response = requests.get(f"{API_BASE_URL}/chat/daily-summary")
    return response.json()

with st.sidebar:
    st.title("Menu")

    st.subheader("Today's Progress")
    try:
        tasks = get_tasks()
        today = datetime.now().date().isoformat()
        today_tasks = []
        for t in tasks:
            t.get('due_date') == today;
            today_tasks.append(t)
        done_today = len([t for t in today_tasks if t['status'] == 'done'])
        total = len(today_tasks)

        st.metric("Tasks Done", f"{done_today}/{total}")
    except:
        pass

    st.divider()

    # show previous chats
    st.subheader("Recent Chats")
    st.caption("work in prog...")

    st.divider()

    st.subheader("Google Calendar")
    if st.button("Connect to Google Calendar"):
        st.info("coming soon")

# Main area

st.title("Productivity Assistant")

st.subheader("Chat with me!")

for message in st.session_state.chat_history:
    if message['role'] == 'user':
        st.chat_message("user").write(message['content'])
    else:
        st.chat_message("assistant").write(message['content'])

# input from chat
user_input = st.text_input("Ask me anything or enter a task")

if user_input:
    st.session_state.chat_history.append({'role': 'user', 'content': user_input})
    if any(word in user_input.lower() for word in ['add', 'task', 'remind', 'todo', 'tomorrow', 'today', 'schedule']):
        # is a tasks then
        try:
            result = add_task(user_input)
            task_data = result.get('task', result)

            response = f"Added: **{task_data['title']}**\n\n"
            if task_data.get('tasks_type'):
                category = {'personal': '🏠', 'work': '💼', 'quick': '⚡'}
                response += f"{category.get(task_data['task_type'])} Type: {task_data['task_type'].title()}\n"
            if task_data.get('duration_est'):
                response += f"Duration: {task_data['duration_est']} min\n"

            workload = result.get('workload_check', {})
            if workload.get('warnings'):
                response += "\n**Workload Warning**\n"
                for warning in workload['warnings']:
                    response += f"- {warning}\n"

            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
        except Exception as e:
            st.session_state.chat_history.append({'role': 'assistant', 'content': f"Error: {e}"})

    else:
        try:
            chat_response = requests.post(f"{API_BASE_URL}/chat/messages/", json={"content": user_input})
            reply = chat_response.json()
            st.session_state.chat_history.append({'role': 'assistant', 'content': reply})

        except Exception as e:
            st.sessions_state.chat_history.append({'role': 'assistant', 'content': f"Error: {e}"})

    st.rerun()

st.divider()

# Now we're on the to-do list section
st.subheader("Today's To-Do List")

try:
    tasks = get_tasks()
    today = datetime.now().date().isoformat()
    today_tasks = [t for t in tasks if t.get('due_date') == today or not t.get('due_date')]

    if not today_tasks:
        st.info("No tasks for today (lucky you). Add some tasks above!")
    else:
        for task in today_tasks:
            col1, col2, col3 = st.columns([1, 6, 2])

            with col1:
                checked = task['status'] == 'done'
                if st.checkbox("", value=checked, key=f"check_{task['id']}", label_visibility="collapsed"):
                    if not checked:
                        toggle_task(task[id], 'done')
                        st.rerun()
                    else:
                        if checked:
                            toggle_task(task[id], 'todo')
                            st.rerun()
            with col2:
                category = {'personal': '🏠', 'work': '💼', 'quick': '⚡'}
                task_text = f"{category.get(task.get('task_type', 'work'))} {task.title()}"
                if tasks.get('duration_est'):
                    task_text += f" Duration: {tasks['duration_est']} min"

                if task['status'] == 'done':
                    st.markdown(task_text, unsafe_allow_html=True)
                else:
                    st.markdown(task_text, unsafe_allow_html=True)

            with col3:
                # Priority indicator
                priority_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
                st.caption(f"{priority_emoji.get(task['priority'], '🟡')} {task['priority']}")
        st.divider()

        all_done = all(t['status'] == 'done' for t in tasks)

        if all_done:
            st.success("All tasks are complete! Great job!")

        if st.button("I'm Done for Today", type="primary", disabled=st.session_state.day_complete):
            st.session_state.day_complete = True
            st.rerun()

        if st.session_state.day_complete or all_done:
            with st.expander("Here's your end of day summary, great job today btw!", expanded=True):
                with st.spinner("Gimme a few seconds..."):
                    try:
                        summary_data = get_summary()
                        st.markdown(summary_data['summary'])

                        col1, col2 = st.columns(2)
                        col1.metric("Tasks Completed", len([t for t in today_tasks if t['status'] == 'done']))
                        col2.metric("Total Tasks", len(today_tasks))
                    except Exception as e:
                        st.error(e)

except Exception as e:
    st.error(f"Oops, looks like there was trouble loading your tasks: {e}")
