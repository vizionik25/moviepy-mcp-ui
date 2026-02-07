import * as React from "react"
import { MonitorPlay, Download, ChevronRight, Menu } from "lucide-react"
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"

import { LibraryPanel } from "@/components/panels/LibraryPanel"
import { PlayerPanel } from "@/components/panels/PlayerPanel"
import { TimelinePanel } from "@/components/panels/TimelinePanel"
import { ChatPanel } from "@/components/panels/ChatPanel"

export function EditorLayout() {
  const [isPlaying, setIsPlaying] = React.useState(false)

  return (
    <div className="h-screen w-screen flex flex-col bg-background text-foreground overflow-hidden font-sans selection:bg-primary/30">
      {/* Header */}
      <header className="h-12 border-b border-zinc-800 bg-zinc-950 flex items-center px-4 justify-between shrink-0 z-50">
        <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-primary font-bold tracking-tight">
                <div className="h-8 w-8 bg-primary/20 rounded-lg flex items-center justify-center">
                    <MonitorPlay className="h-5 w-5 text-primary" />
                </div>
                <span>AI Editor</span>
            </div>
            <Separator orientation="vertical" className="h-6 bg-zinc-800" />
            <div className="flex items-center gap-2 text-sm text-zinc-400">
                <span>My Project</span>
                <ChevronRight className="h-4 w-4" />
                <span className="text-zinc-200">Untitled Video</span>
            </div>
        </div>

        <div className="flex items-center gap-2">
             <Button variant="ghost" size="sm" className="text-zinc-400 hover:text-white">
                <Menu className="h-4 w-4 mr-2" /> Menu
             </Button>
             <Button size="sm" className="bg-primary hover:bg-primary/90 text-primary-foreground font-medium shadow-lg shadow-primary/20">
                <Download className="h-4 w-4 mr-2" /> Export
             </Button>
        </div>
      </header>

      {/* Main Workspace */}
      <div className="flex-1 overflow-hidden">
        <ResizablePanelGroup direction="vertical" className="h-full">
            {/* Top Section: Library | Player | Chat */}
            <ResizablePanel defaultSize={65} minSize={30}>
                <ResizablePanelGroup direction="horizontal" className="h-full">
                    {/* Library */}
                    <ResizablePanel defaultSize={20} minSize={15} maxSize={30} className="bg-zinc-900/50">
                        <LibraryPanel />
                    </ResizablePanel>

                    <ResizableHandle className="bg-zinc-800 w-[1px] hover:w-1 transition-all hover:bg-primary" />

                    {/* Player */}
                    <ResizablePanel defaultSize={55} minSize={30} className="bg-black">
                        <PlayerPanel isPlaying={isPlaying} onTogglePlay={() => setIsPlaying(!isPlaying)} />
                    </ResizablePanel>

                    <ResizableHandle className="bg-zinc-800 w-[1px] hover:w-1 transition-all hover:bg-primary" />

                    {/* Chat */}
                    <ResizablePanel defaultSize={25} minSize={20} maxSize={40} className="bg-background">
                        <ChatPanel />
                    </ResizablePanel>
                </ResizablePanelGroup>
            </ResizablePanel>

            <ResizableHandle className="bg-zinc-800 h-[1px] hover:h-1 transition-all hover:bg-primary" />

            {/* Bottom Section: Timeline */}
            <ResizablePanel defaultSize={35} minSize={15}>
                <TimelinePanel />
            </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  )
}
