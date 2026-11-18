# Week 1: Project foundation and basic student data

## Code received
`backend/app/legacy/week1_part1_foundation.py`

This is the original Week 1, Part 1 implementation supplied by the project owner. It is retained as a complete source snapshot and has not been rewritten into the modular FastAPI implementation yet.

## What this code currently provides

1. **SQLite database connection**
   - Opens `study_planner.db` beside this Python file.
   - Returns rows that can be accessed by column name.
   - Enables SQLite foreign-key enforcement.

2. **Database initialization**
   - Creates profile, subjects, topics, assessments, availability, sessions and planner_settings tables.
   - Adds indexes for session date, topic and assessment lookups.
   - Includes a compatibility check to add `subject_limit` to older availability tables.

3. **Input validation helpers**
   - Non-empty text, bounded integers/floats, yes/no answers and date validation.
   - Date input is accepted as DD-MM-YYYY and stored as ISO YYYY-MM-DD.

4. **Flexible duration input**
   - Accepts hours, minutes, or combined hours and minutes.
   - Can enforce an optional maximum duration.

5. **Profile and plan settings helpers**
   - Reads the single profile row and planner settings row.
   - Saves plan start date and number of plan days.

6. **Time conversion and formatting**
   - Converts hours to minutes and minutes to hours.
   - Formats durations such as `1h 30m`.

## What to write next

- Continue sending the remaining Week 1 code (if any).
- The next section should add profile creation/update and the first subject/topic input or management functions, if those are part of your original implementation.
- Do not duplicate database initialization; extend the existing schema only when a later feature needs new columns/tables.

## Important integration note

The current file is a procedural SQLite/CLI foundation. The wider project scaffold also contains a modular FastAPI + React architecture. For now, preserve this file as the working original. Once all Weeks 1–8 code is received, we can migrate its database and business logic into the modular backend without losing behavior.

## Current archive status
See  for the verified status of this milestone. The local  is a workspace template; the integrated implementation belongs in the backend/frontend destination listed in .

## Current archive status

See `../../docs/IMPLEMENTATION_STATUS.md` for the verified status of this milestone. The local `implementation.py` is a workspace template; the integrated implementation belongs in the backend/frontend destination listed in `../WEEK_TO_CODE_MAP.md`.
