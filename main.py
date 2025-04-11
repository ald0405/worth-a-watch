# backend/main.py
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from config import YouTubeSummary, client

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set to localhost:3000 in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
def analyze_youtube_url(url: str = Form(...)):
    analyzer = YouTubeSummary(client, url)
    analyzer._fetch_metadata()
    metadata = analyzer.contextual_metadata
    summary = analyzer.generate_summary()

    return {
        "metadata": metadata,
        "summary": {
            "video_summary": summary.video_summary,
            "people": [{"name": p.name, "background": p.background} for p in summary.people]
        }
    }
