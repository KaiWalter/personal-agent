from __future__ import annotations as _annotations
from dataclasses import dataclass
from datetime import datetime
from devtools import debug
from httpx import AsyncClient
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from typing import List
import asyncio
import json
import logfire

logfire.configure(send_to_logfire='if-token-present')

@dataclass
class Deps:
    client: AsyncClient

class CalendarEvent(BaseModel):
    id: str
    organizer: str
    subject: str
    start: str
    end: str
    showAs: str

class CalendarEventList(BaseModel):
    events: List[CalendarEvent]


pa = Agent(
    'openai:gpt-4o',
    # 'gemini-1.5-flash',
    # Register a static system prompt using a keyword argument to the agent.
    # For more complex dynamically-generated system prompts, see the example below.
    retries=3,
    system_prompt=(
        #'Be concise, reply with one sentence when asked a specific question.',
        # 'When asked to list, list in CSV format.',
        'Use the retrieve_events tool to retrieve all personal calendar events.',
        'Calendar events are conflicting, when they overlap at the same time. Use the given tool to determine whether two events overlap.',
        ),
     deps_type=Deps,
)

@pa.tool
async def retrieve_events(ctx: RunContext) -> CalendarEventList:
    """Get all personal calendar events. """    

    with open('../.data/calendar-events.json', 'r') as file:
        source_events = json.load(file)

    result_events = [CalendarEvent(**event) for event in source_events]
    return CalendarEventList(events=result_events)

@pa.tool
async def determine_calendar_events_overlapp(ctx: RunContext,event1: CalendarEvent, event2:CalendarEvent) -> bool:
    """Determine whether two calendar events overlap. One event is given with parameter event1 and the other with event2."""
    start1 = datetime.fromisoformat(event1.start)
    end1 = datetime.fromisoformat(event1.end)
    start2 = datetime.fromisoformat(event2.start)
    end2 = datetime.fromisoformat(event2.end)
    return max(start1, start2) <= min(end1, end2) 

async def main():
    async with AsyncClient() as client:
        deps = Deps(
            client=client,
        )
        result = await pa.run(
            # 'Provide a list of conflicting calendar items.',
            'Give me the first conflicting calendar event.',
            # 'Provide a list of calendar events',
            deps=deps,
        )
        debug(result)
        print(result.data)

if __name__ == "__main__":
    asyncio.run(main())
