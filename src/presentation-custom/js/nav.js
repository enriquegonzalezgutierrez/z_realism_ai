/**
 * path: src/presentation-custom/js/nav.js
 * description: Shared Component Injector - Global Navigation.
 * 
 * ABSTRACT:
 * Consolidates the navigation logic for the Z-Realism ecosystem.
 * Implements "Active Link Detection" to provide visual feedback 
 * based on the current URI.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    
    // Helper to determine if a link is active
    const isActive = (path) => currentPath.includes(path) ? 'active' : '';

    const navHTML = `
    <nav class="main-nav">
        <a href="index.html" class="nav-logo">
            <span>🐉</span> Z-REALISM
        </a>
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

    // Inject the navigation at the top of the body
    document.body.insertAdjacentHTML('afterbegin', navHTML);
});