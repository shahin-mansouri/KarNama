// ---------- DATA ----------
const portfolioData = JSON.parse(document.getElementById('portfolio-data').textContent);
const skillsData = portfolioData.skills;
const experienceData = portfolioData.experience;
const projectsData = portfolioData.projects;
const certificatesData = portfolioData.certificates;

// ---------- STATE ----------
let currentTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light');
let currentFilter = 'all';

// ---------- DOM refs ----------
const htmlEl = document.documentElement;
const navLinks = document.getElementById('navLinks');
const hamburger = document.getElementById('hamburger');
const themeToggle = document.getElementById('themeToggle');
const backTop = document.getElementById('backTop');
const scrollProgress = document.getElementById('scrollProgress');
const skillsGrid = document.getElementById('skillsGrid');
const expTimeline = document.getElementById('experienceTimeline');
const projectsGrid = document.getElementById('projectsGrid');
const certificatesGrid = document.getElementById('certificatesGrid');
const filterBtns = document.getElementById('filterBtns');
const contactForm = document.getElementById('contactForm');
const formMessage = document.getElementById('formMessage');

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
        <div class="skill-bar"><div class="fill" style="width:0%" data-level="${s.level}"></div></div>
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
function renderProjects(filter = currentFilter) {
    const filtered = filter === 'all' ? projectsData : projectsData.filter(p => p.category === filter);
    projectsGrid.innerHTML = filtered.map(p => `
    <div class="project-card card fade-in">
        <div class="img-wrap" aria-hidden="true"><div class="project-placeholder"><img src="${p.project_picture}" alt="${p.title}" /></div></div>
        <h3>${p.title}</h3>
        <div class="tech">${p.tech}</div>
        <p style="color:var(--text2);font-size:0.95rem;">${p.desc}</p>
        <div class="links"><a href="${p.github}" target="_blank">GitHub</a><a href="${p.demo}" target="_blank">Demo</a></div>
    </div>
    `).join('');
}

function renderCertificates() {
    certificatesGrid.innerHTML = certificatesData.length ? certificatesData.map(certificate => `
    <article class="certificate-card card fade-in">
        <h3>${certificate.name}</h3>
        <p class="certificate-issuer">${certificate.issuer}</p>
        ${certificate.date ? `<p class="certificate-date">${certificate.date}</p>` : ''}
        ${certificate.link !== '#' ? `<a href="${certificate.link}" target="_blank" rel="noopener">مشاهده گواهینامه</a>` : ''}
    </article>
    `).join('') : '<p class="empty-state">هنوز گواهینامه‌ای ثبت نشده است.</p>';
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
contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const subject = document.getElementById('subject').value.trim();
    const message = document.getElementById('message').value.trim();
    if (!name || !email || !subject || !message) {
    formMessage.textContent = 'لطفاً تمام فیلدها را پر کنید.';
    formMessage.style.color = 'red';
    return;
    }
    if (!email.includes('@')) {
    formMessage.textContent = 'ایمیل معتبر وارد کنید.';
    formMessage.style.color = 'red';
    return;
    }
    formMessage.textContent = '✅ پیام شما با موفقیت ارسال شد! (شبیه‌سازی)';
    formMessage.style.color = 'green';
    contactForm.reset();
    // In production: integrate with backend API
    // fetch('/api/contact', { method: 'POST', body: JSON.stringify({name, email, subject, message}) })
});

// ---------- THEME EVENTS ----------
themeToggle.addEventListener('click', () => setTheme(currentTheme === 'dark' ? 'light' : 'dark'));

// ---------- INIT ----------
function init() {
    setTheme(currentTheme);
    renderFilterBtns();
    renderSkills();
    renderExperience();
    renderProjects();
    renderCertificates();
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