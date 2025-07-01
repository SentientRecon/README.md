# README.md
# 🛰 Sentient Recon Agent (SRA) - AI Cyber Intelligence Dashboard

## Mission Description:

Build a full-stack AI-driven web app called **Sentient Recon Agent (SRA)**. It is designed to serve as a virtual intelligence analyst that can:

- Accept recon prompts from the user
- Analyze those prompts using GPT-4 or Claude
- Log every interaction (prompt + response + timestamp)
- Show a recon **heatmap** of activity per hour
- Show a **Sankey graph** of recon prompt relationships (e.g., prompt → hour used)
- Be modular enough to add scan tools later (e.g., Nmap, WhatWeb)

## Features to Implement:

✅ React-based modern UI  
✅ FastAPI backend that receives prompts and sends them to OpenAI's API  
✅ SQLite database that logs: prompt, response, timestamp  
✅ Heatmap: using `react-grid-heatmap`  
✅ Sankey Diagram: using `@nivo/sankey`  
✅ Admin-friendly layout with Tailwind  
✅ All logic modularized into `frontend` and `backend` folders  
✅ Deployment-ready with `.env` support

## File Structure:

sra/
├── backend/
│ ├── sra_core.py
│ └── requirements.txt
├── frontend/
│ ├── package.json
│ └── src/
│ └── ReconDashboard.js


## Tech Requirements:

Frontend:
- React + Vite
- Tailwind CSS
- `axios`
- `react-grid-heatmap`
- `@nivo/sankey`

Backend:
- FastAPI
- `openai` Python SDK
- SQLite
- `uvicorn`

### Additional Mission Guidelines

- All prompts and logs are stored in `/logs/`
- Enable operator-controlled input/override
- Default LLM model = `gpt-4o` with fallback to `gpt-3.5-turbo`
- Provide robust error handling and graceful fallbacks
