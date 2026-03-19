import React, { useEffect } from 'react'
import { t } from '../i18n/translations'

export default function PromptPreviewModal({ prompt, onCancel, onConfirm }) {
  useEffect(() => {
    console.log('[PintaAI] Prompt modal opened')
  }, [])

  function handleConfirm() {
    console.log('[PintaAI] Prompt confirmed, calling API')
    onConfirm()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4 flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-base font-semibold text-gray-900">{t.modalTitle}</h2>
        </div>

        {/* Prompt text */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          <pre className="font-mono text-xs text-gray-700 whitespace-pre-wrap leading-relaxed">
            {prompt}
          </pre>
        </div>

        {/* Actions */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            {t.modalCancel}
          </button>
          <button
            onClick={handleConfirm}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
          >
            {t.modalConfirm}
          </button>
        </div>
      </div>
    </div>
  )
}
