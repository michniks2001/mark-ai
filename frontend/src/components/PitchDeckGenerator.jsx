import { useState, useEffect } from 'react';
import { getTargetAudiences, generatePitchDeck, getPitchDeckDownloadUrl } from '../lib/api';

const PitchDeckGenerator = () => {
  const [audiences, setAudiences] = useState([]);
  const [formData, setFormData] = useState({
    repository_url: '',
    audience_key: '',
    branch: '',
    format: 'pptx'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Fetch available target audiences on mount
  useEffect(() => {
    getTargetAudiences()
      .then(data => setAudiences(data.audiences || []))
      .catch(err => {
        console.error('Failed to fetch audiences:', err);
        setError('Failed to load target audiences. Please ensure the backend is running.');
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await generatePitchDeck({
        repository_url: formData.repository_url,
        audience_key: formData.audience_key,
        branch: formData.branch || null,
        format: formData.format
      });
      
      if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(err.message || 'Failed to generate pitch deck. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (result?.download_url) {
      // Extract filename from download_url
      const filename = result.download_url.split('/').pop();
      const downloadUrl = getPitchDeckDownloadUrl(filename);
      window.open(downloadUrl, '_blank');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            MarkAI
          </h1>
          <p className="text-lg text-gray-600">
            Generate professional pitch decks from any GitHub repository using your AI marketing assistant!
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-lg shadow-xl p-8 mb-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Repository URL */}
            <div>
              <label htmlFor="repository_url" className="block text-sm font-medium text-gray-700 mb-2">
                GitHub Repository URL
              </label>
              <input
                type="url"
                id="repository_url"
                required
                value={formData.repository_url}
                onChange={(e) => setFormData({ ...formData, repository_url: e.target.value })}
                placeholder="https://github.com/username/repo"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              />
            </div>

            {/* Target Audience */}
            <div>
              <label htmlFor="audience_key" className="block text-sm font-medium text-gray-700 mb-2">
                Target Audience
              </label>
              <select
                id="audience_key"
                required
                value={formData.audience_key}
                onChange={(e) => setFormData({ ...formData, audience_key: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              >
                <option value="">Select an audience...</option>
                {audiences.map((audience) => (
                  <option key={audience.key} value={audience.key}>
                    {audience.label}
                  </option>
                ))}
              </select>
              {formData.audience_key && audiences.find(a => a.key === formData.audience_key) && (
                <p className="mt-2 text-sm text-gray-600">
                  <span className="font-medium">Focus:</span>{' '}
                  {audiences.find(a => a.key === formData.audience_key).focus}
                </p>
              )}
            </div>

            {/* Branch (Optional) */}
            <div>
              <label htmlFor="branch" className="block text-sm font-medium text-gray-700 mb-2">
                Branch (optional)
              </label>
              <input
                type="text"
                id="branch"
                value={formData.branch}
                onChange={(e) => setFormData({ ...formData, branch: e.target.value })}
                placeholder="main"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              />
            </div>

            {/* Format Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Output Format
              </label>
              <div className="flex gap-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="format"
                    value="pptx"
                    checked={formData.format === 'pptx'}
                    onChange={(e) => setFormData({ ...formData, format: e.target.value })}
                    className="mr-2"
                  />
                  <span className="text-sm">PowerPoint (.pptx)</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="format"
                    value="script"
                    checked={formData.format === 'script'}
                    onChange={(e) => setFormData({ ...formData, format: e.target.value })}
                    className="mr-2"
                  />
                  <span className="text-sm">Presenter Script</span>
                </label>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating...
                </span>
              ) : (
                'Generate Pitch Deck'
              )}
            </button>
          </form>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        {/* Result Display */}
        {result && (
          <div className="bg-white rounded-lg shadow-xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              {result.format === 'pptx' ? 'PowerPoint Generated!' : 'Presenter Script'}
            </h2>

            {result.format === 'pptx' && (
              <div className="mb-6">
                <button
                  onClick={handleDownload}
                  className="bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition inline-flex items-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download PowerPoint
                </button>
              </div>
            )}

            {result.format === 'script' && result.content && (
              <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap bg-gray-50 p-6 rounded-lg text-sm overflow-x-auto">
                  {result.content}
                </pre>
              </div>
            )}

            {/* Pitch Data Preview */}
            {result.pitch_data && (
              <div className="mt-8 border-t pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Pitch Deck Structure</h3>
                <div className="space-y-4">
                  <div className="bg-indigo-50 p-4 rounded-lg">
                    <h4 className="font-medium text-indigo-900">{result.pitch_data.title}</h4>
                  </div>
                  {result.pitch_data.slides?.map((slide, idx) => (
                    <div key={idx} className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-medium text-gray-900 mb-2">
                        Slide {idx + 1}: {slide.title}
                      </h5>
                      <p className="text-sm text-gray-600 mb-2">{slide.content}</p>
                      {slide.speaker_notes && (
                        <details className="text-xs text-gray-500">
                          <summary className="cursor-pointer font-medium">Speaker Notes</summary>
                          <p className="mt-2">{slide.speaker_notes}</p>
                        </details>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PitchDeckGenerator;
