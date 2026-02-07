import * as React from "react"
import { Send, Settings, User, Bot, Loader2, Sparkles } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog"

// Initial welcome message
const INITIAL_MESSAGES = [
  { role: "assistant", content: "Hello! I am your AI Video Copilot. How can I help you edit today?" }
]

interface ChatPanelProps {
  className?: string
}

export function ChatPanel({ className }: ChatPanelProps) {
  const [messages, setMessages] = React.useState(INITIAL_MESSAGES)
  const [input, setInput] = React.useState("")
  const [isLoading, setIsLoading] = React.useState(false)
  const [openSettings, setOpenSettings] = React.useState(false)

  // Load API keys from local storage if available
  const [apiKeys, setApiKeys] = React.useState({
    openai: "",
    anthropic: "",
    gemini: "",
    serverSecret: "",
  })

  React.useEffect(() => {
    if (typeof window !== "undefined") {
        const stored = localStorage.getItem("mcp_api_keys")
        if (stored) {
            const parsed = JSON.parse(stored)
            setApiKeys({
                openai: parsed.openai || "",
                anthropic: parsed.anthropic || "",
                gemini: parsed.gemini || "",
                serverSecret: parsed.serverSecret || ""
            })
        }
    }
  }, [])

  const saveApiKeys = () => {
      localStorage.setItem("mcp_api_keys", JSON.stringify(apiKeys))
      setOpenSettings(false)
  }

  const scrollRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    if (scrollRef.current) {
        scrollRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return
    const userMsg = { role: "user", content: input }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setInput("")
    setIsLoading(true)

    try {
        const res = await fetch("http://localhost:8000/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Stitch-Secret": apiKeys.serverSecret || "stitch-secret"
            },
            body: JSON.stringify({
                messages: newMessages,
                api_keys: apiKeys
            })
        })

        if (!res.ok) {
            const err = await res.json()
            throw new Error(err.detail || "Failed to send message")
        }

        const data = await res.json()
        setMessages(prev => [...prev, { role: "assistant", content: data.content }])
    } catch (error: unknown) {
        setMessages(prev => [...prev, { role: "assistant", content: "Error: " + ((error as Error).message || "Unknown error") }])
    } finally {
        setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        handleSend()
    }
  }

  return (
    <div className={`flex h-full flex-col bg-background border-l border-zinc-800/50 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800/50 bg-muted/20">
        <h3 className="text-sm font-medium flex items-center gap-2 text-zinc-300">
            <Sparkles className="h-4 w-4 text-purple-400" /> Copilot
        </h3>
        <Dialog open={openSettings} onOpenChange={setOpenSettings}>
            <DialogTrigger asChild>
                <Button variant="ghost" size="icon" className="h-7 w-7 text-zinc-400 hover:text-white">
                    <Settings className="h-4 w-4" />
                </Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>AI Model Configuration</DialogTitle>
                    <DialogDescription>
                        Configure your API keys for the best experience.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid gap-2">
                         <label htmlFor="serverSecret" className="text-xs font-medium text-muted-foreground">Server Secret (Stitch)</label>
                        <Input
                            id="serverSecret"
                            type="password"
                            value={apiKeys.serverSecret}
                            onChange={(e) => setApiKeys({...apiKeys, serverSecret: e.target.value})}
                            placeholder="stitch-secret"
                            className="bg-muted border-none"
                        />
                    </div>
                    <div className="grid gap-2">
                        <label htmlFor="openai" className="text-xs font-medium text-muted-foreground">OpenAI API Key</label>
                        <Input
                            id="openai"
                            type="password"
                            value={apiKeys.openai}
                            onChange={(e) => setApiKeys({...apiKeys, openai: e.target.value})}
                            placeholder="sk-..."
                            className="bg-muted border-none"
                        />
                    </div>
                    <div className="grid gap-2">
                         <label htmlFor="anthropic" className="text-xs font-medium text-muted-foreground">Anthropic API Key</label>
                        <Input
                            id="anthropic"
                            type="password"
                            value={apiKeys.anthropic}
                            onChange={(e) => setApiKeys({...apiKeys, anthropic: e.target.value})}
                            placeholder="sk-ant-..."
                            className="bg-muted border-none"
                        />
                    </div>
                    <div className="grid gap-2">
                         <label htmlFor="gemini" className="text-xs font-medium text-muted-foreground">Gemini API Key</label>
                        <Input
                            id="gemini"
                            type="password"
                            value={apiKeys.gemini}
                            onChange={(e) => setApiKeys({...apiKeys, gemini: e.target.value})}
                            placeholder="AI..."
                            className="bg-muted border-none"
                        />
                    </div>
                </div>
                <DialogFooter>
                    <Button onClick={saveApiKeys}>Save Configuration</Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4 bg-zinc-950/30">
        <div className="space-y-4">
            {messages.map((msg, i) => (
                <div key={i} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                    <Avatar className="h-7 w-7 border border-zinc-700">
                        <AvatarFallback className={`text-[10px] ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-zinc-800 text-zinc-400"}`}>
                            {msg.role === "user" ? <User className="h-3 w-3" /> : <Bot className="h-3 w-3" />}
                        </AvatarFallback>
                    </Avatar>
                    <div className={`rounded-xl p-3 text-xs max-w-[85%] whitespace-pre-wrap leading-relaxed shadow-sm ${
                        msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-zinc-800 text-zinc-200 border border-zinc-700/50"
                    }`}>
                        {msg.content}
                    </div>
                </div>
            ))}
             {isLoading && (
                <div className="flex gap-3">
                     <Avatar className="h-7 w-7 border border-zinc-700"><AvatarFallback className="bg-zinc-800"><Bot className="h-3 w-3 text-zinc-400" /></AvatarFallback></Avatar>
                     <div className="bg-zinc-800/50 border border-zinc-800 rounded-xl p-3 flex items-center shadow-sm">
                        <Loader2 className="h-3 w-3 animate-spin text-zinc-400" />
                     </div>
                </div>
            )}
            <div ref={scrollRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-3 border-t border-zinc-800/50 bg-background/50 backdrop-blur-sm">
        <div className="flex gap-2 relative">
            <Input
                placeholder="Ask Copilot to edit..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
                className="bg-zinc-900 border-zinc-800 focus:border-primary/50 pl-3 pr-10 py-5 text-sm shadow-inner"
            />
            <Button
                size="icon"
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className="absolute right-1 top-1 h-8 w-8 rounded-lg bg-primary/20 text-primary hover:bg-primary/30 transition-colors"
            >
                <Send className="h-4 w-4" />
            </Button>
        </div>
      </div>
    </div>
  )
}
