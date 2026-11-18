# Planning engine

This folder contains pure Python algorithms, independent from FastAPI and the database.
- `priority.py`: score a topic based on urgency, difficulty, weakness and remaining work.
- `scheduler.py`: allocate ranked topics to available study minutes over a planning horizon.
- `constraints.py`: check availability, session length and deadline constraints.

Write unit tests before connecting this engine to API routes.
