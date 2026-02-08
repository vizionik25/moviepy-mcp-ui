import * as React from "react"
import { RefreshCw, Plus, Search, Film, Image as ImageIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Input } from "@/components/ui/input"
import { Clip } from "@/lib/types"

interface LibraryPanelProps {
  className?: string
}

export function LibraryPanel({ className }: LibraryPanelProps) {
  const [clips, setClips] = React.useState<Clip[]>([])
  const [loading, setLoading] = React.useState(false)

  const fetchClips = async () => {
    setLoading(true)
    try {
        const res = await fetch("http://localhost:8000/api/clips")
        if (res.ok) {
            const data = await res.json()
            setClips(data)
        }
    } catch (e) {
        console.error("Failed to fetch clips", e)
    } finally {
        setLoading(false)
    }
  }

  React.useEffect(() => {
    fetchClips()
    // Optional: Auto-refresh
    const interval = setInterval(fetchClips, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className={`flex h-full flex-col bg-sidebar border-r ${className}`}>
      {/* Header */}
      <div className="p-4 border-b space-y-4">
        <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Media</h2>
            <div className="flex gap-1">
                <Button variant="ghost" size="icon" onClick={() => fetchClips()} disabled={loading} className="h-7 w-7" aria-label="Refresh clips">
                    <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
                </Button>
                <Button variant="ghost" size="icon" className="h-7 w-7" aria-label="Add clip">
                    <Plus className="h-3.5 w-3.5" />
                </Button>
            </div>
        </div>
        <div className="relative">
            <Search className="absolute left-2 top-2 h-3.5 w-3.5 text-muted-foreground" />
            <Input placeholder="Search..." className="pl-8 h-8 text-xs bg-muted/50 border-none" />
        </div>
      </div>

      {/* Grid */}
      <ScrollArea className="flex-1">
        <div className="p-3 grid grid-cols-2 gap-3">
          {clips.length === 0 && !loading && (
             <div className="col-span-2 py-10 text-center text-xs text-muted-foreground">
                No media loaded
             </div>
          )}
          {clips.map((clip) => (
            <Card key={clip.id} className="group cursor-pointer overflow-hidden border-none bg-card hover:ring-1 hover:ring-primary transition-all">
              <div className="aspect-video bg-muted relative flex items-center justify-center">
                  {clip.thumbnail ? (
                      <img src={clip.thumbnail} alt={clip.name} className="w-full h-full object-cover" />
                  ) : (
                      <div className="text-muted-foreground">
                        {clip.type.includes('image') ? <ImageIcon className="h-6 w-6 opacity-50" /> : <Film className="h-6 w-6 opacity-50" />}
                      </div>
                  )}
                  <div className="absolute bottom-1 right-1 bg-black/70 text-[10px] text-white px-1 rounded-sm">
                    {clip.duration}
                  </div>
              </div>
              <div className="p-2 space-y-1">
                <p className="text-xs font-medium truncate text-foreground/90" title={clip.name}>{clip.name}</p>
                <p className="text-[10px] text-muted-foreground uppercase">{clip.type.split("/").pop()}</p>
              </div>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </div>
  )
}
