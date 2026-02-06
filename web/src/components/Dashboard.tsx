import * as React from "react"
import { Play, Pause, Scissors, Plus, RefreshCw } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"

interface Clip {
  id: string
  name: string
  duration: string
  thumbnail: string
  type: string
}

export function Dashboard() {
  const [isPlaying, setIsPlaying] = React.useState(false)
  const [clips, setClips] = React.useState<Clip[]>([])

  const fetchClips = async () => {
    try {
        const res = await fetch("http://localhost:8000/api/clips")
        if (res.ok) {
            const data = await res.json()
            setClips(data)
        }
    } catch (e) {
        console.error("Failed to fetch clips", e)
    }
  }

  React.useEffect(() => {
    fetchClips()
    const interval = setInterval(fetchClips, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="h-full w-full bg-background text-foreground">
      <ResizablePanelGroup direction="horizontal" className="h-full rounded-lg border">
        {/* Clip Library */}
        <ResizablePanel defaultSize={20} minSize={15}>
          <div className="flex h-full flex-col">
            <div className="flex items-center px-4 py-2 border-b">
              <h2 className="text-lg font-semibold">Library</h2>
              <div className="ml-auto flex gap-1">
                <Button variant="ghost" size="icon" onClick={() => fetchClips()}>
                    <RefreshCw className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon">
                    <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <ScrollArea className="flex-1">
              <div className="p-4 grid grid-cols-2 gap-4">
                {clips.length === 0 && <div className="col-span-2 text-center text-sm text-muted-foreground">No clips loaded</div>}
                {clips.map((clip) => (
                  <Card key={clip.id} className="cursor-pointer hover:bg-accent overflow-hidden">
                    <div className="aspect-video bg-muted flex items-center justify-center text-xs text-muted-foreground">
                        {clip.type.split(".").pop()?.replace("Clip", "") || "Clip"}
                    </div>
                    <div className="p-2">
                      <p className="text-sm font-medium truncate" title={clip.id}>{clip.name}</p>
                      <p className="text-xs text-muted-foreground">{clip.duration}</p>
                    </div>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </div>
        </ResizablePanel>

        <ResizableHandle />

        {/* Main Editor Area */}
        <ResizablePanel defaultSize={80}>
          <ResizablePanelGroup direction="vertical">
            {/* Preview Player */}
            <ResizablePanel defaultSize={60}>
              <div className="flex h-full flex-col items-center justify-center bg-black/90 relative">
                <div className="text-white text-2xl font-light">Preview Player</div>
                 {/* Controls Overlay */}
                 <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-2">
                    <Button variant="secondary" size="icon" onClick={() => setIsPlaying(!isPlaying)}>
                        {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                    </Button>
                 </div>
              </div>
            </ResizablePanel>

            <ResizableHandle />

            {/* Timeline */}
            <ResizablePanel defaultSize={40}>
              <div className="flex h-full flex-col">
                <div className="flex items-center justify-between px-4 py-2 border-b bg-muted/20">
                    <span className="text-sm font-medium">Timeline</span>
                    <div className="flex gap-2">
                        <Button variant="ghost" size="icon"><Scissors className="h-4 w-4" /></Button>
                    </div>
                </div>
                <div className="flex-1 p-4 overflow-x-auto relative bg-background">
                    {/* Time Ruler */}
                    <div className="h-6 border-b mb-2 flex text-xs text-muted-foreground">
                        <span>00:00</span>
                        <span className="ml-20">00:10</span>
                        <span className="ml-20">00:20</span>
                    </div>
                    {/* Tracks */}
                    <div className="space-y-2">
                        <div className="h-12 bg-primary/20 rounded-md border border-primary/50 relative">
                             {/* Mock Track Item */}
                        </div>
                    </div>

                    {/* Playhead */}
                    <div className="absolute top-0 bottom-0 left-[100px] w-0.5 bg-red-500 z-10 pointer-events-none"></div>
                </div>
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  )
}
