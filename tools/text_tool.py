def create_text_file(content, filename="output.txt"):

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Text File Created: {filename}"