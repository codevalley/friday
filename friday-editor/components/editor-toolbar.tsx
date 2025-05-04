"use client"

import type React from "react"

import { useEffect, useState } from "react"
import type { Editor } from "@tiptap/react"
import {
  Bold,
  Italic,
  List,
  ListOrdered,
  LinkIcon,
  ImageIcon,
  TableIcon,
  Code,
  CheckSquare,
  Heading1,
  Heading2,
  Heading3,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Highlighter,
  RotateCcw,
  RotateCw,
  Video,
  CodeSquare,
} from "lucide-react"

interface EditorToolbarProps {
  editor: Editor | null
  containerRef: React.RefObject<HTMLDivElement>
}

export function EditorToolbar({ editor, containerRef }: EditorToolbarProps) {
  const [toolbarStyle, setToolbarStyle] = useState({})
  const [showImageInput, setShowImageInput] = useState(false)
  const [imageUrl, setImageUrl] = useState("")
  const [showLinkInput, setShowLinkInput] = useState(false)
  const [linkUrl, setLinkUrl] = useState("")
  const [showVideoInput, setShowVideoInput] = useState(false)
  const [videoUrl, setVideoUrl] = useState("")

  useEffect(() => {
    // Function to update toolbar position
    const updateToolbarPosition = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect()
        setToolbarStyle({
          position: "fixed",
          bottom: "20px",
          left: rect.left + rect.width / 2,
          transform: "translateX(-50%)",
        })
      }
    }

    // Initial position
    updateToolbarPosition()

    // Update on resize
    window.addEventListener("resize", updateToolbarPosition)

    return () => {
      window.removeEventListener("resize", updateToolbarPosition)
    }
  }, [containerRef])

  // Update toolbar position based on selection
  useEffect(() => {
    if (!editor) return

    const updateToolbarPosition = () => {
      const { view } = editor
      if (!view || !containerRef.current) return

      const { from, to } = view.state.selection
      if (from === to) return // No selection

      const start = view.coordsAtPos(from)
      const end = view.coordsAtPos(to)
      const rect = containerRef.current.getBoundingClientRect()

      // Position toolbar above the selection
      setToolbarStyle({
        position: "fixed",
        bottom: window.innerHeight - start.top + 10,
        left: (start.left + end.left) / 2,
        transform: "translateX(-50%)",
      })
    }

    editor.on("selectionUpdate", updateToolbarPosition)

    return () => {
      editor.off("selectionUpdate", updateToolbarPosition)
    }
  }, [editor, containerRef])

  if (!editor) {
    return null
  }

  const addImage = () => {
    if (imageUrl) {
      editor.chain().focus().setImage({ src: imageUrl }).run()
      setImageUrl("")
      setShowImageInput(false)
    }
  }

  const setLink = () => {
    if (linkUrl) {
      editor.chain().focus().extendMarkRange("link").setLink({ href: linkUrl }).run()
      setLinkUrl("")
      setShowLinkInput(false)
    } else {
      editor.chain().focus().extendMarkRange("link").unsetLink().run()
      setShowLinkInput(false)
    }
  }

  const addVideo = () => {
    if (videoUrl) {
      // Extract YouTube video ID
      const youtubeRegex =
        /(?:youtube\.com\/(?:[^/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/
      const match = videoUrl.match(youtubeRegex)

      if (match && match[1]) {
        const videoId = match[1]
        const embedHtml = `<div class="embed-container"><iframe width="560" height="315" src="https://www.youtube.com/embed/${videoId}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>`
        editor.chain().focus().insertContent(embedHtml).run()
      } else {
        // If not YouTube, just insert as a link
        editor.chain().focus().extendMarkRange("link").setLink({ href: videoUrl }).run()
      }

      setVideoUrl("")
      setShowVideoInput(false)
    }
  }

  const addTableControls = () => {
    if (editor.isActive("table")) {
      return (
        <div className="tableControls">
          <button onClick={() => editor.chain().focus().addColumnBefore().run()}>Add Column Before</button>
          <button onClick={() => editor.chain().focus().addColumnAfter().run()}>Add Column After</button>
          <button onClick={() => editor.chain().focus().deleteColumn().run()}>Delete Column</button>
          <button onClick={() => editor.chain().focus().addRowBefore().run()}>Add Row Before</button>
          <button onClick={() => editor.chain().focus().addRowAfter().run()}>Add Row After</button>
          <button onClick={() => editor.chain().focus().deleteRow().run()}>Delete Row</button>
          <button onClick={() => editor.chain().focus().deleteTable().run()}>Delete Table</button>
        </div>
      )
    }
    return null
  }

  return (
    <div className="floating-toolbar" style={toolbarStyle}>
      <div className="toolbar-group">
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          className={`toolbar-btn ${editor.isActive("heading", { level: 1 }) ? "active" : ""}`}
        >
          <Heading1 className="h-4 w-4" />
          <span className="tooltip">Heading 1 (Ctrl+Alt+1)</span>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={`toolbar-btn ${editor.isActive("heading", { level: 2 }) ? "active" : ""}`}
        >
          <Heading2 className="h-4 w-4" />
          <span className="tooltip">Heading 2 (Ctrl+Alt+2)</span>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          className={`toolbar-btn ${editor.isActive("heading", { level: 3 }) ? "active" : ""}`}
        >
          <Heading3 className="h-4 w-4" />
          <span className="tooltip">Heading 3 (Ctrl+Alt+3)</span>
        </button>
      </div>

      <div className="toolbar-divider"></div>

      <div className="toolbar-group">
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={`toolbar-btn ${editor.isActive("bold") ? "active" : ""}`}
        >
          <Bold className="h-4 w-4" />
          <span className="tooltip">Bold (Ctrl+B)</span>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={`toolbar-btn ${editor.isActive("italic") ? "active" : ""}`}
        >
          <Italic className="h-4 w-4" />
          <span className="tooltip">Italic (Ctrl+I)</span>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHighlight().run()}
          className={`toolbar-btn ${editor.isActive("highlight") ? "active" : ""}`}
        >
          <Highlighter className="h-4 w-4" />
          <span className="tooltip">Highlight</span>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleCode().run()}
          className={`toolbar-btn ${editor.isActive("code") ? "active" : ""}`}
        >
          <Code className="h-4 w-4" />
          <span className="tooltip">Inline Code</span>
        </button>
      </div>

      <div className="toolbar-divider"></div>

      <div className="toolbar-group">
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={`toolbar-btn ${editor.isActive("bulletList") ? "active" : ""}`}
        >
          <List className="h-4 w-4" />
          <span className="tooltip">Bullet List (Ctrl+Shift+8)</span>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={`toolbar-btn ${editor.isActive("orderedList") ? "active" : ""}`}
        >
          <ListOrdered className="h-4 w-4" />
          <span className="tooltip">Ordered List (Ctrl+Shift+9)</span>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleTaskList().run()}
          className={`toolbar-btn ${editor.isActive("taskList") ? "active" : ""}`}
        >
          <CheckSquare className="h-4 w-4" />
          <span className="tooltip">Task List (Ctrl+Shift+0)</span>
        </button>
      </div>

      <div className="toolbar-divider"></div>

      <div className="toolbar-group">
        {showLinkInput ? (
          <div className="toolbar-input-container">
            <input
              type="text"
              value={linkUrl}
              onChange={(e) => setLinkUrl(e.target.value)}
              placeholder="Enter URL"
              className="toolbar-input"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  setLink()
                }
              }}
            />
            <button onClick={setLink} className="toolbar-input-btn">
              Add
            </button>
            <button onClick={() => setShowLinkInput(false)} className="toolbar-input-btn">
              Cancel
            </button>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => {
              const previousUrl = editor.getAttributes("link").href
              setLinkUrl(previousUrl || "")
              setShowLinkInput(true)
            }}
            className={`toolbar-btn ${editor.isActive("link") ? "active" : ""}`}
          >
            <LinkIcon className="h-4 w-4" />
            <span className="tooltip">Add Link (Ctrl+K)</span>
          </button>
        )}

        {showImageInput ? (
          <div className="toolbar-input-container">
            <input
              type="text"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              placeholder="Enter image URL"
              className="toolbar-input"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  addImage()
                }
              }}
            />
            <button onClick={addImage} className="toolbar-input-btn">
              Add
            </button>
            <button onClick={() => setShowImageInput(false)} className="toolbar-input-btn">
              Cancel
            </button>
          </div>
        ) : (
          <button type="button" onClick={() => setShowImageInput(true)} className="toolbar-btn">
            <ImageIcon className="h-4 w-4" />
            <span className="tooltip">Add Image</span>
          </button>
        )}

        <button
          type="button"
          onClick={() => {
            editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
          }}
          className="toolbar-btn"
        >
          <TableIcon className="h-4 w-4" />
          <span className="tooltip">Insert Table</span>
        </button>

        {showVideoInput ? (
          <div className="toolbar-input-container">
            <input
              type="text"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              placeholder="Enter YouTube URL"
              className="toolbar-input"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  addVideo()
                }
              }}
            />
            <button onClick={addVideo} className="toolbar-input-btn">
              Add
            </button>
            <button onClick={() => setShowVideoInput(false)} className="toolbar-input-btn">
              Cancel
            </button>
          </div>
        ) : (
          <button type="button" onClick={() => setShowVideoInput(true)} className="toolbar-btn">
            <Video className="h-4 w-4" />
            <span className="tooltip">Embed Video</span>
          </button>
        )}

        <button
          type="button"
          onClick={() => editor.chain().focus().toggleCodeBlock().run()}
          className={`toolbar-btn ${editor.isActive("codeBlock") ? "active" : ""}`}
        >
          <CodeSquare className="h-4 w-4" />
          <span className="tooltip">Code Block (Ctrl+Alt+C)</span>
        </button>
      </div>

      <div className="toolbar-divider"></div>

      <div className="toolbar-group">
        <button
          type="button"
          onClick={() => editor.chain().focus().setTextAlign("left").run()}
          className={`toolbar-btn ${editor.isActive({ textAlign: "left" }) ? "active" : ""}`}
        >
          <AlignLeft className="h-4 w-4" />
          <span className="tooltip">Align Left (Ctrl+Shift+L)</span>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().setTextAlign("center").run()}
          className={`toolbar-btn ${editor.isActive({ textAlign: "center" }) ? "active" : ""}`}
        >
          <AlignCenter className="h-4 w-4" />
          <span className="tooltip">Align Center (Ctrl+Shift+E)</span>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().setTextAlign("right").run()}
          className={`toolbar-btn ${editor.isActive({ textAlign: "right" }) ? "active" : ""}`}
        >
          <AlignRight className="h-4 w-4" />
          <span className="tooltip">Align Right (Ctrl+Shift+R)</span>
        </button>
      </div>

      <div className="toolbar-divider"></div>

      <div className="toolbar-group">
        <button
          type="button"
          onClick={() => editor.chain().focus().undo().run()}
          className="toolbar-btn"
          disabled={!editor.can().undo()}
        >
          <RotateCcw className="h-4 w-4" />
          <span className="tooltip">Undo (Ctrl+Z)</span>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().redo().run()}
          className="toolbar-btn"
          disabled={!editor.can().redo()}
        >
          <RotateCw className="h-4 w-4" />
          <span className="tooltip">Redo (Ctrl+Shift+Z)</span>
        </button>
      </div>

      {editor.isActive("table") && addTableControls()}
    </div>
  )
}
