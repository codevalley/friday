"use client"

import type React from "react"

import { useEditor, EditorContent } from "@tiptap/react"
import StarterKit from "@tiptap/starter-kit"
import Placeholder from "@tiptap/extension-placeholder"
import Image from "@tiptap/extension-image"
import Table from "@tiptap/extension-table"
import TableRow from "@tiptap/extension-table-row"
import TableCell from "@tiptap/extension-table-cell"
import TableHeader from "@tiptap/extension-table-header"
import Highlight from "@tiptap/extension-highlight"
import Link from "@tiptap/extension-link"
import TaskList from "@tiptap/extension-task-list"
import TaskItem from "@tiptap/extension-task-item"
import TextAlign from "@tiptap/extension-text-align"
import { useEffect, useState, useRef, useCallback } from "react"
import { EditorToolbar } from "./editor-toolbar"
import { type Note, NoteStorage, generatePreview } from "@/lib/note-storage"
import { KeyboardShortcuts, ImageShortcut, TagExtension, TableControlsExtension } from "@/lib/editor-extensions"
import debounce from "lodash/debounce"

interface MarkdownEditorProps {
  currentNote: Note | null
  onUpdateNote: (updatedNote: Note) => void
}

export default function MarkdownEditor({ currentNote, onUpdateNote }: MarkdownEditorProps) {
  const [content, setContent] = useState<string>("")
  const editorContainerRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [wordCount, setWordCount] = useState<number>(0)

  // Debounced save function to prevent excessive saves
  const saveNoteDebounced = useCallback(
    debounce((html: string) => {
      if (currentNote) {
        const updatedNote = {
          ...currentNote,
          content: html,
          preview: generatePreview(html),
          updatedAt: Date.now(),
        }

        const noteStorage = new NoteStorage()
        noteStorage.saveNote(updatedNote)
        onUpdateNote(updatedNote)
      }
    }, 500),
    [currentNote, onUpdateNote],
  )

  // Initialize the editor
  const editor = useEditor(
    {
      extensions: [
        StarterKit.configure({
          heading: { levels: [1, 2, 3] },
          bulletList: {
            keepMarks: true,
            keepAttributes: false,
          },
          orderedList: {
            keepMarks: true,
            keepAttributes: false,
          },
        }),
        Placeholder.configure({
          placeholder: "Start writing…",
        }),
        Image.configure({
          allowBase64: true,
          inline: false,
        }),
        Table.configure({
          resizable: true,
        }),
        TableRow,
        TableCell,
        TableHeader,
        Highlight,
        Link.configure({
          openOnClick: false,
        }),
        TaskList.configure({
          HTMLAttributes: {
            class: "task-list",
          },
        }),
        TaskItem.configure({
          nested: true,
          HTMLAttributes: {
            class: "task-item",
          },
        }),
        TextAlign.configure({
          types: ["heading", "paragraph"],
        }),
        KeyboardShortcuts,
        ImageShortcut,
        TagExtension,
        TableControlsExtension,
      ],
      content: currentNote?.content || "",
      onUpdate: ({ editor }) => {
        const html = editor.getHTML()
        setContent(html)
        saveNoteDebounced(html)

        // Update word count
        const text = editor.getText()
        const words = text.split(/\s+/).filter((word) => word.length > 0)
        setWordCount(words.length)
      },
      autofocus: "end",
      editorProps: {
        attributes: {
          class: "prose focus:outline-none",
        },
      },
    },
    [currentNote, saveNoteDebounced],
  )

  // Handle image upload
  const handleImageUpload = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  const onImageSelected = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0]
      if (file && editor) {
        const reader = new FileReader()
        reader.onload = (e) => {
          const result = e.target?.result as string
          if (result) {
            editor.chain().focus().setImage({ src: result }).run()
          }
        }
        reader.readAsDataURL(file)
        // Reset the input
        event.target.value = ""
      }
    },
    [editor],
  )

  // Update editor content when the current note changes
  useEffect(() => {
    if (editor && currentNote) {
      editor.commands.setContent(currentNote.content)

      // Update word count for the new note
      const text = editor.getText()
      const words = text.split(/\s+/).filter((word) => word.length > 0)
      setWordCount(words.length)
    }
  }, [currentNote, editor])

  // Add effect to remove focus styles from the editor
  useEffect(() => {
    if (editor) {
      const element = editor.view.dom

      // Apply inline styles to ensure no focus outline
      element.style.outline = "none"
      element.style.border = "none"
      element.style.boxShadow = "none"

      // Remove the focus outline when the editor gets focus
      const handleFocus = () => {
        element.style.outline = "none"
        element.style.border = "none"
        element.style.boxShadow = "none"
      }

      element.addEventListener("focus", handleFocus)

      return () => {
        element.removeEventListener("focus", handleFocus)
      }
    }
  }, [editor])

  // Listen for custom image upload event
  useEffect(() => {
    const handleImageUploadShortcut = () => {
      handleImageUpload()
    }

    document.addEventListener("tiptap-image-upload", handleImageUploadShortcut)

    return () => {
      document.removeEventListener("tiptap-image-upload", handleImageUploadShortcut)
    }
  }, [handleImageUpload])

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden" ref={editorContainerRef}>
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center space-x-2">
          <button
            className={`p-2 rounded hover:bg-gray-100 ${editor?.isActive("bold") ? "bg-gray-200" : ""}`}
            onClick={() => editor?.chain().focus().toggleBold().run()}
            title="Bold (Ctrl+B)"
          >
            <span className="sr-only">Bold</span>
            <span className="font-bold">B</span>
          </button>
          <button
            className={`p-2 rounded hover:bg-gray-100 ${editor?.isActive("italic") ? "bg-gray-200" : ""}`}
            onClick={() => editor?.chain().focus().toggleItalic().run()}
            title="Italic (Ctrl+I)"
          >
            <span className="sr-only">Italic</span>
            <span className="italic">I</span>
          </button>
          <button
            className={`p-2 rounded hover:bg-gray-100 ${editor?.isActive("strike") ? "bg-gray-200" : ""}`}
            onClick={() => editor?.chain().focus().toggleStrike().run()}
            title="Strike (Ctrl+Shift+X)"
          >
            <span className="sr-only">Strike</span>
            <span className="line-through">S</span>
          </button>
          <button
            className={`p-2 rounded hover:bg-gray-100 ${editor?.isActive("heading", { level: 1 }) ? "bg-gray-200" : ""}`}
            onClick={() => editor?.chain().focus().toggleHeading({ level: 1 }).run()}
            title="Heading 1 (Ctrl+Alt+1)"
          >
            <span className="sr-only">Heading 1</span>
            <span className="font-bold">H1</span>
          </button>
          <button
            className="p-2 rounded hover:bg-gray-100"
            onClick={handleImageUpload}
            title="Upload Image (Ctrl+Shift+I)"
          >
            <span className="sr-only">Upload Image</span>
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
              className="lucide lucide-image"
            >
              <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
              <circle cx="9" cy="9" r="2" />
              <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
            </svg>
          </button>
          <input type="file" ref={fileInputRef} onChange={onImageSelected} accept="image/*" className="hidden" />
        </div>
        <div className="flex items-center space-x-2">
          <div className="text-sm text-gray-500">
            {wordCount} {wordCount === 1 ? "word" : "words"}
          </div>
          <button className="p-2 rounded hover:bg-gray-100">
            <span className="sr-only">Info</span>
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
              className="lucide lucide-info"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M12 16v-4" />
              <path d="M12 8h.01" />
            </svg>
          </button>
          <button className="p-2 rounded hover:bg-gray-100">
            <span className="sr-only">More</span>
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
              className="lucide lucide-more-vertical"
            >
              <circle cx="12" cy="5" r="1" />
              <circle cx="12" cy="12" r="1" />
              <circle cx="12" cy="19" r="1" />
            </svg>
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 editor-container relative">
        {editor && (
          <EditorContent
            editor={editor}
            className="prose h-full editor-content"
            style={{ outline: "none", border: "none", boxShadow: "none" }}
          />
        )}
        {editor && <EditorToolbar editor={editor} containerRef={editorContainerRef} />}
      </div>

      {currentNote && (
        <div className="note-metadata">
          <div className="note-metadata-item">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="lucide lucide-calendar"
            >
              <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
              <line x1="16" x2="16" y1="2" y2="6" />
              <line x1="8" x2="8" y1="2" y2="6" />
              <line x1="3" x2="21" y1="10" y2="10" />
            </svg>
            <span>Last updated: {new Date(currentNote.updatedAt).toLocaleString()}</span>
          </div>
          <div className="note-metadata-item">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="lucide lucide-file-text"
            >
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" x2="8" y1="13" y2="13" />
              <line x1="16" x2="8" y1="17" y2="17" />
              <line x1="10" x2="8" y1="9" y2="9" />
            </svg>
            <span>
              {wordCount} {wordCount === 1 ? "word" : "words"}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
