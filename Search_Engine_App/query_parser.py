import shlex

def parse_query(raw_query):
    path_terms = []
    content_terms = []

    try:
        tokens = shlex.split(raw_query)
    except ValueError as e:
        print(f"[QueryParser Error] {e}")
        tokens = raw_query.split()

    current_type = None
    buffer = ""

    for token in tokens:
        if token.startswith("path:"):
            if current_type == "path" and buffer:
                path_terms.append(buffer.strip())
            elif current_type == "content" and buffer:
                content_terms.append(buffer.strip())
            buffer = token[len("path:"):]
            current_type = "path"

        elif token.startswith("content:"):
            if current_type == "path" and buffer:
                path_terms.append(buffer.strip())
            elif current_type == "content" and buffer:
                content_terms.append(buffer.strip())
            buffer = token[len("content:"):]
            current_type = "content"

        else:
            if current_type:
                buffer += " " + token
            else:
                content_terms.append(token.strip())

    if current_type == "path" and buffer:
        path_terms.append(buffer.strip())
    elif current_type == "content" and buffer:
        content_terms.append(buffer.strip())

    final_content_terms = []
    for content in content_terms:
        final_content_terms.extend(content.split())

    return path_terms, final_content_terms