import * as React from "react"
import { Send, Settings, User, Bot, Loader2 } from "lucide-react"

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
  { role: "assistant", content: "Hello! I am your AI Video Editor Assistant. I can help you edit videos using MoviePy. Please configure your API keys in settings." }
]

export function Chat() {
  const [messages, setMessages] = React.useState(INITIAL_MESSAGES)
  const [input, setInput] = React.useState("")
  const [isLoading, setIsLoading] = React.useState(false)
  const [openSettings, setOpenSettings] = React.useState(false)

  // Load API keys from local storage if available
  const [apiKeys, setApiKeys] = React.useState({
    openai: "",
    anthropic: "",
    gemini: "",
  })

  React.useEffect(() => {
    const stored = localStorage.getItem("mcp_api_keys")
    if (stored) {
        setApiKeys(JSON.parse(stored))
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
            headers: { "Content-Type": "application/json" },
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
    } catch (error: any) {
        setMessages(prev => [...prev, { role: "assistant", content: "Error: " + error.message }])
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
    <div className="flex h-full flex-col border-l bg-muted/10">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-background">
        <h3 className="font-semibold flex items-center gap-2"><Bot className="h-4 w-4" /> AI Assistant</h3>
        <Dialog open={openSettings} onOpenChange={setOpenSettings}>
            <DialogTrigger asChild>
                <Button variant="ghost" size="icon">
                    <Settings className="h-4 w-4" />
                </Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>API Keys Configuration</DialogTitle>
                    <DialogDescription>
                        Enter your API keys to enable LLM capabilities. These are stored locally in your browser.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid gap-2">
                        <label htmlFor="openai" className="text-sm font-medium">OpenAI API Key</label>
                        <Input
                            id="openai"
                            type="password"
                            value={apiKeys.openai}
                            onChange={(e) => setApiKeys({...apiKeys, openai: e.target.value})}
                            placeholder="sk-..."
                        />
                    </div>
                    <div className="grid gap-2">
                         <label htmlFor="anthropic" className="text-sm font-medium">Anthropic API Key</label>
                        <Input
                            id="anthropic"
                            type="password"
                            value={apiKeys.anthropic}
                            onChange={(e) => setApiKeys({...apiKeys, anthropic: e.target.value})}
                            placeholder="sk-ant-..."
                        />
                    </div>
                    <div className="grid gap-2">
                         <label htmlFor="gemini" className="text-sm font-medium">Gemini API Key</label>
                        <Input
                            id="gemini"
                            type="password"
                            value={apiKeys.gemini}
                            onChange={(e) => setApiKeys({...apiKeys, gemini: e.target.value})}
                            placeholder="AI..."
                        />
                    </div>
                </div>
                <DialogFooter>
                    <Button onClick={saveApiKeys}>Save</Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
            {messages.map((msg, i) => (
                <div key={i} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                    <Avatar className="h-8 w-8">
                        <AvatarFallback className={msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}>
                            {msg.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                        </AvatarFallback>
                    </Avatar>
                    <div className={`rounded-lg p-3 text-sm max-w-[80%] whitespace-pre-wrap ${
                        msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-foreground"
                    }`}>
                        {msg.content}
                    </div>
                </div>
            ))}
             {isLoading && (
                <div className="flex gap-3">
                     <Avatar className="h-8 w-8"><AvatarFallback><Bot className="h-4 w-4" /></AvatarFallback></Avatar>
                     <div className="bg-muted rounded-lg p-3 flex items-center">
                        <Loader2 className="h-4 w-4 animate-spin" />
                     </div>
                </div>
            )}
            <div ref={scrollRef} />
        </div>
      </ScrollArea>

      <div className="p-4 border-t bg-background">
        <div className="flex gap-2">
            <Input
                placeholder="Ask to edit video..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
            />
            <Button size="icon" onClick={handleSend} disabled={isLoading || !input.trim()}>
                <Send className="h-4 w-4" />
            </Button>
        </div>
      </div>
    </div>
  )
}
