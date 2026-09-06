from langchain_core.tools import Tool

def read_file(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

file_tool = Tool(
    name="FileReader",
    func=read_file,
    description="Read text files"
)