'use client';

import { useRef, useState } from 'react';

export default function PresentVideo() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);
  const [missing, setMissing] = useState(false);

  const handlePlay = () => {
    const video = videoRef.current;
    if (!video || missing) return;
    void video
      .play()
      .then(() => setPlaying(true))
      .catch(() => setMissing(true));
  };

  return (
    <section className="relative z-10 mx-auto w-full max-w-3xl px-4 pb-36 pt-6">
      <h2
        className="mb-6 text-center text-sm font-semibold tracking-[0.55em] text-rose-400"
        style={{ fontFamily: 'var(--font-display), ui-serif, Georgia, serif' }}
      >
        PRESENT
      </h2>

      <div className="relative overflow-hidden rounded-3xl border border-slate-800 bg-slate-900 shadow-2xl aspect-video">
        <video
          ref={videoRef}
          src="/videos/present.mp4"
          className={`h-full w-full object-cover ${playing ? 'block' : 'hidden'}`}
          controls={playing}
          playsInline
          onError={() => setMissing(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => setPlaying(false)}
        />

        {!playing && (
          <button
            type="button"
            onClick={handlePlay}
            className="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-[radial-gradient(circle_at_center,_rgba(244,63,94,0.18),_#0f172a_70%)] text-white"
            aria-label="Play present video"
          >
            <span className="flex h-20 w-20 items-center justify-center rounded-full border-2 border-rose-300/80 bg-rose-500/90 shadow-lg shadow-rose-500/30">
              <svg viewBox="0 0 24 24" className="ml-1 h-8 w-8 fill-white" aria-hidden>
                <path d="M8 5v14l11-7z" />
              </svg>
            </span>
            <span className="text-sm tracking-[0.25em] text-slate-300">
              {missing ? 'Add public/videos/present.mp4' : 'Play'}
            </span>
          </button>
        )}
      </div>
    </section>
  );
}
