# Contributing Guide

## Branch Naming
Use these formats when creating a new branch:
- `feat/<name>` — new feature
- `fix/<name>` — bug fix
- `chore/<name>` — maintenance or cleanup
- `docs/<name>` — documentation updates

Example:  
`chore/docs-deploy`

---

## Commit Messages (Conventional)
Use the following prefixes:

- `feat:`  new feature  
- `fix:`   bug fix  
- `docs:`  documentation  
- `chore:` maintenance  
- `refactor:` code improvement without feature change  

Examples:
- `feat: add login endpoint`
- `fix: incorrect JWT role check`
- `docs: update API usage in README`
- `chore: reorganize project folders`

---

## Local Setup (For All Contributors)
1. Create virtual environment  
2. Install requirements:  
3. Run migrations (if needed):  
4. Start server:  

---

## Pull Request Rules
Before creating a PR, ensure:

- [ ] Work is done in a branch (not main)
- [ ] Branch is up-to-date with `main`
- [ ] Code runs without errors
- [ ] API docs updated (`openapi.yaml`) if applicable
- [ ] README updated if needed
- [ ] No secrets committed
- [ ] Tests updated (if applicable)

---

## How to Contribute
1. Create a new branch  
2. Make your changes  
3. Commit using correct message format  
4. Push your branch  
5. Open a Pull Request  
6. Wait for review and approval  
