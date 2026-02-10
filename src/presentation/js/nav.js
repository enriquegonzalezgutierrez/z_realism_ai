/**
 * path: src/presentation/js/nav.js
 * description: Global Navigation Injector v21.1 - Thesis Candidate.
 * 
 * ABSTRACT:
 * Orchestrates the shared navigation component across the Z-Realism ecosystem.
 * This script ensures architectural consistency and provides real-time 
 * visual feedback for current URI location.
 * 
 * ARCHITECTURAL ROLE (Presentation Layer):
 * Acts as a Shared Component Injector. It reduces code duplication by 
 * centralizing the navigation structure and its active-state logic.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. URI PATH ANALYSIS
    // Extract the current filename to determine the active navigation node.
    const currentPath = window.location.pathname;
    
    /**
     * Heuristic to determine if a navigation link is the active manifold.
     * @param {string} filename - The target page filename.
     * @returns {string} The CSS class for the active state.
     */
    const isActive = (filename) => currentPath.includes(filename) ? 'active' : '';

    // 2. COMPONENT MANIFOLD (HTML STRUCTURE)
    const navHTML = `
    <nav class="main-nav">
        <!-- Brand Identity -->
        <a href="index.html" class="nav-logo">
            <span>🐉</span> Z-REALISM
        </a>
        
        <!-- Navigation Nodes -->
        <div class="nav-links">
            <a href="image-lab.html" class="nav-item ${isActive('image-lab')}">Static Lab</a>
            <a href="video-lab.html" class="nav-item ${isActive('video-lab')}">Temporal Lab</a>
            <a href="about.html" class="nav-item ${isActive('about')}">About</a>
            <a href="architecture.html" class="nav-item ${isActive('architecture')}">Architecture</a>
            <a href="contact.html" class="nav-item ${isActive('contact')}">Contact</a>
            <a href="legal.html" class="nav-item ${isActive('legal')}">Legal</a>
        </div>
    </nav>
    `;

    // 3. INJECTION PROTOCOL
    // Inserts the component at the high-level entry of the body, 
    // preceding the main content containers.
    document.body.insertAdjacentHTML('afterbegin', navHTML);
    
    // Telemetry Log for Debugging in Development Environments
    console.log(`NAV_SYNC: Navigation component injected. Active Node: [${currentPath}]`);
});