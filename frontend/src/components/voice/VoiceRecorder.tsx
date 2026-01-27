import { useState, useRef, useEffect } from 'react';
import { Button } from '../ui/Button';

interface VoiceRecorderProps {
  onRecordingComplete: (blob: Blob, duration: number) => void;
  maxDuration?: number; // in seconds
}

export function VoiceRecorder({ onRecordingComplete, maxDuration = 60 }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioURL, setAudioURL] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);
  const pausedTimeRef = useRef<number>(0);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (audioURL) {
        URL.revokeObjectURL(audioURL);
      }
    };
  }, [audioURL]);

  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(audioBlob);
        setAudioURL(url);

        // Calculate final duration
        const duration = (Date.now() - startTimeRef.current - pausedTimeRef.current) / 1000;
        onRecordingComplete(audioBlob, duration);

        // Stop all tracks
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setIsPaused(false);
      startTimeRef.current = Date.now();
      pausedTimeRef.current = 0;

      // Start timer
      timerRef.current = window.setInterval(() => {
        const elapsed = (Date.now() - startTimeRef.current - pausedTimeRef.current) / 1000;
        setRecordingTime(elapsed);

        // Auto-stop at max duration
        if (elapsed >= maxDuration) {
          stopRecording();
        }
      }, 100);
    } catch (err) {
      console.error('Error accessing microphone:', err);
      setError('Could not access microphone. Please grant permission and try again.');
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      pausedTimeRef.current += Date.now() - startTimeRef.current;
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      startTimeRef.current = Date.now();

      timerRef.current = window.setInterval(() => {
        const elapsed = (Date.now() - startTimeRef.current - pausedTimeRef.current + pausedTimeRef.current) / 1000;
        setRecordingTime(elapsed);

        if (elapsed >= maxDuration) {
          stopRecording();
        }
      }, 100);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };

  const resetRecording = () => {
    if (audioURL) {
      URL.revokeObjectURL(audioURL);
    }
    setAudioURL(null);
    setRecordingTime(0);
    setError(null);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-4">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Recording Indicator */}
      {isRecording && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2">
            {!isPaused && (
              <span className="flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
              </span>
            )}
            {isPaused && <span className="inline-flex rounded-full h-3 w-3 bg-gray-400"></span>}
          </div>
          <div className="flex-1">
            <p className="font-medium text-gray-900">
              {isPaused ? 'Recording Paused' : 'Recording...'}
            </p>
            <p className="text-sm text-gray-600">
              {formatTime(recordingTime)} / {formatTime(maxDuration)}
            </p>
          </div>
        </div>
      )}

      {/* Waveform Placeholder */}
      {isRecording && !isPaused && (
        <div className="flex items-center justify-center gap-1 h-20 bg-gray-50 rounded-lg">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="w-1 bg-blue-500 rounded-full animate-pulse"
              style={{
                height: `${Math.random() * 60 + 20}%`,
                animationDelay: `${i * 0.05}s`,
              }}
            />
          ))}
        </div>
      )}

      {/* Audio Playback */}
      {audioURL && !isRecording && (
        <div className="p-4 bg-gray-50 rounded-lg">
          <audio src={audioURL} controls className="w-full" />
        </div>
      )}

      {/* Controls */}
      <div className="flex items-center justify-center gap-3">
        {!isRecording && !audioURL && (
          <Button onClick={startRecording} variant="primary" size="lg">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
            </svg>
            Start Recording
          </Button>
        )}

        {isRecording && !isPaused && (
          <>
            <Button onClick={pauseRecording} variant="secondary">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              Pause
            </Button>
            <Button onClick={stopRecording} variant="danger">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
              </svg>
              Stop
            </Button>
          </>
        )}

        {isRecording && isPaused && (
          <>
            <Button onClick={resumeRecording} variant="primary">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              </svg>
              Resume
            </Button>
            <Button onClick={stopRecording} variant="danger">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
              </svg>
              Stop
            </Button>
          </>
        )}

        {audioURL && !isRecording && (
          <Button onClick={resetRecording} variant="secondary">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
            </svg>
            Record Again
          </Button>
        )}
      </div>
    </div>
  );
}
