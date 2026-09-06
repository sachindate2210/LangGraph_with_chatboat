from models.llm import llm
from database.save_step import save_step
from memory.session_memory import get_session_memory, add_session_memory
from agent.multi_graph_state import MultiAgentState

from tools.search_tool     import search_tool
from tools.wiki_tool       import wiki_tool
from tools.calculator_tool import calculator_tool
from tools.weather_tool    import weather_tool
from tools.database_tool   import database_tool
from tools.file_tool       import file_tool
from tools.tool_registry   import pdf_tool, text_tool, email_tool


# =================================================
# MEMORY RETRIEVAL NODE
# =================================================

def memory_retrieval_node(state: MultiAgentState) -> dict:

    memory = get_session_memory()
    save_step(state['session_id'], 1, "Memory Retrieval", memory or "No memory")
    return {"memory": memory}


# =================================================
# MANAGER NODE  — Ek baar chalta hai, task list banata hai
# =================================================

def manager_node(state: MultiAgentState) -> dict:

    response = llm.invoke(f"""
You are a Manager Agent. Analyze the user query and create a task list.

User Query: {state['query']}

Available agents (choose only what is needed):
- chat        → simple conversation, greetings (hi, hello, how are you, thank you, what is your name, general chat)
- research    → facts, news, general knowledge, internet search, Wikipedia
- calculator  → math calculations, python code execution
- weather     → weather of any city
- database    → SQL database queries
- file        → create PDF or text file
- email       → send email

Rules:
- If query is a simple greeting or casual conversation → use ONLY "chat"
- Choose ONE or MORE agents based on what the query needs
- Write them in ORDER of execution (e.g. research before email)
- Reply with COMMA SEPARATED list only
- Examples:
  "hi" → chat
  "hello" → chat
  "what is weather in Mumbai" → weather
  "who is PM of India" → research
  "find hotels and email me" → research,email

Your task list:""").content.strip().lower()

    # Parse task list
    valid = ["chat", "research", "calculator", "weather", "database", "file", "email"]
    tasks = [t.strip() for t in response.split(",") if t.strip() in valid]

    if not tasks:
        tasks = ["chat"]   # default fallback

    save_step(state['session_id'], 2, "Manager Plan", f"Tasks: {tasks}")

    return {"task_queue": tasks, "current_task": ""}


# =================================================
# ROUTER NODE  — Queue se next task uthata hai (No LLM)
# =================================================

def router_node(state: MultiAgentState) -> dict:

    queue = state.get("task_queue", [])

    if not queue:
        return {"current_task": "done"}

    next_task  = queue[0]
    remaining  = queue[1:]

    save_step(state['session_id'], 3,
              "Router", f"Running: {next_task} | Remaining: {remaining}")

    return {"current_task": next_task, "task_queue": remaining}


# =================================================
# CHAT NODE  — Simple conversation, no tools needed
# =================================================

def chat_node(state: MultiAgentState) -> dict:

    response = llm.invoke(f"""
You are a helpful AI assistant.
Have a natural conversation with the user.

Previous Memory:
{state['memory']}

User: {state['query']}
""").content

    save_step(state['session_id'], 4, "Chat Agent", response)
    return {"research_result": response}


# =================================================
# RESEARCH AGENT NODE
# =================================================

def research_agent_node(state: MultiAgentState) -> dict:

    try:
        raw = search_tool.run(state['query'])
        if not raw:
            raw = wiki_tool.run(state['query'])

        # LLM se format karwao — user ki query ke hisaab se
        result = llm.invoke(f"""
Based on the search results below, answer the user's query properly.
Format the answer clearly as the user requested.

User Query: {state['query']}

Search Results:
{raw}

Instructions:
- Answer exactly what the user asked
- Use bullet points if user asked for bullet points
- Be specific and clear
- If exact data is not available in search results, say so honestly
""").content

    except Exception as e:
        result = f"Research error: {str(e)}"

    save_step(state['session_id'], 4, "Research Agent", result)
    return {"research_result": result}


# =================================================
# CALCULATOR AGENT NODE
# =================================================

