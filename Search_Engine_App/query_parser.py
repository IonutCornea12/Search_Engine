def parse_query(raw_query):

    path_terms = []
    content_terms = []

    tokens = raw_query.split()
    for token in tokens:
        if token.startswith("path:"):
            term = token[len("path:"):]
            if term.strip():
                path_terms.append(term.strip())
        elif token.startswith("content:"):
            term = token[len("content:"):]
            if term.strip():
                content_terms.append(term.strip())
        else:
            # Fallback: treat as content
            if token.strip():
                content_terms.append(token.strip())

    return path_terms, content_terms