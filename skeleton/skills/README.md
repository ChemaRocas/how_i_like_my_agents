# skills/

Skills for this project only: packaged knowledge or procedures an agent loads when it needs
them (how a data source behaves, how to build a recurring report), instead of reading
everything every session. Skills that apply to every project live in my global setup, not
here.

One folder per skill, with a `SKILL.md` inside:

```
skills/<skill-name>/SKILL.md
```

## Suggested shape (a suggestion, not a template)

Skills vary a lot in what they do, so there is no required structure. Write each one in
whatever shape fits it. Some things that have worked well:

- **Frontmatter** with a `name` and a `description` that says when to use the skill, and
  when not to. Agents decide whether to load a skill from its description alone, so it
  carries the trigger words.
- **Traps:** mistakes that are easy to make with this subject, and how to avoid them.
- **Known quirks, don't fix:** things that look wrong but are deliberate, with the reason,
  so nobody "corrects" them.
- **Examples** of a correct result, when the output has a precise form.

## Making a skill available to your agent

Agents look for skills in their own folders (for example `.claude/skills/` or
`.agents/skills/`). Keep the source here and, the first time you need one, tell me which
agent folder it should also go in, and wait for my authorization before linking or copying
it there.
