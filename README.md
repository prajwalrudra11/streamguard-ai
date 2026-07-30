# 🛡️ StreamGuard AI — Personalized Creative Assistant for Live Streamers

> **AI Builders Challenge with IBM Bob — July 2026**  
> **Challenge Theme: Reimagine Creative Industries with AI**

StreamGuard AI is an intelligent co-pilot for live content creators that uses a multi-agent AI pipeline to automatically analyze, moderate, prioritize, and generate responses for live stream super chats — letting creators focus on what they do best: **creating**.

---

## 📋 Problem Statement

Live streaming is one of the fastest-growing creative industries, with millions of creators broadcasting daily on platforms like YouTube, Twitch, and more. During live streams, fans send **super chats** (paid messages) to interact with their favorite creators.

**The problem:** Popular streamers receive dozens or even hundreds of super chats per stream. Manually reading, filtering toxic messages, identifying important questions, and crafting responses forces creators to **split their attention** between performing and managing — degrading both the creative experience and fan engagement.

Creators need an AI-powered assistant that handles the operational complexity so they can stay focused on creating compelling content.

## 💡 Solution Description

StreamGuard AI acts as a **personalized creative assistant** that sits between the super chat stream and the creator, providing:

- **🔍 Intelligent Moderation** — Automatically detects and flags toxic, NSFW, or spam messages so creators never have to deal with harmful content
- **💬 Sentiment Analysis** — Understands the emotional tone and intent (question, compliment, request, story) of each message
- **💰 Revenue-Aware Prioritization** — Scores and ranks super chats using a smart priority queue that considers donation amount, sentiment, and intent
- **🤖 AI-Suggested Responses** — Generates natural, tone-appropriate reply suggestions the creator can use or adapt
- **🎤 Voice Matching** — Fuzzy-matches the streamer's spoken words against the displayed super chat text to auto-advance the queue hands-free

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
| AI Engine | Multi-Agent Pipeline (Orchestrator pattern) |
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
