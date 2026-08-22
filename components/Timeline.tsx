'use client';

import { useRef, useState } from 'react';
import { motion, useScroll, useSpring } from 'framer-motion';
import milestones from '@/data/milestones.json';
import PresentVideo from '@/components/PresentVideo';

const STEP = 420;
const LEFT_X = 220;
const RIGHT_X = 780;
const CENTER_X = 500;

function formatDate(iso: string) {
  return new Date(`${iso}T00:00:00`).toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });
}

function buildWindingPath(count: number) {
  const points = Array.from({ length: count }, (_, i) => ({
    x: i % 2 === 0 ? LEFT_X : RIGHT_X,
    y: 200 + i * STEP,
  }));

  let d = `M ${CENTER_X} 28`;
  let prevX = CENTER_X;
  let prevY = 28;

  for (const point of points) {
    d += ` C ${prevX} ${prevY + 110}, ${point.x} ${point.y - 110}, ${point.x} ${point.y}`;
    prevX = point.x;
    prevY = point.y;
  }

  const endY = 200 + count * STEP;
  d += ` C ${prevX} ${prevY + 120}, ${CENTER_X} ${endY - 80}, ${CENTER_X} ${endY}`;
  return { d, points, endY };
}

function MilestonePhoto({ src, title, id }: { src: string; title: string; id: number }) {
  const [failed, setFailed] = useState(false);

  return (
    <div className="relative mb-4 aspect-[4/3] overflow-hidden rounded-2xl border border-slate-700/80 bg-gradient-to-br from-rose-500/30 via-slate-800 to-slate-900">
      {!failed && (
        // Photos live in public/images once added (e.g. /images/milestone_1.jpg)
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={src}
          alt={title}
          className="h-full w-full object-cover"
          onError={() => setFailed(true)}
        />
      )}
      {failed && (
        <div className="flex h-full w-full flex-col items-center justify-center gap-2 text-rose-200/80">
          <span className="text-3xl">{id}</span>
          <span className="px-4 text-center text-xs tracking-wide uppercase">Capture {id}</span>
        </div>
      )}
    </div>
  );
}

export default function Timeline() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { d, points, endY } = buildWindingPath(milestones.length);
  const viewBoxHeight = endY + 40;
  const windingHeight = milestones.length * STEP + 240;

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end'],
  });
  const pathLength = useSpring(scrollYProgress, { stiffness: 400, damping: 90 });

  return (
    <div ref={containerRef} className="relative overflow-hidden bg-slate-950 text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(244,63,94,0.16),_transparent_55%)]" />

      <header className="relative z-10 px-4 pb-10 pt-20 text-center md:pt-28">
        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.35em] text-rose-400">
          A winding year
        </p>
        <h1
          className="text-4xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-pink-300 to-rose-500 md:text-6xl"
          style={{ fontFamily: 'var(--font-display), ui-serif, Georgia, serif' }}
        >
          Our Journey Together
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-slate-400">
          Scroll the path for nine little captures — each with a memory, a place, and a theme.
        </p>
      </header>

      <div className="relative mx-auto w-full max-w-5xl" style={{ height: windingHeight }}>
        <svg
          className="pointer-events-none absolute inset-0 h-full w-full"
          viewBox={`0 0 1000 ${viewBoxHeight}`}
          fill="none"
          preserveAspectRatio="xMidYMin meet"
          aria-hidden
        >
          <path
            d={d}
            stroke="rgba(244,63,94,0.18)"
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray="10 12"
          />
          <motion.path
            d={d}
            stroke="#f43f5e"
            strokeWidth="6"
            strokeLinecap="round"
            style={{ pathLength }}
          />
          {points.map((point, index) => (
            <circle
              key={milestones[index].id}
              cx={point.x}
              cy={point.y}
              r="14"
              fill="#f43f5e"
              stroke="#020617"
              strokeWidth="6"
            />
          ))}
        </svg>

        {milestones.map((item, index) => {
          const isLeft = index % 2 === 0;
          return (
            <motion.article
              key={item.id}
              initial={{ opacity: 0, y: 36 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-80px' }}
              transition={{ duration: 0.55 }}
              className={`absolute w-[min(92%,22rem)] md:w-[38%] ${
                isLeft ? 'left-4 md:left-[6%]' : 'right-4 md:right-[6%]'
              }`}
              style={{ top: 90 + index * STEP }}
            >
              <div className="rounded-3xl border border-slate-800 bg-slate-900/85 p-4 shadow-2xl backdrop-blur-md transition-colors hover:border-rose-500/40">
                <MilestonePhoto src={item.image_path} title={item.title} id={item.id} />
                <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-rose-400">
                  {formatDate(item.date)}
                </p>
                <h2
                  className="mt-1 text-2xl text-white"
                  style={{ fontFamily: 'var(--font-display), ui-serif, Georgia, serif' }}
                >
                  {item.title}
                </h2>
                <p className="mt-2 text-sm leading-relaxed text-slate-300">{item.description}</p>
                <div className="mt-4 flex flex-wrap gap-2 text-xs">
                  <span className="rounded-full border border-slate-700 bg-slate-800/80 px-3 py-1 text-slate-200">
                    {item.location}
                  </span>
                  <span className="rounded-full bg-rose-500/15 px-3 py-1 text-rose-300">
                    {item.theme}
                  </span>
                </div>
              </div>
            </motion.article>
          );
        })}
      </div>

      <PresentVideo />
    </div>
  );
}
