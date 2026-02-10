/**
 * path: src/presentation/js/footer.js
 * description: Global Footer Injector v21.1 - Thesis Candidate.
 * 
 * ABSTRACT:
 * Orchestrates the shared footer component across the Z-Realism ecosystem.
 * This script ensures architectural consistency and provides a professional 
 * sitemap for the research laboratories.
 * 
 * ARCHITECTURAL ROLE (Presentation Layer):
 * Acts as a Shared Component Injector. It adheres to the DRY principle 
 * by centralizing site-wide metadata, legal links, and system status badges.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. COMPONENT MANIFOLD (HTML STRUCTURE)
    const footerHTML = `
    <footer class="site-footer">
        <div class="footer-grid">
            
            <!-- Brand Identity & Mission -->
            <div class="footer-brand">
                <h3>🐉 Z-REALISM</h3>
                <p>
                    The advanced neural research platform for photorealistic character synthesis. 
                    Utilizing a Subject Metadata Knowledge Base to bridge the gap between 
                    stylized ink and cinematic life.
                </p>
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

            <!-- Compliance & Legal -->
            <div class="footer-col">
                <h4>COMPLIANCE</h4>
                <ul class="footer-links">
                    <li><a href="legal.html">Terms & Licensing</a></li>
                    <li><a href="legal.html#cookies">Neural Cache Policy</a></li>
                </ul>
            </div>

        </div>

        <!-- Footer Bottom: Legal & System Telemetry -->
        <div class="footer-bottom">
            <div class="footer-copy">
                &copy; 2024 ENRIQUE GONZÁLEZ GUTIÉRREZ. ARCHITECTED UNDER SOLID PRINCIPLES.
            </div>
            
            <!-- Technical Status Badge -->
            <div class="status-badge" style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: var(--accent); opacity: 0.8;">
                v21.1 STABLE // CUDA_ORCHESTRATOR_ACTIVE
            </div>
        </div>
    </footer>
    `;

    // 2. INJECTION PROTOCOL
    // Appends the footer at the terminal edge of the body element.
    document.body.insertAdjacentHTML('beforeend', footerHTML);
    
    // Telemetry Log
    console.log("FOOTER_SYNC: Global footer component synchronized.");
});