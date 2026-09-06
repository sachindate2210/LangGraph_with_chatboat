from typing import TypedDict, List


class MultiAgentState(TypedDict):

    query:              str
    session_id:         str
    memory:             str

    task_queue:         List[str]   # ["research", "file"] — Manager banata hai
    current_task:       str         # Router decide karta hai

    research_result:    str
    calculation_result: str
    weather_result:     str
    database_result:    str
    file_result:        str
    email_result:       str

    final_answer:       str
