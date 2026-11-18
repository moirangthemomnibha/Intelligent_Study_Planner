# Development guide

1. Start with data models and plain Python functions.
2. Write tests for priority and scheduling calculations before adding UI.
3. Keep routers thin: no complex algorithm should live inside a route function.
4. Store dates as ISO-compatible date/datetime values and define the student's timezone.
5. Store planned sessions separately from actual session outcomes.
6. Make rescheduling deterministic where possible; record why sessions moved.
7. Build AI recommendations only after enough reliable history exists.
8. For an agent, define a small set of allowed tools, validate arguments, log actions and require confirmation for high-impact changes.
