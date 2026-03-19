import React, { useState } from 'react'
import ControlsPanel from './components/ControlsPanel'
import PreviewPanel from './components/PreviewPanel'
import PromptPreviewModal from './components/PromptPreviewModal'

const EMPTY_CONFIG = { regions: '', thickness: '', lineStyle: '', background: '' }

export default function App() {
  const [age, setAge] = useState(null)
  const [topic, setTopic] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  const [imagePreviewUrl, setImagePreviewUrl] = useState(null)
  const [customConfig, setCustomConfig] = useState(EMPTY_CONFIG)
  const [generatedImage, setGeneratedImage] = useState(null)
  const [promptUsed, setPromptUsed] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [showPromptModal, setShowPromptModal] = useState(false)
  const [assembledPrompt, setAssembledPrompt] = useState('')
  const [generationCount, setGenerationCount] = useState(0)

  async function onGenerate() {
    const params = new URLSearchParams({
      age,
      regions: customConfig.regions,
      thickness: customConfig.thickness,
      line_style: customConfig.lineStyle,
      background: customConfig.background,
    })
    console.log('[PintaAI] Fetching prompt preview from backend')
    try {
      const res = await fetch(`/api/prompt-preview?${params}`)
      const data = await res.json()
      setAssembledPrompt(data.prompt)
      setShowPromptModal(true)
    } catch (err) {
      console.error('[PintaAI] Failed to fetch prompt preview:', err)
      alert('Could not load prompt preview. Is the backend running?')
    }
  }

  async function onConfirmGenerate() {
    setShowPromptModal(false)
    setIsLoading(true)
    console.log('[PintaAI] Calling /api/generate — age:', age, 'topic:', topic, 'file:', imageFile?.name)

    const formData = new FormData()
    formData.append('age', age)
    formData.append('topic', topic)
    formData.append('image', imageFile)
    formData.append('regions', customConfig.regions)
    formData.append('thickness', customConfig.thickness)
    formData.append('line_style', customConfig.lineStyle)
    formData.append('background', customConfig.background)

    try {
      const res = await fetch('/api/generate', { method: 'POST', body: formData })
      if (!res.ok) {
        const err = await res.text()
        throw new Error(`Server error ${res.status}: ${err}`)
      }
      const data = await res.json()
      console.log('[PintaAI] Response received — keys:', Object.keys(data))
      setGeneratedImage(data.image_b64 || null)
      setPromptUsed(data.prompt_used)
      setGenerationCount((c) => c + 1)
    } catch (err) {
      console.error('[PintaAI] Generation failed:', err)
      alert(`Generation failed: ${err.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  function onRegenerate() {
    if (generationCount >= 2) return
    console.log('[PintaAI] Regenerate requested')
    onGenerate()
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <ControlsPanel
        age={age}
        setAge={setAge}
        topic={topic}
        setTopic={setTopic}
        imageFile={imageFile}
        setImageFile={setImageFile}
        imagePreviewUrl={imagePreviewUrl}
        setImagePreviewUrl={setImagePreviewUrl}
        customConfig={customConfig}
        setCustomConfig={setCustomConfig}
        onGenerate={onGenerate}
        isLoading={isLoading}
      />

      <PreviewPanel
        generatedImage={generatedImage}
        isLoading={isLoading}
        generationCount={generationCount}
        onRegenerate={onRegenerate}
      />

      {showPromptModal && (
        <PromptPreviewModal
          prompt={assembledPrompt}
          onCancel={() => {
            console.log('[PintaAI] Prompt modal cancelled')
            setShowPromptModal(false)
          }}
          onConfirm={onConfirmGenerate}
        />
      )}
    </div>
  )
}
