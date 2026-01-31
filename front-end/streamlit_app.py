import streamlit as st
import requests
from datetime import datetime

API_BASE_URL = "http://localhost:5000/api"

# page title
st.set_page_config(page_title="Productivity Assistant", layout="wide")

st.title("🤖 Productivity Assistant")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'day_complete' not in st.session_state:
    st.session_state.day_complete = False

# Some helpers

def delete_tasks(task_id):
    """Delete tasks"""
    try:
        response = requests.delete(f"{API_BASE_URL}/tasks/{task_id}")
        return response.json()
    except Exception as e:
        print(f"Delete error: {e}")
        return {'error': str(e)}

def add_task(user_input, sync_calendar=False):
    """Add task using natural language"""
    response = requests.post(
        f"{API_BASE_URL}/tasks/",
        json={"input": user_input, "sync_calendar": sync_calendar}
    )
    return response.json()

def check_calendar_auth():
    """Check Google Calendar auth status"""
    try:
        response = requests.get(f"{API_BASE_URL}/calendar/status")
        return response.json()
    except:
        return {'authenticated': False}

def get_calendar_auth_url():
    """Get Google Calendar auth url"""
    try:
        response = requests.get(f"{API_BASE_URL}/calendar/auth")
        return response.json()
    except:
        return {'auth_url': None}


def find_matching_task(user_input, tasks):
    """Use AI to find which task the user wants to delete"""
    try:
        import openai
        import json

        # Create task list for AI
        task_list = []
        for i, task in enumerate(tasks):
            task_list.append({
                'index': i,
                'id': task['id'],
                'title': task['title'],
                'due_date': task.get('due_date'),
                'due_time': task.get('due_time')
            })

        # Ask AI to match
        response = requests.post(
            f"{API_BASE_URL}/chat/match-task",
            json={
                "user_input": user_input,
                "tasks": task_list
            }
        )

        result = response.json()
        if result.get('matched_index') is not None:
            return tasks[result['matched_index']]
        return None

    except Exception as e:
        print(f"AI matching error: {e}")
        # Fallback: simple keyword matching
        user_lower = user_input.lower()
        for task in tasks:
            if task['title'].lower() in user_lower or user_lower in task['title'].lower():
                return task
        return None

def get_calendar_events():
    """Get upcoming calendar events"""
    try:
        response = requests.get(f"{API_BASE_URL}/calendar/events")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return {'events': []}
    except Exception as e:
        print(f"Error getting events: {e}")
        return {'events': []}

def get_tasks():
    response = requests.get(f"{API_BASE_URL}/tasks/")
    return response.json()

def toggle_task(task, new_status):
    requests.put(f"{API_BASE_URL}/tasks/{task}", json={"status": new_status})

def get_summary():
    response = requests.get(f"{API_BASE_URL}/chat/daily-summary")
    return response.json()

# sidebar section
with st.sidebar:
    st.title("Menu")

    st.subheader("Today's Progress")
    try:
        tasks = get_tasks()
        today = datetime.now().date().isoformat()
        today_tasks = []
        for t in tasks:
            if t.get('due_date') == today:
                today_tasks.append(t)
        done_today = len([t for t in today_tasks if t['status'] == 'done'])
        total = len(today_tasks)

        progress = (done_today / total * 100) if total > 0 else 0

        st.metric("Tasks Completed", f"{done_today}/{total}")
        st.progress(progress / 100)

        if progress == 100 and total > 0:
            st.success("🎉 All done!")
        elif progress >= 50:
            st.info("💪 Halfway there!")
    except:
        st.caption("Add some tasks to see progress!")

    st.divider()

    # show previous chats
    st.subheader("Recent Chats")
    st.caption("work in prog...")

    st.divider()

    st.subheader("Google Calendar")
    calendar_status = check_calendar_auth()

    if calendar_status.get('authenticated'):
        st.success("Connected!")

        try:
            events_data = get_calendar_events()
            event_count = len(events_data.get('events', []))
            st.caption(f"{event_count} upcoming event(s)")
        except:
            pass

        if st.button("Refresh Events"):
            st.rerun()

    else:
        st.warning("Not Connected")
        if st.button("Connect to Google Calendar"):
            auth_data = get_calendar_auth_url()
            auth_url = auth_data.get('auth_url')
            if auth_url:
                st.markdown(f"[Click here to authorize]({auth_url})")
                st.caption("After authorizing, refresh the page!")
            else:
                st.error("Could not get authorization URL")


