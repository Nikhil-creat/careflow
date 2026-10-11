# CareFlow: AI Hospital Management Automation

Demo project. Uses fictional data only. Never enter real patient data; it is not HIPAA/DPDP compliant.

## Features
- Triage, bed, pharmacy and billing automations
- Agents tab: bed, pharmacy, billing and risk agents (plan, act, observe) plus patient risk scores
- AI care navigator chatbot: emergency detection, symptom to department routing, booking
- FastAPI backend with a Claude tool-use agent loop (works without a key using rules)
- Docker, docker-compose, GitHub Actions, Render blueprint

## Structure
docs/ (website) · backend/ (API) · docker-compose.yml · render.yaml · .github/workflows/deploy.yml

## Run locally
cp .env.example .env   (add ANTHROPIC_API_KEY, optional)
docker compose up --build
Website: http://localhost:8080 · API docs: http://localhost:8000/docs
In the AI Assistant tab, tap "connect backend" and enter http://localhost:8000

## Deploy free
1. Website (GitHub Pages): push to a new GitHub repo on branch main. Repo Settings > Pages > Source: GitHub Actions. Site goes live at https://USERNAME.github.io/REPO/
2. Backend (Render free tier): render.com > New > Blueprint > pick the repo. Add ANTHROPIC_API_KEY if you want the LLM (paid API; skip for rule-based mode). First request after idle takes about 50 seconds.
3. Connect: open the live site > AI Assistant > connect backend > paste the Render URL.
4. Lock down: set CORS_ORIGINS to your Pages URL.

## Next steps
Postgres + auth, FHIR integration, vector-search RAG over hospital FAQs, Prometheus/Grafana.

## New in v2
Analytics (occupancy, revenue trend and forecast, department and insurance mix), Marketing (campaigns with ROI, lead sources, patient segments, message drafts), Lab queue, Staff roster, and patient phone and insurance fields.

## Publish on GitHub Pages (step by step)
1. Unzip `careflow-master.zip`. Open the `careflow` folder.
2. On github.com click New repository, name it `careflow`, keep it Public, create it empty.
3. In a terminal inside the folder:
   git init
   git add .
   git commit -m "CareFlow v2"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/careflow.git
   git push -u origin main
4. In the repo go to Settings > Pages > Source and choose GitHub Actions.
5. Open the Actions tab and wait for "Deploy to GitHub Pages" to turn green (1 to 2 minutes).
6. Your site: https://YOUR-USERNAME.github.io/careflow/
No terminal? Upload the files with Add file > Upload files (include the .github folder), then do steps 4 to 6.

## v3: Groq AI, booking confirmations, responsive layout
- Free Groq AI: create a free key at https://console.groq.com/keys, open the app, go to Settings, paste it and Save. The agent then plans, calls tools (triage, beds, book appointment) and answers using Llama on Groq. Emergency messages are always handled by built-in safety rules first.
- Key safety: a key in a static site is visible to visitors. Keep it in Settings (stays in your browser). Only put it in docs/config.js for private demos, and revoke it afterwards. For a public site, host the backend and set GROQ_API_KEY there (Render dashboard).
- Booking automation: every booking (form or chatbot) shows a confirmation with reference, patient, hospital name and address, department, doctor, date, time and helpline. Buttons: Add to calendar (.ics with 1-hour alert), WhatsApp, SMS, Copy, Print. A reminder agent queues reminders for open appointments.
- Settings tab: set your hospital name, address and helpline once.
- Layout: phones get a scrolling tab bar and single column; desktops get a sidebar and wider grid.

## v4: full website + automation
Landing site (header, hero with live status, departments, how it works, automation, doctors, feedback, FAQ, contact, footer) and the Staff portal in one app. Installable (PWA), works offline after first visit, dark mode, keyboard and screen-reader friendly. Agents tab: auto mode (every 20 s), missed-visit rebooking, one-time reminders, daily summary, CSV export.

## Deploy from your phone with Termux
1. Install Termux from F-Droid (the Play Store build is outdated).
2. Run:
   pkg update -y && pkg upgrade -y
   pkg install -y git unzip
   termux-setup-storage        (tap Allow)
3. Unzip into Termux home (not shared storage):
   unzip ~/storage/downloads/careflow-master.zip -d ~
   cd ~/careflow && ls -a      (you should see .github)
4. Git identity and first commit:
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   git init && git add . && git commit -m "CareFlow v4"
   git branch -M main
5. On github.com create an empty repo `careflow`. Create a token: Settings > Developer settings > Personal access tokens > Tokens (classic) > scopes `repo` and `workflow`.
6. git remote add origin https://github.com/YOUR-USERNAME/careflow.git
   git push -u origin main     (username = GitHub username, password = the token)
   Optional: git config --global credential.helper store
7. Repo > Settings > Pages > Source: GitHub Actions. Watch the Actions tab, then open https://YOUR-USERNAME.github.io/careflow/
Update later: edit, then git add . && git commit -m "update" && git push

## v5: branding and selling
logo.svg, logo-dark.svg (and PNGs when available), app icon, privacy notice template, 404 page, demo-request button (set salesPhone or salesEmail in docs/config.js), Telugu/Hindi/English replies from the Groq agent. See sales/SALES-GUIDE.md.
