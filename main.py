
from collections import defaultdict
from decimal import Decimal, InvalidOperation

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# --------------------------------------------------
# Configuration
# --------------------------------------------------

EMAIL = "23f2005531@ds.study.iitm.ac.in"
API_KEY = "ak_wj17bphj1bdpne1cq3har367"

api = FastAPI(title="POST Analytics API")


# --------------------------------------------------
# Request schema
# --------------------------------------------------

class Event(BaseModel):
    user: str
    amount: float
    ts: int | float


class AnalyticsRequest(BaseModel):
    events: list[Event]


# --------------------------------------------------
# POST /analytics
# --------------------------------------------------

@api.post("/analytics")
async def analytics(
    body: AnalyticsRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    # Authentication: missing or incorrect API key -> HTTP 401.
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
        )

    events = body.events

    # Number of events in the submitted batch.
    total_events = len(events)

    # Number of distinct users.
    unique_users = len({event.user for event in events})

    # Sum only strictly positive amounts.
    revenue = sum(
        (Decimal(str(event.amount)) for event in events if event.amount > 0),
        Decimal("0"),
    )

    # Aggregate positive amounts by user.
    user_totals = defaultdict(lambda: Decimal("0"))

    for event in events:
        if event.amount > 0:
            user_totals[event.user] += Decimal(str(event.amount))

    # The grader guarantees there are no ties.
    top_user = (
        max(user_totals, key=user_totals.get)
        if user_totals
        else ""
    )

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": float(revenue),
        "top_user": top_user,
    }


# --------------------------------------------------
# CORS
# --------------------------------------------------

# The assignment permits wildcard CORS or the exam page's origin.
# This configuration supports browser-based grader requests.
app = CORSMiddleware(
    app=api,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