# Main area

st.title("Productivity Assistant")

st.title("🤖 Productivity Assistant")

# Add a quick start guide
with st.expander("❓ Quick Start Guide", expanded=False):
    st.markdown("""
    ### 🎯 How to Use This App

    **1️⃣ Add Tasks:**
    - Type naturally: "Buy milk tomorrow" or "Meeting Friday at 2pm"
    - The AI understands dates, times, and priorities

    **2️⃣ Calendar Sync (Optional):**
    - Connect Google Calendar in the sidebar
    - Enable "Auto-sync" to create calendar events

    **3️⃣ Track Progress:**
    - Check off tasks as you complete them
    - Click "I'm Done for Today" for a summary

    **4️⃣ Stay Balanced:**
    - The app warns if you're overloading a day
    - Suggestions help you spread out work
    """)

st.subheader("Chat with me!")

for message in st.session_state.chat_history:
    if message['role'] == 'user':
        st.chat_message("user").write(message['content'])
    else:
        st.chat_message("assistant").write(message['content'])

calendar_status = check_calendar_auth()
if calendar_status.get('authenticated'):
    sync_to_calendar = st.checkbox(
        "Auto-sync tasks to Google Calendar",
        value=False,
        help="Tasks with dates will automatically create calendar events. "
             "Deleting a task will also delete the event from your calendar!"
    )
else:
    sync_to_calendar = False
    st.caption("Connect Google Calendar in sidebar to enable auto-sync")

# input from chat
user_input = st.chat_input("Ask me anything or enter a task")

if user_input:
    st.session_state.chat_history.append({'role': 'user', 'content': user_input})

    if any(word in user_input.lower() for word in ['delete', 'remove', 'cancel', 'clear']):
        with st.spinner("Finding task to delete..."):
            try:
                # Get all tasks
                all_tasks = get_tasks()

                if not all_tasks:
                    response = "You don't have any tasks to delete."
                else:
                    # Use AI to find matching task
                    task_to_delete = find_matching_task(user_input, all_tasks)

                    if task_to_delete:
                        delete_tasks(task_to_delete['id'])
                        response = f"✅ Deleted: **{task_to_delete['title']}**"
                        if task_to_delete.get('calendar_event_id'):
                            response += "\n📅 Also removed from Google Calendar"
                    else:
                        response = "❌ Couldn't find a matching task. Try being more specific or use the 🗑️ button."

                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            except Exception as e:
                st.session_state.chat_history.append({'role': 'assistant', 'content': f"Error: {e}"})

        st.rerun()
    elif any(word in user_input.lower() for word in ['add', 'task', 'remind', 'todo', 'tomorrow', 'today', 'schedule']):
        # is a task then
        with st.spinner("Creating task..."):
            try:
                result = add_task(user_input, sync_to_calendar)
                task_data = result.get('task', result)

                if 'error' in result:
                    st.error(f"❌ Couldn't create task: {result['error']}")
                    st.info("💡 Try: 'Buy groceries tomorrow' or 'Meeting at 2pm Friday'")
                else:
                    response = f"Added: **{task_data['title']}**\n\n"
                if task_data.get('task_type'):
                    category = {'personal': '🏠', 'work': '💼', 'quick': '⚡'}
                    response += f"{category.get(task_data['task_type'])} Type: {task_data['task_type'].title()}\n"
                if task_data.get('duration_est'):
                    response += f"Duration: {task_data['duration_est']} min\n"

                if sync_to_calendar and task_data.get('due_date'):
                    with st.spinner("📅 Syncing to Google Calendar..."):

                        import time
                        time.sleep(0.5)
                        response += "\n✅ Synced to Google Calendar!\n"

                workload = result.get('workload_check', {})
                if workload.get('warnings'):
                    response += "\n**Workload Warning**\n"
                    for warning in workload['warnings']:
                        response += f"- {warning}\n"

                st.session_state.chat_history.append({'role': 'assistant', 'content': response})

            except requests.exceptions.ConnectionError:
                st.error("🔌 Can't reach the server. Is your backend running?")
                st.code("cd backend && python app.py", language="bash")
            except Exception as e:
                st.error(f"❌ Something went wrong: {e}")
                st.info("💡 Try refreshing the page or restarting the backend")

    else:
        try:
            chat_response = requests.post(f"{API_BASE_URL}/chat/message/", json={"content": user_input})
            reply = chat_response.json()
            st.session_state.chat_history.append({'role': 'assistant', 'content': reply})

        except Exception as e:
            st.session_state.chat_history.append({'role': 'assistant', 'content': f"Error: {e}"})

    st.rerun()

