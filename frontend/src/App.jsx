import { useEffect, useMemo, useRef, useState } from "react";
import { askQuestion, escalateQuery, getLogs } from "./api";

function formatTimestamp(ts) {
  return new Date(ts).toLocaleString();
}

export default function App() {
  const [query, setQuery] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const chatWindowRef = useRef(null);
  const chatBottomRef = useRef(null);

  const lastUserQuery = useMemo(() => {
    const userMessages = chatHistory.filter((item) => item.role === "user");
    if (!userMessages.length) return "";
    return userMessages[userMessages.length - 1].text;
  }, [chatHistory]);

  const botMessageCount = useMemo(
    () => chatHistory.filter((item) => item.role === "bot").length,
    [chatHistory]
  );
  const escalatedCount = useMemo(
    () => chatHistory.filter((item) => item.role === "bot" && item.escalated).length,
    [chatHistory]
  );

  useEffect(() => {
    requestAnimationFrame(() => {
      chatBottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    });
  }, [chatHistory, loading, query]);

  async function handleSend(e) {
    e.preventDefault();

    const trimmed = query.trim();
    if (!trimmed) return;

    setLoading(true);
    setError("");
    setInfo("");

    const userMessage = { role: "user", text: trimmed, ts: Date.now() };
    setChatHistory((prev) => [...prev, userMessage]);
    setQuery("");

    try {
      const result = await askQuestion(trimmed);
      const botMessage = {
        role: "bot",
        text: result.response,
        domain: result.domain,
        intent: result.intent,
        confidence: result.confidence,
        responseTimeMs: result.response_time_ms,
        escalated: result.escalated,
        ts: Date.now(),
      };
      setChatHistory((prev) => [...prev, botMessage]);
      if (result.escalated) {
        setInfo("This query was escalated to human support due to confidence/safety rules.");
      }
    } catch (err) {
      const errorMessage = err.message || "Unexpected error while sending query.";
      setError(errorMessage);
      setChatHistory((prev) => [
        ...prev,
        {
          role: "bot",
          text: `I could not process your request right now: ${errorMessage}`,
          intent: "system_error",
          confidence: 0,
          escalated: true,
          ts: Date.now(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleEscalate() {
    if (!lastUserQuery) {
      setError("Send a query before requesting manual escalation.");
      return;
    }

    setError("");
    setInfo("");
    try {
      const result = await escalateQuery(
        lastUserQuery,
        "User requested manual escalation from frontend."
      );

      setChatHistory((prev) => [
        ...prev,
        {
          role: "bot",
          text: "Your issue has been manually escalated to a human support agent.",
          intent: "manual_escalation",
          confidence: 0,
          escalated: true,
          ts: Date.now(),
        },
      ]);

      if (result.status === "success") {
        setInfo(result.message);
      } else {
        setError("Escalation request was not confirmed by backend.");
      }
    } catch (err) {
      setError(err.message || "Failed to escalate query.");
    }
  }

  async function handleFetchLogs() {
    setLoadingLogs(true);
    setError("");

    try {
      const data = await getLogs();
      setLogs(data);
    } catch (err) {
      setError(err.message || "Failed to load logs.");
    } finally {
      setLoadingLogs(false);
    }
  }

  return (
    <div className="page">
      <div className="bg-shape shape-one" />
      <div className="bg-shape shape-two" />
      <div className="bg-grid" />
      <div className="container">
        <header className="header">
          <h1>AI-Powered Customer Support Chatbot</h1>
          <p>
            Ask about orders, refunds, delivery, returns, payment issues, and more.
          </p>
          <div className="header-stats">
            <div className="stat-chip">
              <span className="dot live" />
              Real-time AI replies
            </div>
            <div className="stat-chip">Confidence scoring</div>
            <div className="stat-chip">Escalation ready</div>
            <div className="stat-chip stat-chip-ghost">Bot replies: {botMessageCount}</div>
            <div className="stat-chip stat-chip-ghost">Escalations: {escalatedCount}</div>
          </div>
        </header>

        <main className="layout">
          <section className="chat-card">
            <div className="card-head">
              <h2>Chat</h2>
              <div className="assistant-pill">
                <span className="dot assistant" />
                Support AI
              </div>
            </div>
            <div className="chat-window" ref={chatWindowRef}>
              {chatHistory.length === 0 && (
                <div className="empty-state">
                  <h3>Start a conversation</h3>
                  <p className="placeholder">
                    Ask anything about orders, refunds, returns, delivery, payment, or
                    invoices.
                  </p>
                </div>
              )}

              {chatHistory.map((item, idx) => (
                <div
                  key={`${item.ts}-${idx}`}
                  className={`message ${item.role === "user" ? "user" : "bot"}`}
                  style={{ animationDelay: `${Math.min(idx * 70, 420)}ms` }}
                >
                  <div className="message-head">
                    <span>{item.role === "user" ? "You" : "Bot"}</span>
                    {item.role === "bot" && (
                      <>
                        <span className="intent">Domain: {item.domain || "general"}</span>
                        <span className="intent">Intent: {item.intent}</span>
                        <span className="confidence">
                          Confidence: {Number(item.confidence).toFixed(2)}
                        </span>
                        {item.responseTimeMs !== undefined && (
                          <span className="intent">Latency: {Number(item.responseTimeMs).toFixed(0)}ms</span>
                        )}
                        {item.escalated && <span className="badge">Escalated</span>}
                      </>
                    )}
                  </div>
                  <p>{item.text}</p>
                </div>
              ))}

              {query.trim() && !loading && (
                <div className="message user" aria-live="polite">
                  <div className="message-head">
                    <span>You</span>
                    <span className="intent">Typing...</span>
                  </div>
                  <p>{query}</p>
                </div>
              )}

              {loading && (
                <div className="message bot typing" aria-live="polite">
                  <div className="message-head">
                    <span>Bot</span>
                    <span className="intent">Typing...</span>
                  </div>
                  <div className="typing-dots">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              )}
              <div ref={chatBottomRef} />
            </div>

            <form className="chat-form" onSubmit={handleSend}>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Type your support question..."
                disabled={loading}
              />
              <button type="submit" disabled={loading} className={loading ? "is-loading" : ""}>
                {loading ? "Sending..." : "Send"}
              </button>
            </form>

            <button className="secondary" type="button" onClick={handleEscalate}>
              Manual Escalation
            </button>

            {error && <p className="error">{error}</p>}
            {info && <p className="info">{info}</p>}
          </section>

          <section className="logs-card">
            <div className="logs-head">
              <h2>Interaction Logs</h2>
              <button
                onClick={handleFetchLogs}
                disabled={loadingLogs}
                className={loadingLogs ? "is-loading" : ""}
              >
                {loadingLogs ? "Loading..." : "View Log"}
              </button>
            </div>

            <div className="logs-window">
              {!logs.length && (
                <div className="empty-state">
                  <h3>Logs are ready</h3>
                  <p className="placeholder">
                    Click <strong>View Logs</strong> to load full interaction history.
                  </p>
                </div>
              )}
              {logs.map((log) => (
                <div
                  className="log-row"
                  key={log.id}
                  style={{ animationDelay: `${Math.min(log.id * 35, 420)}ms` }}
                >
                  <div className="log-top">
                    <strong>#{log.id}</strong>
                    <span>{formatTimestamp(log.timestamp)}</span>
                  </div>
                  <p>
                    <strong>Query:</strong> {log.user_query}
                  </p>
                  <p>
                    <strong>Domain:</strong> {log.detected_domain || "general"}
                  </p>
                  <p>
                    <strong>Intent:</strong> {log.detected_intent}
                  </p>
                  <p className="log-response">
                    <strong>Response:</strong> {log.bot_response}
                  </p>
                  <p>
                    <strong>Confidence:</strong> {Number(log.confidence).toFixed(2)}
                  </p>
                  <p>
                    <strong>Escalated:</strong> {log.escalated ? "Yes" : "No"}
                  </p>
                  <p>
                    <strong>Latency:</strong> {Number(log.response_time_ms || 0).toFixed(0)} ms
                  </p>
                </div>
              ))}
            </div>
            <p className="logs-note">
              Logs include query, response, confidence, and escalation status for review.
            </p>
          </section>
        </main>
      </div>
    </div>
  );
}
