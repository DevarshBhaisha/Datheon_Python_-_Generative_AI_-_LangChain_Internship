
"""LangChain agent setup and readable tool/action trace."""
from __future__ import annotations

import os
from typing import Any

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import calculator_tool, file_reader_tool, web_search_tool


SYSTEM_PROMPT = """You are a careful multi-tool research assistant.

Use tools whenever they materially improve accuracy.
You may call multiple tools in sequence to solve multi-step requests.

Do not invent search results, file contents, calculations, or URLs.
For web claims, include useful source URLs from search results when available.
Explain important assumptions and show calculation results when using the calculator.

The local file tool can only read files from the project's data directory.

If a tool fails, explain the limitation and try a reasonable alternative when possible.

Give a concise, well-structured final answer.
Do not reveal private internal chain-of-thought.
Provide a brief summary of actions taken instead.

Avoid repeating searches unnecessarily.
Once sufficient information is retrieved, provide the final answer.
"""


def build_agent():
    """Initialize the Gemini-powered LangChain agent."""

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Configure it in your .env file."
        )

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    model = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0,
        max_retries=2,
    )

    agent = create_agent(
        model=model,
        tools=[
            web_search_tool,
            calculator_tool,
            file_reader_tool,
        ],
        system_prompt=SYSTEM_PROMPT,
    )

    return agent


def extract_readable_text(content: Any) -> str:
    """Extract readable text from string or structured message content."""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []

        for block in content:
            if isinstance(block, str):
                text_parts.append(block)

            elif isinstance(block, dict):
                if block.get("type") == "text":
                    text = block.get("text", "")
                    if text:
                        text_parts.append(str(text))

        return "\n".join(text_parts).strip()

    return str(content).strip() if content else ""


def run_agent(agent: Any, query: str) -> str:
    """Run the agent and display readable tool events and final answer."""

    print("\nAgent > Working on your request...")

    try:
        final_state = None

        for update in agent.stream(
            {"messages": [{"role": "user", "content": query}]},
            stream_mode="updates",
        ):
            for node_name, payload in update.items():

                if not isinstance(payload, dict):
                    continue

                messages = payload.get("messages", [])

                for message in messages:

                    # Display tool actions selected by the agent.
                    tool_calls = getattr(message, "tool_calls", None) or []

                    for call in tool_calls:
                        tool_name = call.get("name", "tool")
                        tool_args = call.get("args", {})

                        print(f"\n[Action] {tool_name}({tool_args})")

                    # Display tool results.
                    if getattr(message, "type", "") == "tool":
                        tool_name = getattr(message, "name", node_name)
                        content = extract_readable_text(
                            getattr(message, "content", "")
                        )

                        print(f"\n[Observation: {tool_name}]")
                        print(content[:1200])

                if "messages" in payload:
                    final_state = payload

        if final_state is None:
            raise RuntimeError("The agent did not return a final state.")

        messages = final_state.get("messages", [])

        final_message = next(
            (
                message
                for message in reversed(messages)
                if getattr(message, "type", "") == "ai"
                and getattr(message, "content", "")
                and not getattr(message, "tool_calls", None)
            ),
            None,
        )

        answer = (
            extract_readable_text(final_message.content)
            if final_message
            else "The agent did not return a final answer."
        )

        print("\nFinal answer")
        print("------------")
        print(answer)
        print()

        return answer

    except Exception as exc:
        message = f"Agent run failed: {exc}"
        print(f"\n{message}\n")
        return message
