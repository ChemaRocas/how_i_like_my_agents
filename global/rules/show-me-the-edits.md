# Show me the edits

I want to see every change you make to a file. Make file changes with your tool's
file-editing feature, the one that shows me what changed, never through terminal commands
(sed, inline scripts, `echo > file`, heredocs). Use the terminal to run and test things,
not to edit them.

If a change really can't go through the editor (for example, generating many files at
once), say so before doing it, and afterwards show me what changed.

Why: 2026-10-19. Edits made through terminal scripts showed only as "ran a command", so I
couldn't check what had actually changed in each step.
