/**
 * path: src/presentation/js/footer.js
 * description: Global Footer Injector v1.0 - Commercial Product.
 * 
 * ABSTRACT:
 * Orchestrates the shared footer component across the Z-Realism production ecosystem.
 * This script ensures architectural consistency and provides a professional 
 * sitemap for clients and partners.
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
                    The advanced neural production studio for photorealistic content synthesis. 
                    Empowering artists and designers to bring their original artwork to life.
                </p>
            </div>

            <!-- Production Services -->
            <div class="footer-col">
                <h4>SERVICES</h4>
                <ul class="footer-links">
                    <li><a href="image-lab.html">Image Production</a></li>
                    <li><a href="video-lab.html">Video Production</a></li>
                </ul>
            </div>

            <!-- Company & Technology -->
            <div class="footer-col">
                <h4>COMPANY</h4>
                <ul class="footer-links">
                    <li><a href="about.html">About Us</a></li>
                    <li><a href="architecture.html">Technology</a></li>
                    <li><a href="contact.html">Contact Us</a></li>
                </ul>
            </div>

            <!-- Legal & Compliance -->
            <div class="footer-col">
                <h4>LEGAL</h4>
                <ul class="footer-links">
                    <li><a href="legal.html">Terms & Privacy</a></li>
                    <li><a href="legal.html#cookies">Cookie Policy</a></li>
                </ul>
            </div>

        </div>

        <!-- Footer Bottom: Legal & System Telemetry -->
        <div class="footer-bottom">
            <div class="footer-copy">
                &copy; 2026 ENRIQUE GONZÁLEZ GUTIÉRREZ. ALL RIGHTS RESERVED.
            </div>
            
            <!-- Technical Status Badge -->
            <div class="status-badge" style="font-family: var(--font-code); font-size: 0.65rem; color: var(--accent); opacity: 0.8;">
                v1.0 PRODUCTION // OPTIMIZED FOR CREATIVES
            </div>
        </div>
    </footer>
    `;

    // 2. INJECTION PROTOCOL
    document.body.insertAdjacentHTML('beforeend', footerHTML);
    
    // Telemetry Log
    console.log("FOOTER_SYNC: Global footer component synchronized.");
});