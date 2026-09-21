// ---------- DATA ----------
const portfolioData = JSON.parse(document.getElementById('portfolio-data').textContent);
const skillsData = portfolioData.skills;
const experienceData = portfolioData.experience;
const projectsData = portfolioData.projects;
const certificatesData = portfolioData.certificates;
const languagesData = portfolioData.languages || [];
const researchesData = portfolioData.researches || [];
const socialLinksData = portfolioData.social_links || [];
const testimonialsData = portfolioData.testimonials || [];

// ---------- STATE ----------
let currentTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light');
let currentFilter = 'all';

// ---------- DOM refs ----------
const htmlEl = document.documentElement;
const navLinks = document.getElementById('navLinks');
const hamburger = document.getElementById('hamburger');
const themeToggle = document.getElementById('themeToggle');
const printResume = document.getElementById('printResume');
const backTop = document.getElementById('backTop');
const scrollProgress = document.getElementById('scrollProgress');
const skillsGrid = document.getElementById('skillsGrid');
const expTimeline = document.getElementById('experienceTimeline');
const projectsGrid = document.getElementById('projectsGrid');
const certificatesGrid = document.getElementById('certificatesGrid');
const languagesGrid = document.getElementById('languagesGrid');
const researchesGrid = document.getElementById('researchesGrid');
const socialLinksGrid = document.getElementById('socialLinksGrid');
const heroSocialLinks = document.getElementById('heroSocialLinks');
const contactSocialLinks = document.getElementById('contactSocialLinks');
const testimonialsGrid = document.getElementById('testimonialsGrid');
const filterBtns = document.getElementById('filterBtns');
const contactForm = document.getElementById('contactForm');
const formMessage = document.getElementById('formMessage');
const testimonialForm = document.getElementById('testimonialForm');
const testimonialMessage = document.getElementById('testimonialMessage');
let testimonialIndex = 0;
let testimonialTimer;

// ---------- THEME ----------
function setTheme(theme) {
    currentTheme = theme;
    localStorage.setItem('theme', theme);
    htmlEl.setAttribute('data-theme', theme === 'dark' ? 'dark' : '');
    themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
}

// ---------- RENDER SKILLS ----------
function renderSkills() {
    skillsGrid.innerHTML = skillsData.map(s => `
    <div class="skill-item fade-in">
        <div class="name">${s.name}</div>
        <div class="skill-bar"><div class="fill" style="width:0%; --skill-level:${s.level}%" data-level="${s.level}"></div></div>
    </div>
    `).join('');
    // animate fill
    setTimeout(() => {
    document.querySelectorAll('.skill-item .fill').forEach(el => {
        el.style.width = el.dataset.level + '%';
    });
    }, 300);
}

// ---------- RENDER EXPERIENCE ----------
function renderExperience() {
    expTimeline.innerHTML = experienceData.map(exp => `
    <div class="timeline-item fade-in">
        <div class="date">${exp.start} — ${exp.end}</div>
        <h3>${exp.position}</h3>
        <div class="company">${exp.company} · ${exp.location}</div>
        <div class="desc">${exp.desc}</div>
        <div class="tech-tags">${exp.techs.map(t => `<span>${t}</span>`).join('')}</div>
    </div>
    `).join('');
}

// ---------- RENDER PROJECTS ----------
function compactUrl(url) {
    if (!url || url === '#') return '';
    try {
        const parsed = new URL(url, window.location.origin);
        const path = parsed.pathname === '/' ? '' : parsed.pathname.replace(/\/$/, '');
        return parsed.hostname.replace(/^www\./, '') + path;
    } catch {
        return url;
    }
}

function renderProjects(filter = currentFilter) {
    const filtered = filter === 'all' ? projectsData : projectsData.filter(p => p.category === filter);
    projectsGrid.innerHTML = filtered.map(p => {
        const github = p.github && p.github !== '#' ? `<a href="${p.github}" target="_blank" rel="noopener" data-print-url="${compactUrl(p.github)}">GitHub</a>` : '';
        const demo = p.demo && p.demo !== '#' ? `<a href="${p.demo}" target="_blank" rel="noopener" data-print-url="${compactUrl(p.demo)}">Demo</a>` : '';
        return `
    <div class="project-card card fade-in">
        <div class="img-wrap" aria-hidden="true"><div class="project-placeholder"><img src="${p.project_picture}" alt="${p.title}" /></div></div>
        <h3>${p.title}</h3>
        <div class="tech">${p.tech}</div>
        <p style="color:var(--text2);font-size:0.95rem;">${p.desc}</p>
        <div class="links">${github}${demo}</div>
    </div>
    `;
    }).join('');
}

