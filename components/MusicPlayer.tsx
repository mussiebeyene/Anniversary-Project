'use client';

import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

const PLAYLIST_EMBED =
  'https://open.spotify.com/embed/playlist/4Rl7sueXTe559B74qQRTtF';

export default function MusicPlayer() {
  const [open, setOpen] = useState(false);

  return (
    <div className="fixed bottom-6 left-6 z-40">
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 12, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.96 }}
            transition={{ duration: 0.2 }}
            className="absolute bottom-20 left-0 overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl"
          >
            <iframe
              title="Our favorite songs"
              src={PLAYLIST_EMBED}
              width="280"
              height="152"
              allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
              loading="lazy"
              className="block"
            />
          </motion.div>
        )}
      </AnimatePresence>

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex h-16 w-16 items-center justify-center rounded-full bg-rose-500 text-white shadow-2xl transition-transform hover:scale-105 hover:bg-rose-600 active:scale-95"
        aria-label="Toggle favorite songs playlist"
        aria-expanded={open}
      >
        <svg viewBox="0 0 24 24" className="h-7 w-7 fill-current" aria-hidden>
          <path d="M12 3v10.55A4 4 0 1 0 14 17V7h4V3h-6z" />
        </svg>
      </button>
    </div>
  );
}
