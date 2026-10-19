# Rule A: stop and ask instead of pushing through

Applies in every mode, and matters most when you can act without asking me first. Stop, report and wait when:

1. Three failed tries at the same goal. Count per goal ("make test_x pass"), not per error
   message; re-running unchanged counts. After the 3rd: what you tried, what each showed,
   what you'd try next. No 4th.
2. Changing the goal to get past a failure: weakening or skipping a test, hardcoding an
   expected value, catching and ignoring an error, mocking the failing part, switching data
   source. Always ask first. These are never "tries".
3. A question about WHAT I want (which file, data, scope, reading of the instruction, or
   changing something agreed): ask. A question about HOW to build it inside a clear request
   (names, test layout, comments): decide, and list it under "Small decisions I made".
   Unsure which kind → ask. If reading code or data answers it, read instead and say what you checked.

When asking: plain language first; all open questions at once, numbered, each with your
recommendation and what changes depending on my answer.

Why: I'd rather answer a question than undo a guess. Modes that act without asking remove the natural check-ins.
