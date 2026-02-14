/**
 * path: src/presentation-custom/js/api.js
 * description: Shared API Bridge v22.3 - Robust Path Resolution Edition.
 * 
 * ABSTRACT:
 * Orchestrates all client-side communication with the Neural API Gateway.
 * 
 * KEY FIXES (v22.3):
 * 1. Implemented a robust `joinUrl` helper to prevent malformed API paths 
 *    (e.g., '/apianalyze') caused by missing slashes during concatenation.
 * 2. Enhanced error handling to detect HTML responses (404/502 from Nginx) 
 *    before attempting to parse them as JSON, providing clearer debug info.
 * 3. Standardized relative path strategy for production deployments.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

/**
 * INTELLIGENT API DISCOVERY
 * Automatically determines the backend location based on the access context.
 */
const getDynamicApiUrl = () => {
    // 1. Developer Override (localStorage hook for debugging)
    const override = localStorage.getItem('Z_REALISM_API_OVERRIDE');
    if (override) return override;

    // 2. LOCALHOST DEVELOPMENT (Direct Port 8000 Access)
    // If running locally without Nginx proxy (e.g., npm start vs uvicorn),
    // target the API container directly.
    if (window.location.port === '8080') {
        const { hostname, protocol } = window.location;
        return `${protocol}//${hostname}:8000`;
    }

    // 3. PRODUCTION / TUNNEL STRATEGY (Port 80 / Reverse Proxy)
    // Returns a relative path prefix. The browser automatically prepends 
    // the current protocol and domain. This resolves Mixed Content issues 
    // and ensures correct routing through the Nginx '/api' location block.
    console.log("%cPRODUCTION_INFO: Using Relative Path Strategy (/api)", "color: #10b981; font-weight: bold;");
    return '/api'; 
};

const API_BASE_URL = getDynamicApiUrl();

// MANDATORY HEADERS FOR REMOTE CONNECTIVITY
// 'ngrok-skip-browser-warning' allows programmatic access to Ngrok tunnels 
// without tripping the anti-phishing interstitial page.
const SHARED_HEADERS = {
    "ngrok-skip-browser-warning": "true"
};

console.log(`%c🐉 Z-REALISM GATEWAY: ${API_BASE_URL}`, "color: #8b5cf6; font-weight: bold;");

/**
 * Robust URL Joiner Helper.
 * Ensures exactly one slash exists between the base URL and the endpoint path,
 * preventing malformed requests like '/apianalyze'.
 * 
 * @param {string} base - The API base URL (e.g., '/api')
 * @param {string} path - The specific endpoint (e.g., '/analyze')
 * @returns {string} The correctly formatted URL.
 */
function joinUrl(base, path) {
    const cleanBase = base.replace(/\/$/, ''); // Remove trailing slash if present
    const cleanPath = path.startsWith('/') ? path : `/${path}`; // Ensure leading slash
    return `${cleanBase}${cleanPath}`;
}

/**
 * Sends a multipart/form-data payload to the neural gateway.
 * @param {string} endpoint - Target route (e.g., '/transform').
 * @param {FormData} formData - Payload containing assets and parameters.
 */
async function postToGateway(endpoint, formData) {
    try {
        // Construct the target URL using the robust joiner
        const targetUrl = joinUrl(API_BASE_URL, endpoint);

        const response = await fetch(targetUrl, {
            method: 'POST',
            body: formData,
            headers: SHARED_HEADERS
        });
        
        if (!response.ok) {
            // Diagnostic check: Did we get an HTML error page (404/502) instead of JSON?
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("text/html")) {
                throw new Error(`Server returned HTML error (${response.status}). Check URL construction: ${targetUrl}`);
            }

            const errorData = await response.json();
            throw new Error(errorData.detail || `Gateway Error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error("GATEWAY_DISPATCH_FAILURE:", error);
        alert(`Neural Gateway Unreachable: ${error.message}`);
        return null;
    }
}

/**
 * Polls the system status for a specific asynchronous neural task.
 * @param {string} taskId - The Celery Task UUID.
 * @param {Function} onProgress - Callback for real-time telemetry updates.
 * @param {Function} onComplete - Callback for final result injection.
 */
async function pollNeuralTask(taskId, onProgress, onComplete) {
    if (!taskId) return;

    const pollingInterval = setInterval(async () => {
        try {
            // Construct status endpoint
            const statusUrl = joinUrl(API_BASE_URL, `/status/${taskId}`);
            
            const response = await fetch(statusUrl, {
                headers: SHARED_HEADERS
            });
            const data = await response.json();

            if (data.status === 'PROGRESS') {
                if (onProgress) onProgress(data.progress);
            } 
            else if (data.status === 'SUCCESS') {
                clearInterval(pollingInterval);
                
                // Construct result endpoint
                const resultUrl = joinUrl(API_BASE_URL, `/result/${taskId}`);
                const resultResponse = await fetch(resultUrl, {
                    headers: SHARED_HEADERS
                });
                
                if (resultResponse.ok) {
                    const resultData = await resultResponse.json();
                    if (onComplete) onComplete(resultData);
                } else {
                    console.error("FINAL_RETRIEVAL_ERROR: Unable to fetch result payload.");
                }
            } 
            else if (data.status === 'FAILURE') {
                clearInterval(pollingInterval);
                alert("NEURAL_ENGINE_FAILURE: Inference loop crashed. Check worker logs.");
                if (onComplete) onComplete(null);
            }
        } catch (error) {
            // Suppress network jitter errors to keep polling alive
            console.warn("POLLING_RETRY: Connection unstable.");
        }
    }, 1000); // Poll frequency: 1Hz
}

/**
 * Utility: Generates a local preview URL for uploaded files.
 */
function createPreviewURL(file) {
    return URL.createObjectURL(file);
}