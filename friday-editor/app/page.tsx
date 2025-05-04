"use client"

import { useState, useEffect } from "react"
import MarkdownEditor from "@/components/markdown-editor"
import NoteSidebar from "@/components/note-sidebar"
import { type Note, NoteStorage } from "@/lib/note-storage"

export default function Home() {
  const [currentNote, setCurrentNote] = useState<Note | null>(null)
  const [notes, setNotes] = useState<Note[]>([])

  // Load notes on initial render
  useEffect(() => {
    const noteStorage = new NoteStorage()
    noteStorage.initializeWithSampleData()
    const loadedNotes = noteStorage.getNotes()
    setNotes(loadedNotes)

    // Set the first note as current if available
    if (loadedNotes.length > 0) {
      setCurrentNote(loadedNotes[0])
    }
  }, [])

  // Handle note selection
  const handleSelectNote = (note: Note) => {
    setCurrentNote(note)
  }

  // Handle note updates
  const handleUpdateNote = (updatedNote: Note) => {
    setNotes((prevNotes) => prevNotes.map((note) => (note.id === updatedNote.id ? updatedNote : note)))
  }

  return (
    <div className="flex h-screen bg-white">
      <NoteSidebar onSelectNote={handleSelectNote} selectedNoteId={currentNote?.id || null} />
      <MarkdownEditor currentNote={currentNote} onUpdateNote={handleUpdateNote} />
    </div>
  )
}
