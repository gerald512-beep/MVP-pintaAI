import React, { useRef } from 'react'
import { t } from '../i18n/translations'

export default function PreviewPanel({ generatedImage, isLoading, generationCount, onRegenerate }) {
  const canRegenerate = generationCount < 2

  function handleDownload() {
    if (!generatedImage) return
    const a = document.createElement('a')
    a.href = `data:image/png;base64,${generatedImage}`
    a.download = 'coloring-page.png'
    a.click()
    console.log('[PintaAI] Download triggered')
  }

  function handlePrint() {
    console.log('[PintaAI] Print triggered')
    window.print()
  }

  function handleRegenerate() {
    if (!canRegenerate) return
    console.log('[PintaAI] Regenerate triggered (generation count was', generationCount, ')')
    onRegenerate()
  }

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 bg-gray-50 gap-6">
      {/* Image area */}
      <div className="w-full max-w-[512px] aspect-square bg-white rounded-xl border-2 border-dashed border-gray-200 flex items-center justify-center overflow-hidden shadow-sm print:border-0 print:shadow-none">
        {isLoading ? (
          <div className="flex flex-col items-center gap-3 text-gray-400">
            <svg className="animate-spin h-10 w-10" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            <span className="text-sm">{t.generating}</span>
          </div>
        ) : generatedImage ? (
          <img
            src={`data:image/png;base64,${generatedImage}`}
            alt="Generated coloring page"
            className="w-full h-full object-contain"
          />
        ) : (
          <p className="text-sm text-gray-400 text-center px-8">{t.previewPlaceholder}</p>
        )}
      </div>

      {/* Action buttons — only shown when an image exists */}
      {generatedImage && !isLoading && (
        <div className="flex items-center gap-3 print:hidden">
          <button
            onClick={handlePrint}
            className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            {t.print}
          </button>
          <button
            onClick={handleDownload}
            className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            {t.download}
          </button>
          <button
            onClick={handleRegenerate}
            disabled={!canRegenerate}
            title={!canRegenerate ? 'Regeneration limit reached' : undefined}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors border ${
              canRegenerate
                ? 'border-blue-500 text-blue-600 hover:bg-blue-50'
                : 'border-gray-200 text-gray-400 cursor-not-allowed bg-gray-100'
            }`}
          >
            {t.regenerate}
          </button>
        </div>
      )}
    </div>
  )
}
