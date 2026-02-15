/**
 * path: src/presentation/js/nav.js
 * description: Global Navigation Injector v23.2 - SVG Flags Edition.
 * 
 * ABSTRACT:
 * Orchestrates the shared navigation manifold.
 * 
 * FIX v23.2:
 * Replaced OS-dependent Emoji flags with embedded SVGs. This resolves 
 * rendering issues on Windows 10/11 where flags appear as "US/ES" letters.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

const injectNav = () => {
    // 1. URI PATH ANALYSIS
    const currentPath = window.location.pathname;
    const isActive = (filename) => currentPath.includes(filename) ? 'active' : '';

    // 2. SVG FLAGS (Embedded for Cross-Platform Consistency)
    const flagUS = `https://upload.wikimedia.org/wikipedia/en/a/a4/Flag_of_the_United_States.svg`;
    const flagES = `https://upload.wikimedia.org/wikipedia/commons/9/9a/Flag_of_Spain.svg`;

    // 3. LANGUAGE SELECTOR MANIFOLD
    const langToggle = `
        <div class="lang-selector">
            <button onclick="i18n.setLanguage('en')" 
                    class="flag-btn ${i18n.currentLang === 'en' ? 'active' : ''}" 
                    title="English"
                    aria-label="Switch to English">
                <img src="${flagUS}" alt="USA Flag">
            </button>
            <button onclick="i18n.setLanguage('es')" 
                    class="flag-btn ${i18n.currentLang === 'es' ? 'active' : ''}" 
                    title="Español"
                    aria-label="Cambiar a Español">
                <img src="${flagES}" alt="Spain Flag">
            </button>
        </div>
    `;

    // 4. COMPONENT CONSTRUCTION
    const navHTML = `
    <nav class="main-nav">
        <!-- Brand Identity -->
        <a href="index.html" class="nav-logo">
            <span>🐉</span> Z-REALISM
        </a>

        <!-- Interactive Mobile Toggle (Hamburger) -->
        <button class="menu-toggle" id="nav-toggle" aria-label="Toggle menu">
            <span></span>
            <span></span>
            <span></span>
        </button>
        
        <!-- Navigation Nodes & Language Selection -->
        <div class="nav-links" id="nav-menu">
            <a href="image-lab.html" class="nav-item ${isActive('image-lab')}" data-i18n="nav_image">
                ${i18n.translate('nav_image')}
            </a>
            <a href="video-lab.html" class="nav-item ${isActive('video-lab')}" data-i18n="nav_video">
                ${i18n.translate('nav_video')}
            </a>
            <a href="about.html" class="nav-item ${isActive('about')}" data-i18n="nav_about">
                ${i18n.translate('nav_about')}
            </a>
            <a href="architecture.html" class="nav-item ${isActive('architecture')}" data-i18n="nav_tech">
                ${i18n.translate('nav_tech')}
            </a>
            <a href="contact.html" class="nav-item ${isActive('contact')}" data-i18n="nav_contact">
                ${i18n.translate('nav_contact')}
            </a>
            <a href="legal.html" class="nav-item ${isActive('legal')}" data-i18n="nav_legal">
                ${i18n.translate('nav_legal')}
            </a>
            
            <!-- Injected Flag Toggles -->
            ${langToggle}
        </div>
    </nav>
    `;

    // 5. INJECTION & CLEANUP PROTOCOL
    const existingNav = document.querySelector('.main-nav');
    if (existingNav) existingNav.remove();
    document.body.insertAdjacentHTML('afterbegin', navHTML);

    // 6. RESPONSIVE INTERACTION LOGIC
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');

    if (navToggle && navMenu) {
        navToggle.onclick = () => {
            const isOpened = navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
            console.log(`NAV_INTERACT: Mobile drawer ${isOpened ? 'Opened' : 'Closed'}`);
        };

        navMenu.querySelectorAll('.nav-item').forEach(link => {
            link.onclick = () => {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
            };
        });
    }

    console.log(`NAV_SYNC: Production manifold [${i18n.currentLang.toUpperCase()}] injected.`);
};

// --- SYSTEM SUBSCRIPTION ---
if (i18n.isReady) {
    injectNav();
} else {
    window.addEventListener('i18nReady', injectNav);
}

window.addEventListener('langChanged', injectNav);