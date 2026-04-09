# AGENTS.md

## Project Structure

```
/frontend    - React 19 + Vite + TypeScript + @xyflow/react (node-based UI)
/backend     - FastAPI + SQLite (aiosqlite) + multiple LLM providers
/openspec    - Spec-driven development artifacts
/.opencode   - OpenCode skills and commands
```

## Developer Commands

**Backend:**
```ps1
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```ps1
cd frontend
npm install
npm run dev
```

**Linting/Typecheck:**
```ps1
cd frontend && npm run lint
cd frontend && npm run build  # runs tsc -b && vite build
```

## Important Notes

- `.agents` folder is NOT versioned (high volume). Enable full automation with:
  ```ps1
  npx antigravity-awesome-skills --path .agents/skills
  ```
- Backend runs on `http://localhost:8000`, frontend on `http://localhost:5173`
- Backend supports multiple LLM providers: OpenAI, Google (Gemini), Anthropic, agno
- OpenCode skills are in `.opencode/skills/` directory
- Openspec workflow uses `.openspec.yaml` files in change directories