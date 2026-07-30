/* ── StreamGuard AI - Voice Recognition Hook ─────── */
"use client";

import { useCallback, useEffect, useRef, useState } from "react";

interface VoiceRecognitionOptions {
  onTranscript: (text: string) => void;
  continuous?: boolean;
  lang?: string;
}

export function useVoiceRecognition({
  onTranscript,
  continuous = true,
  lang = "en-US",
}: VoiceRecognitionOptions) {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const onTranscriptRef = useRef(onTranscript);
  const isListeningRef = useRef(isListening);
  const hasErrorRef = useRef(false);

  // Keep callback ref current
  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  }, [onTranscript]);

  // Keep isListeningRef current so callbacks can read it without triggering re-effects
  useEffect(() => {
    isListeningRef.current = isListening;
  }, [isListening]);

  // Initialize SpeechRecognition once (or when settings change)
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    setIsSupported(!!SpeechRecognition);

    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = continuous;
    recognition.interimResults = false;
    recognition.lang = lang;

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const last = event.results[event.results.length - 1];
      if (last.isFinal) {
        const transcript = last[0].transcript.trim();
        if (transcript) {
          onTranscriptRef.current(transcript);
        }
      }
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      if (event.error !== "no-speech") {
        console.error("Speech recognition error:", event.error);
        
        // Critical errors should stop the listening state to prevent loops
        if (["not-allowed", "audio-capture", "network", "service-not-allowed", "language-not-supported"].includes(event.error)) {
          hasErrorRef.current = true;
          setIsListening(false);
        }
      }
    };

    recognition.onend = () => {
      // Auto-restart if we are still supposed to be listening and no critical error occurred
      if (isListeningRef.current && !hasErrorRef.current) {
        try {
          recognition.start();
        } catch (e) {
          console.warn("Failed to auto-restart speech recognition:", e);
        }
      }
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.stop();
    };
  }, [continuous, lang]);

  // Start / stop based on isListening state changes
  useEffect(() => {
    if (!recognitionRef.current) return;

    if (isListening) {
      hasErrorRef.current = false;
      try {
        recognitionRef.current.start();
      } catch (e) {
        /* already started */
      }
    } else {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        /* already stopped */
      }
    }
  }, [isListening]);

  const startListening = useCallback(() => {
    setIsListening(true);
  }, []);

  const stopListening = useCallback(() => {
    setIsListening(false);
  }, []);

  return { isListening, isSupported, startListening, stopListening };
}

