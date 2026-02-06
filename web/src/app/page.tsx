"use client"

import * as React from "react"
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import { Dashboard } from "@/components/Dashboard"
import { Chat } from "@/components/Chat"

export default function Home() {
  return (
    <main className="h-screen w-screen overflow-hidden bg-background">
      <ResizablePanelGroup direction="horizontal">
        {/* Main Dashboard Area */}
        <ResizablePanel defaultSize={75} minSize={50}>
            <Dashboard />
        </ResizablePanel>

        <ResizableHandle />

        {/* Chat Sidebar */}
        <ResizablePanel defaultSize={25} minSize={20} maxSize={40}>
            <Chat />
        </ResizablePanel>
      </ResizablePanelGroup>
    </main>
  )
}
