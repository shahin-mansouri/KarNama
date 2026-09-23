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

const stepCards = document.querySelectorAll('.steps-grid > div');
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (stepCards.length && !reduceMotion) {
    let activeStep = 0;

    const highlightNextStep = () => {
        stepCards.forEach(card => card.classList.remove('is-auto-hover'));
        stepCards[activeStep].classList.add('is-auto-hover');
        activeStep = (activeStep + 1) % stepCards.length;
    };

    highlightNextStep();
    window.setInterval(highlightNextStep, 1500);
}

const heroTypedText = document.getElementById('heroTypedText');
const heroPhrases = [
    'داستان شما',
    'مسیر شما',
    'مهارت‌ شما',
    'تجربه‌ شما',
    'توانایی شما',
];

if (heroTypedText && !reduceMotion) {
    let phraseIndex = 0;
    let characterIndex = heroPhrases[phraseIndex].length;
    let isDeleting = false;

    const typeHeroPhrase = () => {
        const phrase = heroPhrases[phraseIndex];
        heroTypedText.textContent = phrase.slice(0, characterIndex);

        if (!isDeleting && characterIndex < phrase.length) {
            characterIndex += 1;
            window.setTimeout(typeHeroPhrase, 85);
            return;
        }

        if (!isDeleting) {
            isDeleting = true;
            window.setTimeout(typeHeroPhrase, 1800);
            return;
        }

        if (characterIndex > 0) {
            characterIndex -= 1;
            window.setTimeout(typeHeroPhrase, 45);
            return;
        }

        phraseIndex = (phraseIndex + 1) % heroPhrases.length;
        isDeleting = false;
        window.setTimeout(typeHeroPhrase, 350);
    };

    window.setTimeout(() => {
        isDeleting = true;
        typeHeroPhrase();
    }, 1800);
}
