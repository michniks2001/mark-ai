/**
 * API client for the Marketing Tool backend
 */

const API_BASE_URL = '/api';

/**
 * Fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || data.detail || `HTTP ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

/**
 * Get list of available target audiences
 */
export async function getTargetAudiences() {
  return fetchAPI('/target-audiences');
}

/**
 * Generate a pitch deck
 */
export async function generatePitchDeck(data) {
  return fetchAPI('/generate-pitch-deck', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Get download URL for a pitch deck file
 */
export function getPitchDeckDownloadUrl(filename) {
  return `${API_BASE_URL}/download-pitch-deck/${filename}`;
}

/**
 * Test Dedalus endpoint (for debugging)
 */
export async function testDedalus(data) {
  return fetchAPI('/test-dedalus', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Health check
 */
export async function healthCheck() {
  return fetchAPI('/health');
}

/**
 * Dedalus ping
 */
export async function dedalusPing() {
  return fetchAPI('/dedalus-ping');
}
