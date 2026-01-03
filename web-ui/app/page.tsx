'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

interface PoisonResult {
  success: boolean;
  poisonedImage: string;
  signatureId: string;
  signature: any;
  error?: string;
}

interface BatchResult {
  original_name: string;
  poisoned_image: string;
  signature_id: string;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PoisonResult | null>(null);
  const [batchResults, setBatchResults] = useState<BatchResult[]>([]);
  const [epsilon, setEpsilon] = useState(0.01);
  const [pgdSteps, setPgdSteps] = useState(1);
  const [mode, setMode] = useState<'single' | 'batch' | 'video'>('single');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (mode === 'batch') {
      setFiles(acceptedFiles);
      setBatchResults([]);
      setResult(null);
    } else if (mode === 'video') {
      const file = acceptedFiles[0];
      setFile(file);
      setResult(null);
      const reader = new FileReader();
      reader.onload = () => setPreview(reader.result as string);
      reader.readAsDataURL(file);
    } else {
      const file = acceptedFiles[0];
      if (file) {
        setFile(file);
        setResult(null);
        setBatchResults([]);

        // Create preview
        const reader = new FileReader();
        reader.onload = () => {
          setPreview(reader.result as string);
        };
        reader.readAsDataURL(file);
      }
    }
  }, [mode]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: mode === 'video'
      ? { 'video/*': ['.mp4', '.avi', '.mov'] }
      : { 'image/*': ['.png', '.jpg', '.jpeg'] },
    maxFiles: mode === 'batch' ? 10 : 1,
    multiple: mode === 'batch'
  });

  const poisonImage = async () => {
    if (!file && files.length === 0) return;

    setLoading(true);
    setResult(null);
    setBatchResults([]);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

    try {
      if (mode === 'batch') {
        // Batch processing
        const formData = new FormData();
        files.forEach((file) => {
          formData.append('images', file);
        });
        formData.append('epsilon', epsilon.toString());
        formData.append('pgd_steps', pgdSteps.toString());

        const response = await axios.post(`${apiUrl}/api/batch`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        setBatchResults(response.data.results);
      } else {
        // Single image or video
        const formData = new FormData();
        formData.append('image', file!);
        formData.append('epsilon', epsilon.toString());
        formData.append('pgd_steps', pgdSteps.toString());

        const response = await axios.post(`${apiUrl}/api/poison`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        setResult(response.data);
      }
    } catch (error: any) {
      setResult({
        success: false,
        poisonedImage: '',
        signatureId: '',
        signature: null,
        error: error.response?.data?.error || 'Failed to poison. Make sure API server is running on port 5000'
      });
    } finally {
      setLoading(false);
    }
  };

  const downloadPoisonedImage = () => {
    if (!result?.poisonedImage) return;

    const link = document.createElement('a');
    link.href = result.poisonedImage;
    link.download = `poisoned_${file?.name || 'image.jpg'}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const downloadSignature = () => {
    if (!result?.signature) return;

    const blob = new Blob([JSON.stringify(result.signature, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `signature_${result.signatureId}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-green-900 to-gray-900">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-sm border-b border-green-500/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-4xl font-bold text-green-400">
            ✨ Sigil: Dual-Layer Defense
          </h1>
          <p className="mt-2 text-gray-300">
            <strong>Scrapers can't win.</strong> HD → Model breaks. SD → We track you.
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Mode Selector */}
        <div className="mb-8 bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-green-500/20">
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => setMode('single')}
              className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
                mode === 'single'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Single Image
            </button>
            <button
              onClick={() => setMode('batch')}
              className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
                mode === 'batch'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Batch Images
            </button>
            <button
              onClick={() => setMode('video')}
              className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
                mode === 'video'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Video (Phase 2)
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Panel - Upload */}
          <div className="space-y-6">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-green-500/20">
              <h2 className="text-2xl font-semibold text-green-400 mb-4">
                1. Upload Your {mode === 'video' ? 'Video' : mode === 'batch' ? 'Images' : 'Image'}
              </h2>

              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-green-400 bg-green-400/10'
                    : 'border-gray-600 hover:border-green-500'
                }`}
              >
                <input {...getInputProps()} />
                {mode === 'batch' && files.length > 0 ? (
                  <div className="space-y-4">
                    <p className="text-green-400 font-semibold">{files.length} files selected</p>
                    <div className="max-h-40 overflow-y-auto">
                      {files.map((f, i) => (
                        <p key={i} className="text-sm text-gray-400">{f.name}</p>
                      ))}
                    </div>
                  </div>
                ) : preview ? (
                  <div className="space-y-4">
                    {mode === 'video' ? (
                      <video
                        src={preview}
                        controls
                        className="max-h-64 mx-auto rounded-lg"
                      />
                    ) : (
                      <img
                        src={preview}
                        alt="Preview"
                        className="max-h-64 mx-auto rounded-lg"
                      />
                    )}
                    <p className="text-sm text-gray-400">{file?.name}</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-lg text-gray-300 mb-2">
                      {isDragActive
                        ? `Drop your ${mode === 'video' ? 'video' : mode === 'batch' ? 'images' : 'image'} here...`
                        : `Drag & drop ${mode === 'video' ? 'a video' : mode === 'batch' ? 'images' : 'an image'} here`}
                    </p>
                    <p className="text-sm text-gray-500">
                      or click to select {mode === 'video' ? '(MP4, AVI, MOV)' : '(JPG, PNG)'}
                      {mode === 'batch' && ' - up to 10 files'}
                    </p>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-green-500/20">
              <h2 className="text-2xl font-semibold text-green-400 mb-4">
                2. Configure Settings
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Perturbation Strength (Epsilon)
                  </label>
                  <input
                    type="range"
                    min="0.005"
                    max="0.05"
                    step="0.005"
                    value={epsilon}
                    onChange={(e) => setEpsilon(parseFloat(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Subtle (0.005)</span>
                    <span className="text-green-400 font-medium">{epsilon.toFixed(3)}</span>
                    <span>Strong (0.05)</span>
                  </div>
                  <p className="text-xs text-gray-400 mt-2">
                    Higher values = stronger protection but more visible. Recommended: 0.01
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    PGD Steps (Robustness)
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    step="1"
                    value={pgdSteps}
                    onChange={(e) => setPgdSteps(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Fast (1 - FGSM)</span>
                    <span className="text-green-400 font-medium">{pgdSteps} steps</span>
                    <span>Robust (10 - PGD)</span>
                  </div>
                  <p className="text-xs text-gray-400 mt-2">
                    More steps = more robust but slower. 1 step = FGSM (fast), 5-10 steps = PGD (robust)
                  </p>
                </div>

                <button
                  onClick={poisonImage}
                  disabled={(mode === 'batch' ? files.length === 0 : !file) || loading}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors"
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Poisoning {mode === 'video' ? 'Video' : mode === 'batch' ? 'Images' : 'Image'}...
                    </span>
                  ) : (
                    `✨ Poison ${mode === 'video' ? 'Video' : mode === 'batch' ? 'Images' : 'Image'}`
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Right Panel - Results */}
          <div className="space-y-6">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-green-500/20">
              <h2 className="text-2xl font-semibold text-green-400 mb-4">
                3. Download Protected Image
              </h2>

              {!result && batchResults.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  Upload and poison {mode === 'video' ? 'a video' : mode === 'batch' ? 'images' : 'an image'} to see results
                </div>
              )}

              {result?.error && (
                <div className="bg-red-900/30 border border-red-500 rounded-lg p-4 text-red-300">
                  <p className="font-semibold">Error:</p>
                  <p className="text-sm">{result.error}</p>
                </div>
              )}

              {/* Batch Results */}
              {batchResults.length > 0 && (
                <div className="space-y-4">
                  <div className="bg-green-900/30 border border-green-500 rounded-lg p-4 text-green-300">
                    <p className="font-semibold flex items-center">
                      <span className="mr-2">✅</span>
                      {batchResults.length} Images Successfully Poisoned!
                    </p>
                  </div>

                  <div className="max-h-96 overflow-y-auto space-y-3">
                    {batchResults.map((item, idx) => (
                      <div key={idx} className="bg-gray-700/50 rounded-lg p-3 border border-gray-600">
                        <p className="text-sm font-semibold text-gray-300 mb-2">{item.original_name}</p>
                        <img
                          src={item.poisoned_image}
                          alt={`Poisoned ${idx}`}
                          className="w-full rounded mb-2"
                        />
                        <p className="text-xs text-gray-400">
                          Signature: <code className="bg-black/30 px-1 rounded">{item.signature_id}</code>
                        </p>
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={() => {
                      batchResults.forEach((item, idx) => {
                        const link = document.createElement('a');
                        link.href = item.poisoned_image;
                        link.download = `poisoned_${item.original_name}`;
                        link.click();
                      });
                    }}
                    className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors"
                  >
                    Download All Images
                  </button>
                </div>
              )}

              {result?.success && (
                <div className="space-y-4">
                  <div className="bg-green-900/30 border border-green-500 rounded-lg p-4 text-green-300">
                    <p className="font-semibold flex items-center">
                      <span className="mr-2">✅</span>
                      Image Successfully Poisoned!
                    </p>
                    <p className="text-sm mt-1">
                      Signature ID: <code className="bg-black/30 px-2 py-1 rounded">{result.signatureId}</code>
                    </p>
                  </div>

                  {result.poisonedImage && (
                    <div>
                      <p className="text-sm text-gray-400 mb-2">Preview (poisoned):</p>
                      <img
                        src={result.poisonedImage}
                        alt="Poisoned"
                        className="w-full rounded-lg border border-gray-700"
                      />
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    <button
                      onClick={downloadPoisonedImage}
                      className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors"
                    >
                      Download Image
                    </button>
                    <button
                      onClick={downloadSignature}
                      className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors"
                    >
                      Download Signature
                    </button>
                  </div>

                  <div className="bg-yellow-900/30 border border-yellow-500/50 rounded-lg p-4 text-yellow-300 text-sm">
                    <p className="font-semibold">⚠️ Important:</p>
                    <ul className="list-disc list-inside mt-2 space-y-1">
                      <li>Keep the signature file safe - you need it to prove ownership</li>
                      <li>The poisoned image looks identical but contains your unique signature</li>
                      <li>If AI trains on this image, you can detect it in the trained model</li>
                    </ul>
                  </div>
                </div>
              )}
            </div>

            {/* Info Panel */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-green-500/20">
              <h3 className="text-lg font-semibold text-green-400 mb-3">
                Dual-Layer Defense
              </h3>
              <div className="space-y-4 text-sm text-gray-300">
                <div>
                  <p className="font-semibold text-red-400 mb-2">🔴 Layer 1: Active Poison (HD Content)</p>
                  <ul className="space-y-1 ml-4">
                    <li>• Radioactive signature poisons AI models</li>
                    <li>• Model outputs reveal theft (Z-score: 5.8)</li>
                    <li>• Works on Vimeo Pro, YouTube HD, Archives</li>
                  </ul>
                </div>
                <div>
                  <p className="font-semibold text-blue-400 mb-2">🔵 Layer 2: Passive Tracking (Compressed)</p>
                  <ul className="space-y-1 ml-4">
                    <li>• Perceptual hash survives compression (0-14 bit drift)</li>
                    <li>• Tracks usage across YouTube, TikTok, Facebook</li>
                    <li>• Creates forensic evidence for legal action</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Info */}
        <div className="mt-12 text-center text-gray-500 text-sm">
          <p>First compression-robust video marking system • Built on ICML 2020 research</p>
          <p className="mt-1">Open source • MIT License • Production ready</p>
          <p className="mt-1 text-xs">
            🔴 Active: CRF 18-23 (detection 0.50-0.60) • 🔵 Passive: CRF 28+ (hash drift 0-14 bits)
          </p>
        </div>
      </main>
    </div>
  );
}
