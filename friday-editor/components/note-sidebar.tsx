"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Search, Plus, Trash2 } from "lucide-react"
import { type Note, NoteStorage } from "@/lib/note-storage"

interface NoteSidebarProps {
  onSelectNote: (note: Note) => void
  selectedNoteId: string | null
}

export default function NoteSidebar({ onSelectNote, selectedNoteId }: NoteSidebarProps) {
  const [notes, setNotes] = useState<Note[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [isSearching, setIsSearching] = useState(false)

  // Load notes from storage
  useEffect(() => {
    const noteStorage = new NoteStorage()
    noteStorage.initializeWithSampleData()
    setNotes(noteStorage.getNotes())
  }, [])

  // Create a new note
  const createNewNote = () => {
    const noteStorage = new NoteStorage()
    const newNote: Note = {
      id: `note-${Date.now()}`,
      title: "Untitled Note",
      content: "",
      preview: "Empty note...",
      createdAt: Date.now(),
      updatedAt: Date.now(),
    }

    noteStorage.saveNote(newNote)
    setNotes(noteStorage.getNotes())
    onSelectNote(newNote)
  }

  // Delete a note
  const deleteNote = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm("Are you sure you want to delete this note?")) {
      const noteStorage = new NoteStorage()
      noteStorage.deleteNote(id)
      setNotes(noteStorage.getNotes())

      // If the deleted note was selected, select the first available note
      if (id === selectedNoteId && notes.length > 1) {
        const remainingNotes = notes.filter((note) => note.id !== id)
        if (remainingNotes.length > 0) {
          onSelectNote(remainingNotes[0])
        }
      }
    }
  }

  // Filter notes based on search term
  const filteredNotes = searchTerm
    ? notes.filter(
        (note) =>
          note.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          note.content.toLowerCase().includes(searchTerm.toLowerCase()),
      )
    : notes

  return (
    <div className="w-80 border-r h-full flex flex-col">
      <div className="p-4 border-b flex items-center justify-between">
        <h1 className="text-lg font-medium flex items-center">
          Notes
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="lucide lucide-chevron-down ml-1 h-4 w-4"
          >
            <path d="m6 9 6 6 6-6" />
          </svg>
        </h1>
        <div className="flex space-x-2">
          <button className="p-2 rounded hover:bg-gray-100" onClick={() => createNewNote()} title="New Note">
            <Plus className="h-5 w-5" />
          </button>
          <button
            className="p-2 rounded hover:bg-gray-100"
            onClick={() => setIsSearching(!isSearching)}
            title="Search Notes"
          >
            <Search className="h-5 w-5" />
          </button>
        </div>
      </div>

      {isSearching && (
        <div className="p-2 border-b">
          <input
            type="text"
            placeholder="Search notes..."
            className="w-full p-2 border rounded"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        {filteredNotes.map((note) => (
          <div
            key={note.id}
            className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${selectedNoteId === note.id ? "bg-gray-100" : ""}`}
            onClick={() => onSelectNote(note)}
          >
            <div className="flex justify-between">
              <h2 className="font-medium mb-1 flex items-center">
                {note.emoji && <span className="mr-2">{note.emoji}</span>}
                {note.title}
              </h2>
              <button
                className="p-1 rounded hover:bg-gray-200"
                onClick={(e) => deleteNote(note.id, e)}
                title="Delete Note"
              >
                <Trash2 className="h-4 w-4 text-gray-500" />
              </button>
            </div>
            <p className="text-gray-600 text-sm line-clamp-2">{note.preview}</p>

            {note.image && (
              <div className="mt-2">
                <img
                  src={note.image || "/placeholder.svg"}
                  alt={note.title}
                  className="rounded w-full h-24 object-cover"
                />
              </div>
            )}

            <div className="mt-2 text-xs text-gray-500">{new Date(note.updatedAt).toLocaleDateString()}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