st.divider()

# Now we're on the to-do list section
st.subheader("Today's To-Do List")

try:
    tasks = get_tasks()
    today = datetime.now().date().isoformat()
    today_tasks = [t for t in tasks if t.get('due_date') == today or not t.get('due_date')]

    if not today_tasks:
        st.info("No tasks for today (lucky you). Add some tasks below!")
        with st.expander("💡 How to add tasks", expanded=False):
            st.markdown("""
            Try these examples:
            - "Buy groceries tomorrow"
            - "Team meeting Friday at 2pm"
            - "Call dentist next week"
            - "Urgent: finish report by 5pm"

            The AI will understand natural language and set dates, times, and priorities automatically!
            """)
    else:
        for task in today_tasks:
            col1, col2, col3, col4 = st.columns([1, 5, 2, 1])

            with col1:
                checked = task['status'] == 'done'
                new_checked = st.checkbox("", value=checked, key=f"check_{task['id']}", label_visibility="collapsed")
                if new_checked != checked:
                    new_status = 'done' if new_checked else 'todo'
                    toggle_task(task['id'], new_status)
                    st.rerun()
            with col2:
                category = {'personal': '🏠', 'work': '💼', 'quick': '⚡'}
                task_text = f"{category.get(task.get('task_type', 'work'))} {task['title']}"
                if task.get('duration_est'):
                    task_text += f" Duration: {task['duration_est']} min"

                if task['status'] == 'done':
                    st.markdown(task_text, unsafe_allow_html=True)
                else:
                    st.markdown(task_text, unsafe_allow_html=True)
                if task.get('calendar_event_id'):
                    st.caption("Synced to Google Calendar!")

            with col3:
                # Priority indicator
                priority_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
                st.caption(f"{priority_emoji.get(task['priority'], '🟡')} {task['priority']}")

            with col4:
                if st.button("🗑️", key=f"delete_{task['id']}", help="Delete task"):
                    delete_tasks(task['id'])
                    st.success("Task deleted!")
                    st.rerun()
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
                        st.success("✅ Summary ready!")
                        st.markdown(summary_data['summary'])

                        col1, col2, col3 = st.columns(3)

                        completed = len([t for t in today_tasks if t['status'] == 'done'])
                        total = len(today_tasks)
                        completion_rate = (completed / total * 100) if total > 0 else 0

                        col1.metric("✅ Completed", completed)
                        col2.metric("📋 Total Tasks", total)
                        col3.metric("📈 Completion Rate", f"{completion_rate:.0f}%")

                    except Exception as e:
                        st.error(f"❌ Couldn't generate summary: {e}")

except Exception as e:
    st.error(f"Oops, looks like there was trouble loading your tasks: {e}")

# Calendar Events Section
st.divider()

if check_calendar_auth().get('authenticated'):
    with st.expander("Upcoming Calendar Events", expanded=False):
        with st.spinner("Loading events..."):
            try:
                events_data = get_calendar_events()
                events = events_data.get('events', [])

                if not events:
                    st.info("No upcoming events found")
                    st.caption("💡 Enable calendar sync when creating tasks to see them here!")
                else:
                    st.caption(f"Showing upcoming events: {len(events)}")

                    for event in events:
                        col1, col2 = st.columns([5, 1])
                        with col1:
                            st.markdown(f"{event['summary']}")

                            start_time = event['start_time']
                            try:
                                if 'T' in start_time:
                                    from datetime import datetime
                                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                                    formatted_time = dt.strftime('%b %d at %I:%M %p')
                                else:
                                    formatted_time = f"{start_time} (All day)"
                            except:
                                formatted_time = start_time

                            st.caption(f"🕒 {formatted_time}")

                        with col2:
                            st.caption("📅")

                        st.divider()

            except Exception as e:
                st.error(f"Error loading events: {e}")
