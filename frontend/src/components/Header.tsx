/* ── StreamGuard AI - Header Component ────────────── */
"use client";

interface HeaderProps {
  isActive: boolean;
  isConnected: boolean;
  onStartStream: () => void;
  onStopStream: () => void;
  onToggleVoice: () => void;
  isListening: boolean;
  voiceSupported: boolean;
  onGoHome?: () => void;
}

export default function Header({
  isActive,
  isConnected,
  onStartStream,
  onStopStream,
  onToggleVoice,
  isListening,
  voiceSupported,
  onGoHome,
}: HeaderProps) {
  return (
    <header className="glass-strong border-b border-[hsl(220,12%,22%)] px-6 py-3 flex items-center justify-between sticky top-0 z-50">
      {/* Logo */}
      <div 
        onClick={onGoHome} 
        className={`flex items-center gap-3 ${onGoHome ? "cursor-pointer hover:opacity-80 transition-opacity" : ""}`}
      >
        <div className="w-9 h-9 rounded-lg gradient-primary flex items-center justify-center text-lg shadow-md shadow-[hsl(250,80%,60%,0.2)]">
          🛡️
        </div>
        <div>
          <h1 className="text-lg font-bold gradient-text leading-tight">
            StreamGuard AI
          </h1>
          <p className="text-[10px] text-[hsl(220,10%,40%)] uppercase tracking-widest">
            Super Chat Co-Pilot
          </p>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-3">
        {/* Trust Report Link */}
        <a
          href="/trust-report"
          className="px-3.5 py-2 rounded-lg text-xs font-semibold bg-[hsl(168,85%,48%,0.15)] text-[hsl(168,85%,52%)] border border-[hsl(168,85%,48%,0.3)] hover:bg-[hsl(168,85%,48%,0.25)] transition-all flex items-center gap-1.5"
        >
          <span>📊</span> Trust Report
        </a>

        {/* Voice Toggle */}
        {voiceSupported && isActive && (
          <button
            onClick={onToggleVoice}
            className={`
              px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer
              ${
                isListening
                  ? "bg-[hsl(280,80%,60%,0.2)] text-[hsl(280,80%,60%)] ring-1 ring-[hsl(280,80%,60%,0.4)]"
                  : "bg-[hsl(220,16%,14%)] text-[hsl(220,10%,60%)] hover:bg-[hsl(220,16%,18%)]"
              }
            `}
          >
            {isListening ? "🎤 Listening..." : "🎤 Voice Off"}
          </button>
        )}

        {/* Stream Control */}
        {isActive ? (
          <button
            onClick={onStopStream}
            className="px-5 py-2 rounded-lg text-sm font-semibold bg-[hsl(0,75%,55%,0.2)] text-[hsl(0,75%,55%)] hover:bg-[hsl(0,75%,55%,0.3)] ring-1 ring-[hsl(0,75%,55%,0.3)] transition-all cursor-pointer"
          >
            ⏹️ End Stream
          </button>
        ) : (
          <button
            onClick={onStartStream}
            className="px-5 py-2 rounded-lg text-sm font-semibold gradient-primary text-white hover:opacity-90 transition-all shadow-lg cursor-pointer"
          >
            🚀 Start Stream
          </button>
        )}

        {/* Connection Indicator */}
        <div
          className={`w-3 h-3 rounded-full ${
            isConnected
              ? "bg-[hsl(152,70%,50%)] shadow-[0_0_10px_hsl(152,70%,50%,0.5)]"
              : "bg-[hsl(0,75%,55%)]"
          }`}
          title={isConnected ? "Connected" : "Disconnected"}
        />
      </div>
    </header>
  );
}
