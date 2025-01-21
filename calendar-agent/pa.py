from __future__ import annotations as _annotations
from dataclasses import dataclass
from datetime import datetime
from devtools import debug
from httpx import AsyncClient
from pydantic import BaseModel, ValidationError
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.ollama import OllamaModel
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


ollama_model = OllamaModel(
    model_name='mistral-nemo',
)

pa = Agent(
    model=ollama_model,
    retries=3,
    system_prompt=(
        'You are a professional and thorough personal assistant that helps his user to manage tasks and time.',
        'You help with various tasks:',
        'Task 1 - detect conflicting events in your user''s calendar',
        'Use the retrieve_events tool to retrieve all personal calendar events.',
        'Calendar events are conflicting, when they overlap at the same time. Use tool determine_calendar_events_overlap to determine whether two events overlap.',
        'When displaying result convert time from UTC to Central European Time with DST offset valid at that date.'
        ),
     deps_type=Deps,
)

@pa.tool
async def retrieve_events(ctx: RunContext) -> CalendarEventList:
    """Retrieve all calendar events. """    

    # with open('../.data/calendar-events.json', 'r') as file:
    #     source_events = json.load(file)
    #
    # result_events = [CalendarEvent(**event) for event in source_events]

    with open('../.data/calendar-events.json', 'r') as file:
        source_events = json.load(file)

    result_events = []
    for event in source_events:
        try:
            result_events.append(CalendarEvent(**event))
        except ValidationError as e:
            print(f"Error creating CalendarEvent: {e}")

    return CalendarEventList(events=result_events)

@pa.tool
async def determine_calendar_events_overlap(ctx: RunContext,event1: CalendarEvent, event2:CalendarEvent) -> bool:
    """Determine whether two calendar events overlap. One event is given with parameter event1 and the other with event2."""
    start1 = datetime.fromisoformat(event1.start)
    end1 = datetime.fromisoformat(event1.end)
    start2 = datetime.fromisoformat(event2.start)
    end2 = datetime.fromisoformat(event2.end)
    return max(start1, start2) < min(end1, end2) 

async def main():
    async with AsyncClient() as client:
        deps = Deps(
            client=client,
        )
        result = await pa.run(
            'Provide a list of conflicting calendar events.',
            deps=deps,
        )
        # debug(result)
        print(result.data)

if __name__ == "__main__":
    asyncio.run(main())
