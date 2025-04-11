import { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

export default function Home() {
  const [url, setUrl] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [duration, setDuration] = useState(0);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('history');
      if (stored) {
        setHistory(JSON.parse(stored));
      }
    }
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('history', JSON.stringify(history));
    }
  }, [history]);

  useEffect(() => {
    let interval;
    if (loading) {
      interval = setInterval(() => {
        setDuration((d) => d + 1);
      }, 1000);
    } else {
      clearInterval(interval);
      setDuration(0);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleSubmit = async () => {
    if (!url.trim()) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("url", url);

    try {
      const res = await axios.post("http://127.0.0.1:8000/analyze", formData);
      setData(res.data);
      setHistory((prev) => [{ url, data: res.data }, ...prev.slice(0, 4)]);
    } catch (err) {
      console.error("Error calling backend:", err);
      alert("Something went wrong. Check the backend and console.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      fontFamily: "'Segoe UI', sans-serif",
      background: "linear-gradient(180deg, #0f2027, #203a43, #2c5364)",
      minHeight: "100vh",
      color: "#e0f7fa",
      padding: "3rem 1rem"
    }}>
      <div style={{ maxWidth: "960px", margin: "0 auto" }}>
        <h1 style={{
          fontSize: "2.75rem",
          fontWeight: "bold",
          textAlign: "center",
          marginBottom: "2rem",
          color: "#00e676"
        }}>
          🎬 Worth the Watch? <span style={{ fontWeight: 300, color: "#e0f7fa" }}>Let AI help you decide</span>
        </h1>

        <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem" }}>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste YouTube URL here"
            autoFocus
            style={{
              flexGrow: 1,
              padding: "0.75rem 1rem",
              fontSize: "1rem",
              border: "1px solid #333",
              borderRadius: "8px",
              backgroundColor: "#1c2b36",
              color: "#fff"
            }}
          />
          <button
            onClick={handleSubmit}
            disabled={!url.trim() || loading}
            style={{
              padding: "0.75rem 1.5rem",
              fontSize: "1rem",
              background: !url.trim() || loading ? "#444" : "#00e676",
              color: "#000",
              borderRadius: "8px",
              border: "none",
              cursor: !url.trim() || loading ? "not-allowed" : "pointer",
              fontWeight: "bold"
            }}
          >
            Analyze
          </button>
        </div>

        {history.length > 0 && (
          <div style={{ marginBottom: "2rem" }}>
            <h2 style={{ fontSize: "1.25rem", color: "#4dd0e1", marginBottom: "1rem" }}>🔁 Recent Searches</h2>
            <ul>
              {history.map((entry, i) => (
                <li key={i} style={{ marginBottom: "0.5rem" }}>
                  <button onClick={() => { setUrl(entry.url); setData(entry.data); }} style={{ color: "#80cbc4", background: "none", border: "none", textDecoration: "underline", cursor: "pointer" }}>
                    {entry.url}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {loading && (
          <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
            <p style={{ fontSize: "1.1rem" }}>⏳ Generating AI-powered summary...</p>
            <p style={{ fontSize: "0.9rem", color: "#80cbc4" }}>Elapsed time: {duration}s</p>
          </div>
        )}

        {data && (
          <div style={{
            backgroundColor: "#1a2e35",
            padding: "2rem",
            borderRadius: "14px",
            boxShadow: "0 12px 30px rgba(0,0,0,0.5)",
            transition: "all 0.3s ease-in-out"
          }}>
            <div style={{ display: "flex", gap: "2rem", marginBottom: "2rem", flexWrap: "wrap" }}>
              <img src={data.metadata.thumbnail} alt="Thumbnail" style={{
                width: "280px",
                height: "auto",
                objectFit: "cover",
                borderRadius: "12px",
                flexShrink: 0
              }} />
              <div style={{ flex: "1 1 300px" }}>
                <h2 style={{ fontSize: "1.5rem", color: "#80cbc4", marginBottom: "0.75rem" }}>{data.metadata.title}</h2>
                <p><strong>📅 Upload Date:</strong> {data.metadata.upload_date}</p>
                <p><strong>👤 Uploader:</strong> <a href={data.metadata.channel_url} target="_blank" rel="noopener noreferrer" style={{ color: "#4dd0e1" }}>{data.metadata.uploader}</a></p>
                <p><strong>👀 Views:</strong> {data.metadata.view_count.toLocaleString()}</p>
                <p><strong>👍 Likes:</strong> {data.metadata.like_count.toLocaleString()}</p>
                <p><strong>📢 Categories:</strong> {data.metadata.categories.join(', ')}</p>
              </div>
            </div>

            <details style={{ marginBottom: "1.5rem" }}>
              <summary style={{ cursor: "pointer", color: "#00e676", fontSize: "1.2rem" }}>👥 People in the Video</summary>
              <ul style={{ paddingLeft: "1rem", marginTop: "1rem" }}>
                {data.summary.people.map((person) => (
                  <li key={person.name} style={{ marginBottom: "0.5rem" }}>
                    <strong>{person.name}</strong>{person.background ? ` – ${person.background}` : ""}
                  </li>
                ))}
              </ul>
            </details>

            <details>
              <summary style={{ cursor: "pointer", color: "#00e676", fontSize: "1.2rem" }}>📜 Summary</summary>
              <p style={{ fontStyle: "italic", color: "#ccc", marginBottom: "1rem" }}>
                AI-Generated – Please interpret with caution
              </p>
              <div style={{ fontSize: "1.05rem", lineHeight: "1.6", color: "#e0f2f1" }}>
                <ReactMarkdown>{data.summary.video_summary}</ReactMarkdown>
              </div>
            </details>
          </div>
        )}
      </div>
    </div>
  );
}
