/**
 * path: src/presentation-custom/js/footer.js
 * description: Shared Component Injector - Global Footer.
 * 
 * ABSTRACT:
 * This script ensures all pages in the Z-Realism ecosystem share the 
 * same footer without code duplication (DRY Principle).
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {
    const footerHTML = `
    <footer class="site-footer">
        <div class="footer-grid">
            
            <!-- Brand & Mission -->
            <div class="footer-brand">
                <h3>🐉 Z-REALISM</h3>
                <p>The advanced neural research platform for 2D character photorealistic synthesis. Bridging the gap between ink and life.</p>
            </div>

            <!-- Laboratory Nodes -->
            <div class="footer-col">
                <h4>LABORATORIES</h4>
                <ul class="footer-links">
                    <li><a href="image-lab.html">Static Fusion Lab</a></li>
                    <li><a href="video-lab.html">Temporal Fusion Lab</a></li>
                </ul>
            </div>

            <!-- Documentation & Research -->
            <div class="footer-col">
                <h4>RESEARCH</h4>
                <ul class="footer-links">
                    <li><a href="about.html">Our Mission</a></li>
                    <li><a href="architecture.html">System Architecture</a></li>
                    <li><a href="contact.html">Peer Review & Contact</a></li>
                </ul>
            </div>

            <!-- Legal & Privacy -->
            <div class="footer-col">
                <h4>COMPLIANCE</h4>
                <ul class="footer-links">
                    <li><a href="legal.html">Terms & Licensing</a></li>
                    <li><a href="legal.html#cookies">Neural Cache Policy</a></li>
                </ul>
            </div>

        </div>

        <div class="footer-bottom">
            <div class="footer-copy">
                &copy; 2024 ENRIQUE GONZÁLEZ GUTIÉRREZ. ARCHITECTED UNDER SOLID PRINCIPLES.
            </div>
            <div class="status-badge">
                v20.2 STABLE // CUDA_ORCHESTRATOR_ACTIVE
            </div>
        </div>
    </footer>
    `;

    // Append the footer to the end of the body
    document.body.insertAdjacentHTML('beforeend', footerHTML);
});