function renderCertificates() {
    certificatesGrid.innerHTML = certificatesData.length ? certificatesData.map(certificate => `
    <article class="certificate-card card fade-in">
        <h3>${certificate.name}</h3>
        <p class="certificate-issuer">${certificate.issuer}</p>
        ${certificate.date ? `<p class="certificate-date">${certificate.date}</p>` : ''}
        ${certificate.link !== '#' ? `<a href="${certificate.link}" target="_blank" rel="noopener" data-print-url="${compactUrl(certificate.link)}">مشاهده گواهینامه</a>` : ''}
    </article>
    `).join('') : '<p class="empty-state">هنوز گواهینامه‌ای ثبت نشده است.</p>';
}

function renderLanguages() {
    if (!languagesGrid) return;
    languagesGrid.innerHTML = languagesData.map(language => `
    <div class="language-item card fade-in">
        <div class="language-heading"><strong>${escapeHtml(language.name)}</strong><span>${language.level}%</span></div>
        <div class="skill-bar"><div class="fill" style="width:${language.level}%; --skill-level:${language.level}%"></div></div>
    </div>
    `).join('');
}

function renderResearches() {
    if (!researchesGrid) return;
    researchesGrid.innerHTML = researchesData.map(research => `
    <article class="research-card card fade-in">
        <div class="research-year">${research.year}</div>
        <h3>${escapeHtml(research.title)}</h3>
        ${research.description ? `<p class="research-description">${escapeHtml(research.description)}</p>` : ''}
        ${research.link && research.link !== '#' ? `<a href="${research.link}" target="_blank" rel="noopener" data-print-url="${compactUrl(research.link)}">مراجعه به تحقیق</a>` : ''}
    </article>
    `).join('');
}

const socialIconUrls = {
    github: 'https://cdn.simpleicons.org/github',
    linkedin: 'https://cdn.simpleicons.org/linkedin',
    instagram: 'https://cdn.simpleicons.org/instagram',
    twitter: 'https://cdn.simpleicons.org/x',
    telegram: 'https://cdn.simpleicons.org/telegram',
    facebook: 'https://cdn.simpleicons.org/facebook',
    youtube: 'https://cdn.simpleicons.org/youtube',
    website: 'https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6/svgs/solid/globe.svg',
};
function socialLinkMarkup(social) {
    const iconUrl = socialIconUrls[social.platform] || 'https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6/svgs/solid/link.svg';
    return `<a class="social-link" href="${social.url}" target="_blank" rel="noopener" aria-label="${escapeHtml(social.label)}" title="${escapeHtml(social.label)}" data-print-url="${compactUrl(social.url)}"><img src="${iconUrl}" alt="" loading="lazy"><span>${escapeHtml(social.label)}</span></a>`;
}

function renderSocialLinks() {
    const markup = socialLinksData.map(socialLinkMarkup).join('');
    if (socialLinksGrid) socialLinksGrid.innerHTML = markup;
    if (heroSocialLinks) heroSocialLinks.innerHTML = markup;
    if (contactSocialLinks) contactSocialLinks.innerHTML = markup;
}

function escapeHtml(value) {
    const element = document.createElement('div');
    element.textContent = value || '';
    return element.innerHTML;
}

function renderTestimonials() {
    clearTimeout(testimonialTimer);
    if (!testimonialsData.length) {
        testimonialsGrid.innerHTML = '<p class="empty-state">هنوز نظری ثبت نشده است. اولین نفر باشید.</p>';
        return;
    }

    const testimonial = testimonialsData[testimonialIndex % testimonialsData.length];
    testimonialsGrid.innerHTML = `
    <article class="testimonial-card fade-in visible">
        <div class="quote-mark">“</div>
        <p class="testimonial-text"></p>
        <div class="testimonial-author">
            <div class="author-avatar">${escapeHtml(testimonial.author).charAt(0)}</div>
            <div><strong>${escapeHtml(testimonial.author)}</strong><span>${escapeHtml(testimonial.role) || 'همکار حرفه‌ای'}</span></div>
        </div>
    </article>
    `;

    const textElement = testimonialsGrid.querySelector('.testimonial-text');
    const text = testimonial.text || '';
    let characterIndex = 0;
    const typeNextCharacter = () => {
        textElement.textContent = text.slice(0, characterIndex++);
        if (characterIndex <= text.length) {
            setTimeout(typeNextCharacter, 18);
        } else {
            testimonialTimer = setTimeout(() => {
                testimonialIndex = (testimonialIndex + 1) % testimonialsData.length;
                renderTestimonials();
            }, 3000);
        }
    };
    typeNextCharacter();
}

function renderFilterBtns() {
    const cats = ['all', ...new Set(projectsData.map(p => p.category))];
    filterBtns.innerHTML = cats.map(c => `
    <button class="${c === currentFilter ? 'active' : ''}" data-filter="${c}">${c.charAt(0).toUpperCase() + c.slice(1)}</button>
    `).join('');
    filterBtns.querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', () => {
        currentFilter = btn.dataset.filter;
        filterBtns.querySelectorAll('button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderProjects(currentFilter);
    });
    });
}

