/**
 * path: src/presentation-custom/js/api.js
 * description: Shared API Bridge v20.5 - Dynamic Discovery Mode.
 * 
 * ABSTRACT:
 * This script orchestrates communication with the FastAPI Gateway.
 * It features "Dynamic Discovery," which automatically adjusts the API 
 * base URL based on the client's access manifold (Localhost, Network IP, or Tunnel).
 * 
 * ARCHITECTURAL ROLE:
 * - Decouples the frontend from static environment variables.
 * - Manages the lifecycle of high-latency neural tasks (Dispatch -> Poll -> Retrieve).
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

/**
 * INTELLIGENT API DISCOVERY
 * Automatically determines the backend location based on the access manifold.
 * UPDATED: Added support for Unified Proxy Gateway (/api).
 */
const getDynamicApiUrl = () => {
    const { hostname, protocol, port } = window.location;
    
    // Developer Override: Check if a custom API URL is set in LocalStorage
    const override = localStorage.getItem('Z_REALISM_API_OVERRIDE');
    if (override) return override;

    // LOCAL DEVELOPMENT BYPASS:
    // If accessing UI directly via port 8080, assume API is on port 8000.
    if (port === '8080') {
        return `${protocol}//${hostname}:8000`;
    }

    // UNIFIED PRODUCTION GATEWAY (Ngrok / Nginx):
    // Use the same host/domain but target the /api route.
    // This resolves CORS and 'Fetch Failure' by maintaining Same-Origin policy.
    console.log("%cPRODUCTION_INFO: Routing traffic through Unified Gateway (/api)", "color: #10b981; font-weight: bold;");
    return `${protocol}//${hostname}/api`; 
};

const API_BASE_URL = getDynamicApiUrl();
console.log(`%c🐉 Z-REALISM GATEWAY: ${API_BASE_URL}`, "color: #8b5cf6; font-weight: bold;");

/**
 * Sends a multipart/form-data payload to the neural gateway.
 * @param {string} endpoint - Route (e.g., '/transform', '/animate').
 * @param {FormData} formData - Neural parameters and binary manifolds.
 */
async function postToGateway(endpoint, formData) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
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
            const response = await fetch(`${API_BASE_URL}/status/${taskId}`);
            const data = await response.json();

            if (data.status === 'PROGRESS') {
                if (onProgress) onProgress(data.progress);
            } 
            else if (data.status === 'SUCCESS') {
                clearInterval(pollingInterval);
                
                // Retrieve the actual result from the backend
                const resultResponse = await fetch(`${API_BASE_URL}/result/${taskId}`);
                if (resultResponse.ok) {
                    const resultData = await resultResponse.json();
                    if (onComplete) onComplete(resultData);
                } else {
                    console.error("FINAL_RETRIEVAL_ERROR");
                }
            } 
            else if (data.status === 'FAILURE') {
                clearInterval(pollingInterval);
                alert("NEURAL_ENGINE_FAILURE: Inference loop crashed. Check worker logs.");
                if (onComplete) onComplete(null);
            }
        } catch (error) {
            // We don't clear the interval here to allow for temporary network blips
            console.warn("POLLING_RETRY: Connection unstable.");
        }
    }, 1000); // Frequency: 1Hz
}

/**
 * Logic to generate a local preview URL for uploaded files.
 */
function createPreviewURL(file) {
    return URL.createObjectURL(file);
}