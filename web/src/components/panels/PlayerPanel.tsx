import * as React from "react"
import { Play, Pause, Settings, Maximize2, SkipBack, SkipForward } from "lucide-react"
import { Button } from "@/components/ui/button"

interface PlayerPanelProps {
  className?: string
  isPlaying: boolean
  onTogglePlay: () => void
}

export function PlayerPanel({ className, isPlaying, onTogglePlay }: PlayerPanelProps) {
  return (
    <div className={`flex h-full w-full flex-col bg-black/95 relative ${className}`}>
      {/* Top Bar (Overlay) */}
      <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-start z-10 pointer-events-none">
        <div className="text-xs font-mono text-white/50 pointer-events-auto">00:00:00:00</div>
        <div className="flex gap-2 pointer-events-auto">
            <Button variant="ghost" size="icon" className="h-6 w-6 hover:bg-white/10 text-white/70" aria-label="Settings">
                <Settings className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="icon" className="h-6 w-6 hover:bg-white/10 text-white/70" aria-label="Maximize">
                <Maximize2 className="h-3 w-3" />
            </Button>
        </div>
      </div>

      {/* Main Screen */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="aspect-video w-full max-w-4xl bg-zinc-900 rounded-lg border border-zinc-800 shadow-2xl flex items-center justify-center relative overflow-hidden group">
            {/* Placeholder Content */}
            <div className="text-zinc-700 font-light text-2xl select-none">Preview Player</div>

            {/* Play Overlay (Optional) */}
            {!isPlaying && (
                <div className="absolute inset-0 bg-black/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <Play className="h-12 w-12 text-white/80 fill-white/80" />
                </div>
            )}
        </div>
      </div>

      {/* Controls Bar */}
      <div className="h-14 bg-zinc-950 border-t border-zinc-900 px-4 flex items-center justify-center gap-4">
        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground" aria-label="Previous frame">
            <SkipBack className="h-4 w-4" />
        </Button>
        <Button
            variant="outline"
            size="icon"
            className="h-10 w-10 rounded-full border-primary/20 bg-primary/10 text-primary hover:bg-primary/20 hover:text-primary-foreground transition-all"
            onClick={onTogglePlay}
            aria-label={isPlaying ? "Pause" : "Play"}
        >
            {isPlaying ? <Pause className="h-4 w-4 fill-current" /> : <Play className="h-4 w-4 fill-current ml-0.5" />}
        </Button>
        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground" aria-label="Next frame">
            <SkipForward className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
