# SafeSpace: Finishing a Mental Health Support App

## What I Built

I finished SafeSpace, a FastAPI backend for private journaling, mood tracking,
supportive reflection, crisis-aware safety messaging, and categorized wellness
resources. Users can create an account, securely authenticate, manage only their
own entries, review mood patterns, and request a supportive reflection.

The AI feature is demo-safe by design: it can use the OpenAI Responses API when
configured, but a thoughtful local fallback keeps the core experience working
without a paid service or network connection. Reflections are explicitly
non-diagnostic and include a professional-care disclaimer.

## Demo

The demo begins in FastAPI's interactive documentation. I log in with seeded
demo data, create and edit a journal, add mood check-ins, view the mood summary,
generate a reflection, demonstrate crisis-safe messaging, and browse resources.
The final shot shows the automated smoke tests passing.

## The Comeback Story

The repository had a promising FastAPI and SQLAlchemy foundation, but it could
not start. Its entry point referenced missing modules, local configuration
required unused infrastructure, authentication routes and JWT payloads disagreed,
the main report route was empty, tests targeted nonexistent behavior, and the
README contained no setup path.

I preserved the useful architecture and turned it into a focused, stable product.
The result starts with SQLite and one command, keeps optional integrations truly
optional, validates input, protects user data, and supports a coherent recorded
demo from signup through reflection.

## My Experience with GitHub Copilot

GitHub Copilot helped accelerate the repetitive parts of the finish-up work:
drafting schemas, route shapes, ownership checks, test cases, and documentation.
I treated its output as a starting point rather than an authority. I reviewed
security boundaries, simplified infrastructure, tested the real API flow, and
kept the mental health language supportive and non-diagnostic. That combination
of assisted implementation and deliberate engineering judgment was especially
useful for turning an incomplete codebase into a dependable demo.
