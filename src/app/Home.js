import React, { useState, useEffect, useRef } from "react";
import "../styles/Home.css";

// Ionicons CDN for icons
const IonIcon = ({ name, ...props }) => (
  <span {...props}>
    <ion-icon name={name}></ion-icon>
  </span>
);

function Home() {
  const [theme, setTheme] = useState("light");
  const [input, setInput] = useState("");
  const inputRef = useRef(null);
  const baseHeightRef = useRef(48); // fallback to 48px
  const [showHint, setShowHint] = useState(false);
  const hintTimeoutRef = useRef(null);

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

  const handleSend = () => {
    if (!input.trim()) {
      // Show hint for empty input
      setShowHint(true);
      if (hintTimeoutRef.current) clearTimeout(hintTimeoutRef.current);
      hintTimeoutRef.current = setTimeout(() => setShowHint(false), 2000);
      return;
    }
    // Placeholder for send logic
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

  return (
    <div className="home-container no-scroll">
      <div className="thespis-name">Thespis</div>
      <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle dark/light mode">
        <IonIcon name={theme === "light" ? "moon" : "sunny"} />
      </button>
      <div className="chat-input-wrapper">
        <textarea
          ref={inputRef}
          className="chat-input"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder="Type your message..."
          style={{ fontSize: "1.05rem" }}
        />
        <button className="send-btn" onClick={handleSend} aria-label="Send">
          <IonIcon name="send" style={{ fontSize: "1.25rem" }} />
        </button>
        {showHint && (
          <div className="hint-popup">
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
      </div>
    </div>
  );
}

export default Home;
