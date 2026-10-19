# Personal repos

My work and personal GitHub accounts are both signed in on my computer. When a
personal repo (under the GitHub account ChemaRocas) needs to be set up, it must be
set up this way. Before changing anything, tell me what you plan to do and why (this
file is the source), and wait for my authorization.

- The active GitHub account always stays the work one. Never switch it.
- Commits use my GitHub private email, never a work email, set for that repo only:
  `git config --local user.name "Josemaria Rocas"`
  `git config --local user.email "94923549+ChemaRocas@users.noreply.github.com"`
- The repo gets its own setting so it always pushes and pulls as ChemaRocas, whatever
  account is active:
  `git config --local credential.https://github.com.helper ''`
  `git config --local --add credential.https://github.com.helper '!f() { test "$1" = get && echo username=ChemaRocas && echo "password=$(gh auth token --user ChemaRocas)"; }; f'`
- Check it: with the work account active, `git push --dry-run` must succeed.

Why: 2026-10-19. Switching the active account to push a personal repo broke syncing the
work repo in VS Code. A name in the repo's address doesn't help: the login helper ignores it.