// ---------- STATS ANIMATION ----------
function renderStats() {
    const nums = document.querySelectorAll('.stat-item .num');
    nums.forEach(el => {
    const target = parseInt(el.dataset.count);
    let current = 0;
    const step = Math.ceil(target / 30);
    const interval = setInterval(() => {
        current += step;
        if (current >= target) { current = target; clearInterval(interval); }
        el.textContent = current;
    }, 40);
    });
}

// ---------- SCROLL REVEAL ----------
function handleScrollReveal() {
    const els = document.querySelectorAll('.fade-in:not(.visible)');
    els.forEach(el => {
    const rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight - 80) el.classList.add('visible');
    });
}

// ---------- BACK TO TOP + PROGRESS ----------
window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    const progress = maxScroll > 0 ? (scrollY / maxScroll) * 100 : 0;
    scrollProgress.style.width = progress + '%';
    backTop.classList.toggle('visible', scrollY > 300);
});
backTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

// ---------- NAV ----------
hamburger.addEventListener('click', () => {
    const open = navLinks.classList.toggle('open');
    hamburger.setAttribute('aria-expanded', open);
});
navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
    navLinks.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
    link.classList.add('active');
    });
});
// highlight active section
const sections = document.querySelectorAll('section[id]');
window.addEventListener('scroll', () => {
    let currentSection = '';
    sections.forEach(s => {
    const top = s.offsetTop - 120;
    if (window.scrollY >= top) currentSection = s.id;
    });
    navLinks.querySelectorAll('a').forEach(a => {
    a.classList.toggle('active', a.getAttribute('href') === '#' + currentSection);
    });
});

// ---------- FORM ----------
contactForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    formMessage.textContent = 'در حال ارسال...';
    formMessage.style.color = 'var(--text2)';

    try {
        const response = await fetch(contactForm.action, {
            method: 'POST',
            body: new FormData(contactForm),
            headers: {'X-Requested-With': 'XMLHttpRequest'},
        });
        const result = await response.json();

        if (!response.ok) {
            const firstError = Object.values(result.errors || {})[0];
            throw new Error(firstError?.[0]?.message || 'لطفاً اطلاعات فرم را بررسی کنید.');
        }

        formMessage.textContent = result.message;
        formMessage.style.color = 'green';
        contactForm.reset();
    } catch (error) {
        formMessage.textContent = error.message || 'ارسال پیام انجام نشد.';
        formMessage.style.color = 'red';
    }
});

testimonialForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    testimonialMessage.textContent = 'در حال ثبت نظر...';
    testimonialMessage.style.color = 'var(--text2)';

    try {
        const response = await fetch(testimonialForm.action, {
            method: 'POST',
            body: new FormData(testimonialForm),
            headers: {'X-Requested-With': 'XMLHttpRequest'},
        });
        const result = await response.json();
        if (!response.ok) {
            const firstError = Object.values(result.errors || {})[0];
            throw new Error(firstError?.[0]?.message || 'لطفاً اطلاعات فرم را بررسی کنید.');
        }

        testimonialsData.unshift(result.testimonial);
        testimonialIndex = 0;
        renderTestimonials();
        testimonialForm.reset();
        testimonialMessage.textContent = result.message;
        testimonialMessage.style.color = 'green';
    } catch (error) {
        testimonialMessage.textContent = error.message || 'ثبت نظر انجام نشد.';
        testimonialMessage.style.color = 'red';
    }
});

// ---------- THEME EVENTS ----------
themeToggle.addEventListener('click', () => setTheme(currentTheme === 'dark' ? 'light' : 'dark'));
printResume?.addEventListener('click', () => window.print());

window.addEventListener('beforeprint', () => {
    renderProjects('all');
    document.querySelectorAll('.skill-item .fill').forEach(el => {
        el.style.width = el.dataset.level + '%';
    });
    document.querySelectorAll('.stat-item .num').forEach(el => {
        el.textContent = el.dataset.count;
    });
    document.querySelectorAll('.fade-in').forEach(el => el.classList.add('visible'));
});
window.addEventListener('afterprint', () => {
    renderProjects(currentFilter);
    document.querySelectorAll('.fade-in').forEach(el => el.classList.add('visible'));
});

// ---------- INIT ----------
function init() {
    setTheme(currentTheme);
    renderFilterBtns();
    renderSkills();
    renderExperience();
    renderProjects();
    renderCertificates();
    renderLanguages();
    renderResearches();
    renderSocialLinks();
    renderTestimonials();
    renderStats();
    // observe fade-in
    const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
    }, { threshold: 0.15 });
    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
    window.addEventListener('scroll', handleScrollReveal);
    handleScrollReveal();
}

init();