from langchain_core.tools import Tool

def calculator(expression):

    try:
        result = eval(expression)
        return str(result)

    except Exception as e:
        return str(e)

calculator_tool = Tool(
    name="Calculator",
    func=calculator,
    description="Math calculations"
)