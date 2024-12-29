from __future__ import annotations as _annotations
from dataclasses import dataclass
from devtools import debug
from httpx import AsyncClient
from pydantic_ai import Agent, RunContext
from typing import Any
import asyncio
import logfire

logfire.configure(send_to_logfire='if-token-present')

@dataclass
class Deps:
    client: AsyncClient

pa = Agent(
    'gemini-1.5-flash',
    # Register a static system prompt using a keyword argument to the agent.
    # For more complex dynamically-generated system prompts, see the example below.
    system_prompt=('Be concise, reply with one sentence when asked a specific question.',
                   'When asked to list, list in CSV format.'
                   'Use the retrieve_events tool to retrieve personal calendar events.',
                   'Calendar events are conflicting, when they overlap at the same time.'
                   ),
     deps_type=Deps,
)

@pa.tool_plain
async def retrieve_events() -> str:
    """Get personal calendar events.

    Args:
        ctx: The context.
    """    

    with open('../.data/calendar-events.json', 'r') as file:
        file_content = file.read()
    return file_content


async def main():
    async with AsyncClient() as client:
        deps = Deps(
            client=client,
        )
        result = await pa.run(
            # 'Provide a list of conflicting calendar items.',
            'Provide a list of calendar items.',
            deps=deps,
        )
        debug(result)
        print('Response:', result.data)

if __name__ == "__main__":
    asyncio.run(main())
