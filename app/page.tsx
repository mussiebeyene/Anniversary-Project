import Timeline from '@/components/Timeline';
import MusicPlayer from '@/components/MusicPlayer';
import ChatbotModal from '@/components/ChatbotModal';

export default function Home() {
  return (
    <main className="relative min-h-screen bg-slate-950">
      <Timeline />
      <MusicPlayer />
      <ChatbotModal />
    </main>
  );
}
