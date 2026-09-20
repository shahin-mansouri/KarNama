const homeProgress = document.getElementById('homeScrollProgress');
const homeBackTop = document.getElementById('homeBackTop');
const homeMenuToggle = document.getElementById('homeMenuToggle');
const homeNav = document.querySelector('.home-nav');

window.addEventListener('scroll', () => {
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    const progress = maxScroll > 0 ? (window.scrollY / maxScroll) * 100 : 0;
    homeProgress.style.width = `${progress}%`;
    homeBackTop.classList.toggle('visible', window.scrollY > 320);
});

homeBackTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

homeMenuToggle.addEventListener('click', () => {
    const isOpen = homeNav.classList.toggle('open');
    homeMenuToggle.classList.toggle('open', isOpen);
    homeMenuToggle.setAttribute('aria-expanded', isOpen);
});

homeNav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
        homeNav.classList.remove('open');
        homeMenuToggle.classList.remove('open');
        homeMenuToggle.setAttribute('aria-expanded', 'false');
    });
});
