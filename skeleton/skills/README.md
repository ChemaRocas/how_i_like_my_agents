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

## Registering a skill, so agents actually find it

A skill in this folder is **invisible to agents** until it's registered where they look:
an agent doesn't browse `skills/` on its own. (Learned the hard way: a session answered a
data question by guessing, because the skill that explained the data sat in an
unregistered folder.)

Register each skill with a link from each agent's project skills folder to the skill's
folder here, so there is still only one copy to edit:

| Agent | Link | Points to |
|---|---|---|
| Claude Code | `.claude/skills/<skill-name>` | `../../skills/<skill-name>` |
| Codex | `.agents/skills/<skill-name>` | `../../skills/<skill-name>` |

Check the agent's current documentation for its project skills folder before linking:
these locations change (if one moves, update the table above: the tests read it). Creating
a link can't go through the file editor, so tell me which links you'll create and wait for
my authorization. Also list the skill in the Read this first table in
[AGENTS.md](../AGENTS.md), for the task it serves.

`tests/test_skills_registered.py` fails if a skill here isn't linked for every agent in the
table, or if a link points to a skill that no longer exists.

**On Windows,** git may turn links into small text files unless the computer allows them
(Developer Mode on, and `git config core.symlinks true` before cloning). If the test fails
there right after cloning, that's the reason, not a missing registration.
