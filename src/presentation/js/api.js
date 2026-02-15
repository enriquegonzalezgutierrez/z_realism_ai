/**
 * path: src/presentation/js/api.js
 * description: Shared API Bridge v23.1 - Global i18n Error Synchronization.
 * 
 * ABSTRACT:
 * Orchestrates client-side communication with the Neural API Gateway.
 * This version is fully integrated with the i18n engine to provide 
 * localized error reporting and system status messages.
 * 
 * MODIFICATION LOG v23.1:
 * Integrated i18n.translate() for all user-facing alerts and errors. 
 * The bridge now maps backend error keys to their corresponding localized 
 * strings in the active manifold.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

/**
 * INTELLIGENT API DISCOVERY
 * Automatically determines the backend location based on the access context.
 */
const getDynamicApiUrl = () => {
    const override = localStorage.getItem('Z_REALISM_API_OVERRIDE');
    if (override) return override;

    if (window.location.port === '8080') {
        const { hostname, protocol } = window.location;
        return `${protocol}//${hostname}:8000`;
    }

    console.log("%cPRODUCTION_INFO: Using Relative Path Strategy (/api)", "color: #10b981; font-weight: bold;");
    return '/api'; 
};

const API_BASE_URL = getDynamicApiUrl();

const SHARED_HEADERS = {
    "ngrok-skip-browser-warning": "true"
};

/**
 * Robust URL Joiner Helper.
 * Ensures exactly one slash exists between the base URL and the endpoint path.
 */
function joinUrl(base, path) {
    const cleanBase = base.replace(/\/$/, ''); 
    const cleanPath = path.startsWith('/') ? path : `/${path}`; 
    return `${cleanBase}${cleanPath}`;
}

/**
 * Sends a multipart/form-data payload to the neural gateway.
 * Localized errors are triggered if the server is unreachable or returns a fault.
 */
async function postToGateway(endpoint, formData) {
    try {
        const targetUrl = joinUrl(API_BASE_URL, endpoint);
        const response = await fetch(targetUrl, {
            method: 'POST',
            body: formData,
            headers: SHARED_HEADERS
        });
        
        if (!response.ok) {
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("text/html")) {
                // Critical failure: unexpected HTML response (usually Nginx 404/502)
                throw new Error(i18n.translate('error_gateway_unreachable'));
            }

            const errorData = await response.json();
            // Resolve backend error key through the i18n engine
            const translatedMessage = i18n.translate(errorData.detail || 'error_inference_failed');
            throw new Error(translatedMessage);
        }
        
        return await response.json();
    } catch (error) {
        console.error("GATEWAY_DISPATCH_FAILURE:", error);
        // Display localized alert to the user
        const alertMsg = error.message.includes('error_') ? error.message : i18n.translate('error_gateway_unreachable');
        alert(alertMsg);
        return null;
    }
}

/**
 * Polls the system status for a specific asynchronous neural task.
 * Updates the UI with localized progress states and ETA.
 */
async function pollNeuralTask(taskId, onProgress, onComplete) {
    if (!taskId) return;

    let inferenceStartTime = null;

    const pollingInterval = setInterval(async () => {
        try {
            const statusUrl = joinUrl(API_BASE_URL, `/status/${taskId}`);
            const response = await fetch(statusUrl, { headers: SHARED_HEADERS });
            const data = await response.json();

            if (data.status === 'PROGRESS') {
                const rawProgress = data.progress;
                let percent = rawProgress.percent || 0;
                // Translate the status key received from the worker
                let statusText = i18n.translate(rawProgress.status_text);
                let etaLabel = i18n.translate('status_calculating');

                if (percent === 0) {
                    statusText = i18n.translate('status_warmup');
                    percent = 2; // UI trick to show activity
                } else {
                    if (!inferenceStartTime) inferenceStartTime = Date.now();
                    const elapsedSeconds = (Date.now() - inferenceStartTime) / 1000;
                    const estimatedTotalSeconds = (elapsedSeconds / percent) * 100;
                    const remainingSeconds = Math.max(0, estimatedTotalSeconds - elapsedSeconds);

                    const mins = Math.floor(remainingSeconds / 60);
                    const secs = Math.floor(remainingSeconds % 60);
                    etaLabel = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
                }

                if (onProgress) {
                    onProgress({ percent, status_text: statusText, eta: etaLabel });
                }
            } 
            else if (data.status === 'SUCCESS') {
                clearInterval(pollingInterval);
                const resultUrl = joinUrl(API_BASE_URL, `/result/${taskId}`);
                const resultResponse = await fetch(resultUrl, { headers: SHARED_HEADERS });
                
                if (resultResponse.ok) {
                    const resultData = await resultResponse.json();
                    if (onComplete) onComplete(resultData);
                }
            } 
            else if (data.status === 'FAILURE') {
                clearInterval(pollingInterval);
                // Report localized inference failure
                alert(i18n.translate('error_inference_failed'));
                if (onComplete) onComplete(null);
            }
        } catch (error) {
            console.warn("POLLING_RETRY: Connection unstable.");
        }
    }, 1000);
}