def calculator_agent_node(state: MultiAgentState) -> dict:

    try:
        expr = llm.invoke(
            f"Extract only the math expression from: {state['query']}\n"
            f"Reply with expression only. Example: 25 * 48"
        ).content.strip()

        result = calculator_tool.run(expr)
    except Exception as e:
        result = f"Calculation error: {str(e)}"

    save_step(state['session_id'], 4, "Calculator Agent", result)
    return {"calculation_result": result}


# =================================================
# WEATHER AGENT NODE
# =================================================

def weather_agent_node(state: MultiAgentState) -> dict:

    try:
        city = llm.invoke(
            f"Extract only the city name from: {state['query']}\n"
            f"Reply with city name only. Example: Mumbai"
        ).content.strip()

        result = weather_tool.run(city)
    except Exception as e:
        result = f"Weather error: {str(e)}"

    save_step(state['session_id'], 4, "Weather Agent", result)
    return {"weather_result": result}


# =================================================
# DATABASE AGENT NODE
# =================================================

def database_agent_node(state: MultiAgentState) -> dict:

    try:
        query = state['query'].strip()

        # Check karo — kya user ne SQL directly type kiya?
        sql_keywords = ['select', 'insert', 'update', 'delete', 'create', 'drop', 'alter']
        is_already_sql = any(query.lower().startswith(kw) for kw in sql_keywords)

        if is_already_sql:
            sql = query   # directly use karo
        else:
            sql = llm.invoke(
                f"Convert this to a PostgreSQL query: {query}\n"
                f"Rules:\n"
                f"- Reply with SQL only\n"
                f"- No markdown, no backticks, no explanation\n"
                f"- Just the raw SQL statement"
            ).content.strip()

        # Markdown code blocks hato agar LLM ne diye
        sql = sql.replace("```sql", "").replace("```", "").strip()

        result = database_tool.run(sql)
        result_str = str(result)

        # Result bada ho to file me save karo — browser freeze na ho
        if len(result_str) > 3000:
            filename = "db_result.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result_str)
            # Pehle 3 rows preview + download signal
            preview = result_str[:1000]
            result = (
                f"Query successful. Results are large — saved to file.\n\n"
                f"Preview (first few rows):\n{preview}\n\n"
                f"[DOWNLOAD_FILE:db_result.txt]"
            )
        else:
            result = result_str

    except Exception as e:
        result = f"Database error: {str(e)}"

    save_step(state['session_id'], 4, "Database Agent", result)
    return {"database_result": result}


# =================================================
# FILE AGENT NODE
# =================================================

def file_agent_node(state: MultiAgentState) -> dict:

    try:
        # Research result available ho to use karo
        content = state.get('research_result') or state['query']

        if "pdf" in state['query'].lower():
            result = pdf_tool.run(content)
        else:
            result = text_tool.run(content)

    except Exception as e:
        result = f"File error: {str(e)}"

    save_step(state['session_id'], 4, "File Agent", result)
    return {"file_result": result}


# =================================================
# EMAIL AGENT NODE
# =================================================

def email_agent_node(state: MultiAgentState) -> dict:

    try:
        body = state.get('research_result') or state['query']

        email_addr = llm.invoke(
            f"Extract only the email address from: {state['query']}\n"
            f"Reply with email address only."
        ).content.strip()

        result = email_tool.run({
            "receiver_email": email_addr,
            "body": body
        })
    except Exception as e:
        result = f"Email error: {str(e)}"

    save_step(state['session_id'], 4, "Email Agent", result)
    return {"email_result": result}


# =================================================
# FINAL RESPONSE NODE
# =================================================

def final_response_node(state: MultiAgentState) -> dict:

    results = []
    if state.get('research_result'):    results.append(state['research_result'])
    if state.get('calculation_result'): results.append(state['calculation_result'])
    if state.get('weather_result'):     results.append(state['weather_result'])
    if state.get('database_result'):    results.append(state['database_result'])
    if state.get('file_result'):        results.append(state['file_result'])
    if state.get('email_result'):       results.append(state['email_result'])

    final = "\n\n".join(results) if results else "Task completed."

    add_session_memory(f"AI: {final}")
    save_step(state['session_id'], 5, "Final Response", final)

    return {"final_answer": final}
