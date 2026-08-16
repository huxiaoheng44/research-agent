TOOLS = [
    {
        "type": "function",
        "name": "search_uploaded_sources",
        "description": (
            "Search the user's uploaded source files for information "
            "relevant to the research request. Use this tool when the "
            "question may depend on information contained in uploaded files."
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
    }
]