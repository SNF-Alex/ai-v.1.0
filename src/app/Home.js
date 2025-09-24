import React, { useState, useEffect, useRef, useMemo } from "react";
import "../styles/Home.css";

// Ionicons CDN for icons
const IonIcon = ({ name, ...props }) => (
  <span {...props}>
    <ion-icon name={name}></ion-icon>
  </span>
);

function Home() {
  // Sessions state: array of { messages: [] }
  const [sessions, setSessions] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("sessions") || "[]") || [{ messages: [] }];
    } catch {
      return [{ messages: [] }];
    }
  });
  const [activeSession, setActiveSession] = useState(0);
  const [theme, setTheme] = useState("light");
  const [input, setInput] = useState("");
  const inputRef = useRef(null);
  const baseHeightRef = useRef(48); // fallback to 48px
  const [showHint, setShowHint] = useState(false);
  const hintTimeoutRef = useRef(null);
  const [inputFocused, setInputFocused] = useState(false);

  // Fix ESLint: useMemo for messages
  const messages = useMemo(() => sessions[activeSession]?.messages || [], [sessions, activeSession]);

  useEffect(() => {
    document.body.setAttribute("data-theme", theme);
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, [theme]);

  useEffect(() => {
    // Load Ionicons CDN if not present
    if (!document.getElementById("ionicons-cdn")) {
      const script = document.createElement("script");
      script.id = "ionicons-cdn";
      script.src = "https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.esm.js";
      script.type = "module";
      document.body.appendChild(script);
      const nomoduleScript = document.createElement("script");
      nomoduleScript.src = "https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.js";
      document.body.appendChild(nomoduleScript);
    }
  }, []);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const MAX_HEIGHT = 192; // ~20% bigger than previous 160px

  // Save sessions to localStorage
  useEffect(() => {
    localStorage.setItem("sessions", JSON.stringify(sessions));
  }, [sessions]);

  // Add new session
  const handleNewSession = () => {
    setSessions(prev => [...prev, { messages: [] }]);
    setActiveSession(sessions.length);
    setInput("");
    if (inputRef.current) {
      inputRef.current.style.height = `${baseHeightRef.current || 48}px`;
      inputRef.current.focus();
    }
  };

  // Switch session
  const handleSwitchSession = idx => {
    setActiveSession(idx);
    setInput("");
    if (inputRef.current) {
      inputRef.current.style.height = `${baseHeightRef.current || 48}px`;
      inputRef.current.focus();
    }
  };

  // Delete session
  const handleDeleteSession = idx => {
    if (sessions.length === 1) return; // Don't delete last session
    setSessions(prev => {
      const updated = prev.filter((_, i) => i !== idx);
      // If deleting active, switch to previous or first
      let newActive = activeSession;
      if (idx === activeSession) {
        newActive = Math.max(0, activeSession - 1);
      } else if (idx < activeSession) {
        newActive = activeSession - 1;
      }
      setActiveSession(newActive);
      return updated;
    });
  };

  // Save all messages to localStorage
  useEffect(() => {
    localStorage.setItem("messages", JSON.stringify(messages));
  }, [messages]);

  // Save first message to localStorage when it changes
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem("firstMessage", messages[0]);
    }
  }, [messages]);

  // When user sends a message, show it above input and add to messages
  const handleSend = () => {
    if (!input.trim()) {
      // Show hint for empty input above input field
      setShowHint(true);
      if (hintTimeoutRef.current) clearTimeout(hintTimeoutRef.current);
      hintTimeoutRef.current = setTimeout(() => setShowHint(false), 2000);
      // Scroll hint into view above input
      if (inputRef.current) {
        inputRef.current.scrollIntoView({ block: "center", behavior: "smooth" });
      }
      return;
    }
    const msg = input.trim();
    setSessions(prev => {
      const updated = [...prev];
      updated[activeSession] = {
        ...updated[activeSession],
        messages: [...updated[activeSession].messages, msg]
      };
      return updated;
    });
    setInput("");
    if (inputRef.current) {
      const minH = baseHeightRef.current || 48;
      inputRef.current.style.height = `${minH}px`;
      inputRef.current.focus();
    }
  };

  // Measure base height on mount
  useEffect(() => {
    if (inputRef.current) {
      // Capture the natural single-line height as the baseline
      baseHeightRef.current = inputRef.current.clientHeight || 48;
      inputRef.current.style.height = `${baseHeightRef.current}px`;
    }
  }, []);

  // Auto-grow textarea, clamped to MAX_HEIGHT and never below base height
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      const minH = baseHeightRef.current || 48;
      const next = Math.max(minH, Math.min(inputRef.current.scrollHeight, MAX_HEIGHT));
      inputRef.current.style.height = `${next}px`;
    }
  }, [input]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!input.trim()) {
        // Show hint for empty input
        setShowHint(true);
        if (hintTimeoutRef.current) clearTimeout(hintTimeoutRef.current);
        hintTimeoutRef.current = setTimeout(() => setShowHint(false), 5000);
        return;
      }
      handleSend();
    }
  };

  // Hide hint as soon as the user starts typing something
  useEffect(() => {
    if (input.trim()) {
      setShowHint(false);
      if (hintTimeoutRef.current) {
        clearTimeout(hintTimeoutRef.current);
        hintTimeoutRef.current = null;
      }
    }
    return () => {
      if (hintTimeoutRef.current) {
        clearTimeout(hintTimeoutRef.current);
        hintTimeoutRef.current = null;
      }
    };
  }, [input]);

  // Determine if input should be at bottom
  const inputAtBottom = messages.length > 0;

  return (
    <div className="home-container no-scroll">
      {/* Sidebar overlay */}
      <div className="sidebar-overlay">
        <div className="sidebar-header-row">
          <span className="sidebar-ai-name">Thespis</span>
          <button
            className="add-session-btn"
            onClick={handleNewSession}
            aria-label="New chat/session"
            type="button"
          >
            <IonIcon name="add" style={{ fontSize: "1.7rem" }} />
          </button>
        </div>
        <div className="sidebar-session-list">
          {sessions.map((session, idx) => (
            <button
              key={idx}
              className={`sidebar-session-item${idx === activeSession ? " active" : ""}`}
              onClick={() => handleSwitchSession(idx)}
              title={session.messages[0] || "New chat"}
              type="button"
            >
              <span className="session-title">
                {session.messages[0]
                  ? session.messages[0].length > 32
                    ? session.messages[0].slice(0, 32) + "..."
                    : session.messages[0]
                  : "New chat"}
              </span>
              {sessions.length > 1 && (
                <span
                  className="delete-session-btn"
                  onClick={e => {
                    e.stopPropagation();
                    handleDeleteSession(idx);
                  }}
                  aria-label="Delete session"
                  tabIndex={-1}
                >
                  <IonIcon name="trash" style={{ fontSize: "1.15rem" }} />
                </span>
              )}
            </button>
          ))}
        </div>
      </div>
      <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle dark/light mode">
        <IonIcon name={theme === "light" ? "moon" : "sunny"} />
      </button>
      {/* Remove .above-input-message */}
      {/* Scrollable middle area for messages */}
      <div className="messages-scroll-area">
        {messages.map((msg, idx) => (
          <div key={idx} className="message-item">
            {msg}
          </div>
        ))}
      </div>
      <div
        className={`chat-input-wrapper${inputAtBottom ? " animate-pos" : ""}`}
        style={
          inputAtBottom
            ? {
                bottom: "20px",
                top: "auto",
                left: "50%",
                transform: "translateX(-50%)",
                position: "absolute",
                paddingBottom: "0"
              }
            : {}
        }
      >
        {/* Show hint above the textarea, not below */}
        {showHint && (
          <div className="hint-popup" style={{ bottom: "auto", top: "-44px" }}>
            <span>Try asking Thespis a question</span>
            <button
              type="button"
              className="hint-close"
              onClick={() => setShowHint(false)}
              aria-label="Close hint"
            >
              <IonIcon name="close" />
            </button>
          </div>
        )}
        <textarea
          ref={inputRef}
          className="chat-input"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder="Type your message..."
          style={{ fontSize: "1.05rem" }}
          onFocus={() => setInputFocused(true)}
          onBlur={() => setInputFocused(false)}
        />
        <button className="send-btn" onClick={handleSend} aria-label="Send">
          <IonIcon name="send" style={{ fontSize: "1.25rem" }} />
        </button>
      </div>
      <div className="footer">
        All rights reserved to Thespis
      </div>
    </div>
  );
}

export default Home;
