# 🛡️ StreamGuard AI — Personalized Creative Assistant for Live Streamers

> **AI Builders Challenge with IBM Bob — July 2026**  
> **Challenge Theme: Reimagine Creative Industries with AI**

StreamGuard AI is an intelligent co-pilot for live content creators that uses a multi-agent AI pipeline to automatically analyze, moderate, prioritize, and generate responses for live stream super chats — letting creators focus on what they do best: **creating**.

---

## 📋 Problem Statement

During high-energy live streams on YouTube and Twitch, fans pay money to send **Super Chats** expecting their favorite creator to read their message live. However, live stream chats move at lightning speed:

1. **The Buried Super Chat Trap:** Super chats pop up for just a few seconds before getting buried by thousands of incoming messages. If a streamer is gaming or talking, they completely miss it.
2. **Fan Frustration & Spam:** Unacknowledged fans feel ignored after spending hard-earned money and spam follow-up messages like *"Hey, I sent $20 five minutes ago! Did you see my super chat?"*
3. **The Manual Scrolling Disruption:** Streamers are forced to stop performing, break character, and manually scroll up and down through endless chat logs trying to hunt down missed super chats — destroying live stream momentum.

## 💡 Solution Description

StreamGuard AI is a **hands-free AI co-pilot** that eliminates chat scrolling forever and ensures no fan is ever missed:

- **📌 Intelligent Priority Queue:** Super chats never disappear into a fast-moving chat. They are AI-scored by sentiment, question urgency, and donation tier, keeping key messages pinned at the top.
- **🎤 Hands-Free Voice Matching (The WOW Factor):** StreamGuard AI listens to the streamer's microphone in real time. The second the creator reads a fan's message out loud, StreamGuard's fuzzy voice-matching engine recognizes the spoken words, marks the chat as read, and automatically advances the queue — **zero mouse clicks, zero manual scrolling.**
- **🛡️ 4-Agent AI Pipeline:** Simultaneously filters toxic content, analyzes sentiment, scores priority, and suggests natural 1-sentence replies so the streamer can respond instantly.

## 🏗️ AI Approach & Architecture

### Multi-Agent AI Pipeline

```
SuperChat → [Moderation Agent] → [Sentiment Agent] → [Revenue Agent] → [Response Agent] → Priority Queue
```

StreamGuard uses **4 specialized AI agents** coordinated by a central orchestrator:

| Agent | Role | Method |
|-------|------|--------|
| **Moderation Agent** | Detects toxic, NSFW, spam content | AI + regex rules |
| **Sentiment Agent** | Classifies sentiment & intent | AI analysis |
| **Revenue Agent** | Calculates priority score by tier | Rule-based + sentiment bonus |
| **Response Agent** | Generates suggested replies | AI with tone matching |

All four agents are powered by a **single optimized AI call** for speed and cost efficiency, with the orchestrator distributing results to each specialized agent.

### System Architecture

```
┌─────────────────────────────────────────────────┐
│                  Next.js Frontend                │
│     Dashboard · Chat Queue · Stats · Controls    │
└──────────────────────┬──────────────────────────┘
                       │ WebSocket + REST
┌──────────────────────▼──────────────────────────┐
│               FastAPI Backend                    │
│  ┌──────────────────────────────────────────┐   │
│  │          Agent Orchestrator               │   │
│  │  Moderation → Sentiment → Revenue →      │   │
│  │  Response → Priority Queue               │   │
│  └──────────────────────────────────────────┘   │
│  ┌─────────────┐  ┌─────────────────────────┐   │
│  │Voice Matcher │  │   Queue Manager (Heap)  │   │
│  └─────────────┘  └─────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │         Supabase (PostgreSQL)             │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python, WebSocket |
| AI Engine | Multi-Agent Pipeline powered by **IBM Granite 3.1 (watsonx.ai)** |
| Database | Supabase (PostgreSQL) |
| Voice | Fuzzy matching with difflib + keyword overlap |
| Real-time | WebSocket for instant updates |

## 🎯 Selected Challenge Theme

**Reimagine Creative Industries with AI**

StreamGuard AI reimagines how content creators interact with their audience during live streams. Instead of being overwhelmed by the volume of fan interactions, creators get an AI-powered assistant that:

- **Enhances creativity** — by removing the cognitive load of chat management
- **Helps creators engage faster** — with AI-suggested responses and priority-sorted queues
- **Unlocks new interactive experiences** — through voice-matched auto-advancement and real-time sentiment insights

## 🔧 How IBM Bob Was Used

IBM Bob was used as our primary AI-powered development partner throughout the software lifecycle. See the complete report in **[IBM_BOB_WORKFLOW.md](IBM_BOB_WORKFLOW.md)**.

- **Architecture Planning** — Designed the batch Orchestrator pattern for sub-second agent processing
- **Code Optimization** — Refactored the Voice Matching engine with hybrid sequence matching and rolling buffers
- **Troubleshooting** — Completed the *"Lab: Troubleshoot Your Code Using IBM Bob"* on IBM SkillsBuild and applied Bob's debugging workflows to fix async concurrency issues in WebSocket handlers
- **Schema Validation** — Assisted in writing structured Pydantic models and TypeScript interfaces

> *IBM SkillsBuild Activity Completed: "Lab: Troubleshoot Your Code Using IBM Bob" (Completed 30 Jul 2026)*

## 🚀 How to Run

### Prerequisites
- Python 3.10+
- Node.js 18+
- Supabase account (free tier works)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your Supabase + AI API keys

# Run the Supabase schema
# Copy supabase_schema.sql contents into Supabase SQL Editor and run

# Start server
python run.py
```

Backend runs at: `http://localhost:8000`  
API docs at: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: `http://localhost:3000`

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/stream/start` | Start a stream session |
| POST | `/api/stream/stop` | End the session |
| GET | `/api/stream/status` | Get session status |
| POST | `/api/superchat/send` | Send a super chat |
| GET | `/api/superchat/queue` | View the priority queue |
| GET | `/api/superchat/next` | Advance to next chat |
| WS | `/ws` | WebSocket for real-time updates |

## 🎬 Demo Video

> 📹 [Watch the 3-minute demo video](#) *( https://drive.google.com/file/d/1UjVJ2XBczN4CNx-qHKPtgATN5gmDMfDo/view?usp=sharing )*

## 👥 Team

- **Prajwal Rudrapwar** — Full-stack Developer & AI Engineer

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built for the AI Builders Challenge with IBM Bob · July 2026*
