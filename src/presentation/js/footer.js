/**
 * path: src/presentation/js/footer.js
 * description: Global Footer Injector v1.2 - Multi-language Production.
 * 
 * ABSTRACT:
 * Orchestrates the shared footer component across the Z-Realism ecosystem.
 * This version implements a decoupled i18n-aware controller that ensures 
 * brand messaging and legal links are synchronized across global manifolds.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

const injectFooter = () => {
    // 1. COMPONENT CONSTRUCTION
    // Utilizes i18n.translate() for dynamic manifold resolution.
    const footerHTML = `
    <footer class="site-footer">
        <div class="footer-grid">
            
            <!-- Brand Identity & Mission -->
            <div class="footer-brand">
                <h3>🐉 Z-REALISM</h3>
                <p data-i18n="footer_mission">
                    ${i18n.translate('footer_mission')}
                </p>
            </div>

            <!-- Production Services -->
            <div class="footer-col">
                <h4 data-i18n="footer_services">${i18n.translate('footer_services')}</h4>
                <ul class="footer-links">
                    <li><a href="image-lab.html" data-i18n="nav_image">${i18n.translate('nav_image')}</a></li>
                    <li><a href="video-lab.html" data-i18n="nav_video">${i18n.translate('nav_video')}</a></li>
                </ul>
            </div>

            <!-- Company & Technology -->
            <div class="footer-col">
                <h4 data-i18n="footer_company">${i18n.translate('footer_company')}</h4>
                <ul class="footer-links">
                    <li><a href="about.html" data-i18n="nav_about">${i18n.translate('nav_about')}</a></li>
                    <li><a href="architecture.html" data-i18n="nav_tech">${i18n.translate('nav_tech')}</a></li>
                    <li><a href="contact.html" data-i18n="nav_contact">${i18n.translate('nav_contact')}</a></li>
                </ul>
            </div>

            <!-- Legal & Compliance -->
            <div class="footer-col">
                <h4 data-i18n="footer_legal">${i18n.translate('footer_legal')}</h4>
                <ul class="footer-links">
                    <li><a href="legal.html#terms" data-i18n="nav_legal">${i18n.translate('nav_legal')}</a></li>
                    <li><a href="legal.html#privacy" data-i18n="cookie_policy">${i18n.translate('cookie_policy')}</a></li>
                </ul>
            </div>

        </div>

        <!-- Footer Bottom: Legal & System Telemetry -->
        <div class="footer-bottom">
            <div class="footer-copy">
                &copy; 2026 ENRIQUE GONZÁLEZ GUTIÉRREZ. <span data-i18n="footer_rights">${i18n.translate('footer_rights')}</span>.
            </div>
            
            <!-- Technical Status Badge -->
            <div class="status-badge" style="font-family: var(--font-code); font-size: 0.65rem; color: var(--accent); opacity: 0.8;">
                v1.2 PRODUCTION // I18N_MANIFOLD_SYNCED
            </div>
        </div>
    </footer>
    `;

    // 2. INJECTION & CLEANUP
    // Prevents duplicate footers during manifold switching.
    const existingFooter = document.querySelector('.site-footer');
    if (existingFooter) existingFooter.remove();
    document.body.insertAdjacentHTML('beforeend', footerHTML);
    
    console.log(`FOOTER_SYNC: Component manifold [${i18n.currentLang.toUpperCase()}] synchronized.`);
};

// --- SUBSCRIPTION INTERFACES ---
// Ensure the component renders only when the translation engine is ready.
if (i18n.isReady) {
    injectFooter();
} else {
    window.addEventListener('i18nReady', injectFooter);
}

// React to global language changes (triggered by the i18n-engine)
window.addEventListener('langChanged', injectFooter);