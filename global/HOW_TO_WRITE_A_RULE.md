# How to write a new rule

For me, or an agent helping me, when something about how I like to work should become
permanent. This file is a guide, not a rule: `install.py` doesn't install it.

## Where it goes

| Kind | Folder | Example |
|---|---|---|
| How to work with me | `global/rules/` | one step at a time, ask before editing |
| How to talk to me, or how I set things up | `global/general_instructions/` | acronyms, personal repos |
| A procedure an agent loads only when needed | `global/skills/<name>/SKILL.md` | gitignore audit |
| Only for one project | that project's `AGENTS.md` | its folder conventions |
| Only for one computer or one employer | never this repo: see the README, "Changing my instructions" | a company's required rule |

## The shape

One rule per file, named for what it does (`show-me-the-edits.md`, not `rule-7.md`):

```markdown
# <Title that states the rule>

<The rule, in plain words, written to the agent. Say what to do, and what not to.>

**Why:** <date: the incident that made it necessary, with enough detail that a reader
can judge edge cases.>

**How to apply:** <only if it's not obvious: when it applies, exceptions, how it relates
to other rules.>
```

- **Write it for any agent:** no tool names ("your file-editing feature", not a specific
  tool), unless the rule is about one tool.
- **Keep the why.** A rule without its reason gets bent or dropped the first time it's
  inconvenient. The date and incident are what let a future agent apply it well.
- **Derive, don't list.** If the rule depends on values that live elsewhere, point to the
  source instead of copying them.

## From idea to global rule

1. **Try it in one project first.** Save it as that project's note (an agent memory, or a
   line in the project's `AGENTS.md`) and work with it for a while.
2. **If it works and applies everywhere,** write it here in the shape above, remove the
   project-level copy (back it up first), and run `python3 global/install.py`.
3. **Check it loaded:** a new session in each agent should list it.
4. **When a rule changes,** update its file and add the new date and reason to its Why.
   When it's dropped, delete the file; the installer retires the installed copies.
