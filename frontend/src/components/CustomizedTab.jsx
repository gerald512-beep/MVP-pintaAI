import React, { useRef } from 'react'
import { t } from '../i18n/translations'

export const AGE_CONFIG = {
  '5': {
    regions: '9 to 15 large enclosed shapes',
    thickness: '1.5 to 2.5 pts — similar to thick marker strokes',
    lineStyle: 'Most lines rounded, simple angles allowed',
    background: 'Simple background and floor based on the uploaded photo',
  },
  '6': {
    regions: '16 or more enclosed shapes',
    thickness: '1 to 1.5 pts — similar to fine marker or colored pencil strokes',
    lineStyle: 'Mix of rounded and angular lines',
    background: 'Multiple background elements and floor based on the uploaded photo',
  },
}

const CONFIG_OPTIONS = {
  regions: [
    { label: '6–9 regions (4 yrs or less)',  value: '6 to 9 large enclosed shapes' },
    { label: '9–15 regions (5 yrs)',          value: '9 to 15 large enclosed shapes' },
    { label: '16+ regions (6 yrs)',           value: '16 or more enclosed shapes' },
  ],
  thickness: [
    { label: '3–4 pts — jumbo crayons (3 yrs)',             value: '3 to 4 pts — similar to jumbo crayons' },
    { label: '2.5–3 pts — regular crayons (4 yrs)',         value: '2.5 to 3 pts — similar to regular crayons' },
    { label: '1.5–2.5 pts — thick markers (5 yrs)',         value: '1.5 to 2.5 pts — similar to thick marker strokes' },
    { label: '1–1.5 pts — markers / colored pencils (6 yrs)', value: '1 to 1.5 pts — similar to fine marker or colored pencil strokes' },
  ],
  lineStyle: [
    { label: 'Rounded corners, no sharp angles (4 yrs or less)', value: 'All lines rounded corners, no sharp angles' },
    { label: 'Most rounded, simple angles (5 yrs)',               value: 'Most lines rounded, simple angles allowed' },
    { label: 'Mix of rounded and angular (6 yrs)',                value: 'Mix of rounded and angular lines' },
  ],
  background: [
    { label: 'No background (4 yrs or less)',                         value: 'No background' },
    { label: 'Simple background and floor from photo (5 yrs)',        value: 'Simple background and floor based on the uploaded photo' },
    { label: 'Multiple background elements and floor from photo (6 yrs)', value: 'Multiple background elements and floor based on the uploaded photo' },
  ],
}

export default function CustomizedTab({
  age, setAge,
  topic, setTopic,
  imageFile, setImageFile,
  imagePreviewUrl, setImagePreviewUrl,
  customConfig, setCustomConfig,
}) {
  const fileInputRef = useRef(null)

  function handleAgeSelect(selectedAge) {
    console.log('[PintaAI] Age selected:', selectedAge)
    setAge(selectedAge)
    // Reset config fields to defaults for the new age
    const cfg = AGE_CONFIG[selectedAge]
    setCustomConfig({
      regions: cfg.regions,
      thickness: cfg.thickness,
      lineStyle: cfg.lineStyle,
      background: cfg.background,
    })
  }

  function handleTopicSelect(selectedTopic) {
    console.log('[PintaAI] Topic selected:', selectedTopic)
    setTopic(selectedTopic)
  }

  function handleUploadClick() {
    console.log('[PintaAI] Upload photo clicked')
    fileInputRef.current?.click()
  }

  function handleFileChange(e) {
    const file = e.target.files?.[0]
    if (!file) return
    console.log('[PintaAI] Photo selected:', file.name, file.size, 'bytes')
    setImageFile(file)
    setImagePreviewUrl(URL.createObjectURL(file))
    e.target.value = ''
  }

  function handleConfigChange(field, value) {
    setCustomConfig((prev) => ({ ...prev, [field]: value }))
  }

  const configFields = [
    { key: 'regions',   label: t.autoConfigRegions },
    { key: 'thickness', label: t.autoConfigThickness },
    { key: 'lineStyle', label: t.autoConfigLineStyle },
    { key: 'background',label: t.autoConfigBackground },
  ]

  return (
    <div className="space-y-6">
      {/* Age */}
      <div>
        <p className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">{t.sectionAge}</p>
        <div className="flex gap-2">
          {['5', '6'].map((a) => (
            <button
              key={a}
              onClick={() => handleAgeSelect(a)}
              className={`px-4 py-2 rounded-full border text-sm font-medium transition-colors ${
                age === a
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
              }`}
            >
              {a === '5' ? t.age5 : t.age6}
            </button>
          ))}
        </div>
      </div>

      {/* Topic */}
      <div>
        <div className="flex items-baseline gap-2 mb-2">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">{t.sectionTopic}</p>
          <span className="text-xs text-gray-400 italic">{t.topicOnlyAnimal}</span>
        </div>
        <div className="flex gap-2">
          {/* Animal */}
          <button
            onClick={() => handleTopicSelect('animal')}
            className={`px-4 py-2 rounded-full border text-sm font-medium transition-colors ${
              topic === 'animal'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
            }`}
          >
            {t.topicAnimal}
          </button>

          {/* Myself — disabled */}
          <div className="relative group">
            <button
              disabled
              className="px-4 py-2 rounded-full border border-gray-200 bg-gray-100 text-gray-400 text-sm font-medium cursor-not-allowed"
            >
              {t.topicMyself}
            </button>
            <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 rounded bg-gray-800 text-white text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
              {t.comingSoon}
            </span>
          </div>
        </div>

        {/* File upload — only shown after topic is selected */}
        {topic === 'animal' && (
          <div className="mt-3">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileChange}
            />
            {imageFile ? (
              <div className="flex items-center gap-3">
                <img
                  src={imagePreviewUrl}
                  alt="Selected"
                  className="w-14 h-14 rounded object-cover border border-gray-200"
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700 truncate">{imageFile.name}</p>
                  <button
                    onClick={handleUploadClick}
                    className="text-xs text-blue-600 hover:underline mt-0.5"
                  >
                    {t.changePhoto}
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={handleUploadClick}
                className="px-4 py-2 rounded-lg border border-dashed border-gray-300 text-sm text-gray-600 hover:border-blue-400 hover:text-blue-600 transition-colors w-full"
              >
                {t.uploadPhoto}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Config dropdowns — shown once age is selected */}
      {age && (
        <div className="space-y-2">
          {configFields.map(({ key, label }) => (
            <div key={key} className="flex flex-col gap-1">
              <label className="text-xs font-bold text-gray-700">{label}</label>
              <select
                value={customConfig[key] || ''}
                onChange={(e) => handleConfigChange(key, e.target.value)}
                className="text-xs text-gray-700 border border-gray-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
              >
                {CONFIG_OPTIONS[key].map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
