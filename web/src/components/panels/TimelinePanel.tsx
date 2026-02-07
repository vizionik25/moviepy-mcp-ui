import * as React from "react"
import { Scissors, MousePointer2, GripHorizontal, Plus, ZoomIn, ZoomOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"

interface TimelinePanelProps {
  className?: string
}

export function TimelinePanel({ className }: TimelinePanelProps) {
  return (
    <div className={`flex h-full flex-col bg-background/50 ${className}`}>
      {/* Timeline Toolbar */}
      <div className="h-10 border-b flex items-center justify-between px-2 bg-muted/20">
        <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" className="h-7 w-7"><MousePointer2 className="h-3.5 w-3.5" /></Button>
            <Button variant="ghost" size="icon" className="h-7 w-7"><Scissors className="h-3.5 w-3.5" /></Button>
            <div className="w-px h-4 bg-border mx-1" />
            <Button variant="ghost" size="icon" className="h-7 w-7"><GripHorizontal className="h-3.5 w-3.5" /></Button>
        </div>
        <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="h-7 w-7"><ZoomOut className="h-3.5 w-3.5" /></Button>
            <div className="w-24 h-1 bg-muted rounded-full overflow-hidden">
                <div className="w-1/3 h-full bg-primary/50" />
            </div>
            <Button variant="ghost" size="icon" className="h-7 w-7"><ZoomIn className="h-3.5 w-3.5" /></Button>
        </div>
      </div>

      {/* Timeline Area */}
      <div className="flex-1 relative flex flex-col overflow-hidden">
        {/* Ruler */}
        <div className="h-6 border-b bg-muted/10 flex text-[10px] text-muted-foreground select-none">
             {/* Simple Ruler Mockup */}
             {Array.from({ length: 20 }).map((_, i) => (
                 <div key={i} className="flex-1 border-r border-border/20 flex pl-1 items-end pb-0.5">
                    {i % 2 === 0 ? `00:0${i}` : ''}
                 </div>
             ))}
        </div>

        {/* Tracks Container */}
        <ScrollArea className="flex-1 bg-black/20">
            <div className="min-h-full min-w-[800px] p-2 space-y-2 relative">
                {/* Playhead Line (Overlay) */}
                <div className="absolute top-0 bottom-0 left-[120px] w-px bg-red-500 z-20 pointer-events-none">
                    <div className="absolute -top-3 -left-1.5 w-3 h-3 bg-red-500 transform rotate-45 rounded-sm" />
                </div>

                {/* Track 1 */}
                <div className="h-16 bg-zinc-900/50 rounded-lg border border-zinc-800/50 relative group">
                    <div className="absolute left-0 top-0 bottom-0 w-24 border-r border-zinc-800 flex items-center justify-center text-xs text-muted-foreground bg-zinc-900/80 z-10">
                        Video 1
                    </div>
                    {/* Clip */}
                    <div className="absolute left-[120px] top-1 bottom-1 w-[200px] bg-primary/20 border border-primary/40 rounded-md flex items-center px-2 text-xs text-primary-foreground/80 overflow-hidden cursor-pointer hover:bg-primary/30 transition-colors">
                        <span className="truncate">main_footage.mp4</span>
                    </div>
                </div>

                {/* Track 2 */}
                <div className="h-16 bg-zinc-900/50 rounded-lg border border-zinc-800/50 relative">
                     <div className="absolute left-0 top-0 bottom-0 w-24 border-r border-zinc-800 flex items-center justify-center text-xs text-muted-foreground bg-zinc-900/80 z-10">
                        Audio 1
                    </div>
                     {/* Clip */}
                    <div className="absolute left-[150px] top-1 bottom-1 w-[300px] bg-emerald-500/20 border border-emerald-500/40 rounded-md flex items-center px-2 text-xs text-emerald-100 overflow-hidden cursor-pointer hover:bg-emerald-500/30 transition-colors">
                        <span className="truncate">background_music.mp3</span>
                    </div>
                </div>

                 {/* Track 3 (Empty) */}
                 <div className="h-16 bg-zinc-900/30 rounded-lg border border-dashed border-zinc-800/30 flex items-center justify-center text-zinc-800 hover:bg-zinc-900/50 transition-colors cursor-pointer">
                    <Plus className="h-4 w-4 mr-2" /> Add Track
                </div>
            </div>
            <ScrollBar orientation="horizontal" />
        </ScrollArea>
      </div>
    </div>
  )
}
