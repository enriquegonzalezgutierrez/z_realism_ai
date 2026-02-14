/**
 * path: src/presentation/js/nav.js
 * description: Global Navigation Injector v1.0 - Commercial Product.
 * 
 * ABSTRACT:
 * Orchestrates the shared navigation component across the Z-Realism production ecosystem.
 * This script ensures architectural consistency and provides real-time 
 * visual feedback for the current product section.
 * 
 * ARCHITECTURAL ROLE (Presentation Layer):
 * Acts as a Shared Component Injector. It centralizes the navigation structure 
 * and active-state logic for a streamlined user experience.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. URI PATH ANALYSIS
    const currentPath = window.location.pathname;
    
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
            <a href="image-lab.html" class="nav-item ${isActive('image-lab')}">Image Production</a>
            <a href="video-lab.html" class="nav-item ${isActive('video-lab')}">Video Production</a>
            <a href="about.html" class="nav-item ${isActive('about')}">About Us</a>
            <a href="architecture.html" class="nav-item ${isActive('architecture')}">Technology</a>
            <a href="contact.html" class="nav-item ${isActive('contact')}">Contact Us</a>
            <a href="legal.html" class="nav-item ${isActive('legal')}">Legal & Privacy</a>
        </div>
    </nav>
    `;

    // 3. INJECTION PROTOCOL
    document.body.insertAdjacentHTML('afterbegin', navHTML);
    
    // Telemetry Log for Debugging
    console.log(`NAV_SYNC: Navigation component injected. Active Node: [${currentPath}]`);
});