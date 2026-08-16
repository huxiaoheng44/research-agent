TOOLS = [
    {
        "type": "function",
        "name": "search_uploaded_sources",
        "description": (
            "Search only the user's private uploaded source files. Use this "
            "tool when the user refers to uploaded documents, asks about their "
            "contents, or explicitly asks for an answer grounded in those files. "
            "Do not use it for current public information or general web knowledge."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The semantic search query to use when searching "
                        "the uploaded source files."
                    ),
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        # OpenAI-hosted tool.
        "type": "web_search",
        "search_context_size": "low",
    },
]
