session_memory = []


def add_session_memory(message):

    session_memory.append(message)


def get_session_memory():

    return "\n".join(session_memory)