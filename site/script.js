const examples = {
  survey: {
    prompt: 'Inspect this repository and explain what is true before we decide what to change.',
    skill: 'context-survey'
  },
  build: {
    prompt: 'Implement the approved task, keep the scope narrow, and prove the result.',
    skill: 'implementation'
  },
  review: {
    prompt: 'Review this branch for correctness, regressions, and missing tests.',
    skill: 'change-review'
  },
  ship: {
    prompt: 'Package this completed work and prepare a verified release handoff.',
    skill: 'shipping'
  }
};

const installs = {
  codex: {
    command: `codex plugin marketplace add static-var/Keystone --ref main
codex plugin add keystone --marketplace keystone`,
    note: 'Add the static-var/Keystone marketplace, then install the plugin.'
  },
  claude: {
    command: `/plugin marketplace add static-var/Keystone
/plugin install keystone@keystone`,
    note: 'Add static-var/Keystone as a Claude Code marketplace, then install the plugin.'
  },
  pi: {
    command: 'pi install npm:@static-var/keystone',
    note: 'Installs the Pi extension and all nine discoverable skills.'
  }
};

document.addEventListener('DOMContentLoaded', () => {
  const header = document.querySelector('[data-header]');
  const prompt = document.querySelector('[data-prompt]');
  const skill = document.querySelector('[data-skill]');
  const themeToggle = document.querySelector('[data-theme-toggle]');
  const themeColor = document.querySelector('meta[name="theme-color"]');
  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');

  const savedTheme = () => {
    try { return localStorage.getItem('keystone-theme'); } catch { return null; }
  };

  const applyTheme = (theme, persist = false) => {
    document.documentElement.dataset.theme = theme;
    themeToggle?.setAttribute('aria-pressed', String(theme === 'dark'));
    themeToggle?.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
    themeColor?.setAttribute('content', theme === 'dark' ? '#0f121b' : '#f7f8fa');
    if (persist) {
      try { localStorage.setItem('keystone-theme', theme); } catch { /* Current page still updates. */ }
    }
  };

  applyTheme(document.documentElement.dataset.theme || (systemTheme.matches ? 'dark' : 'light'));

  themeToggle?.addEventListener('click', () => {
    applyTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark', true);
  });

  systemTheme.addEventListener('change', (event) => {
    if (!savedTheme()) applyTheme(event.matches ? 'dark' : 'light');
  });

  window.addEventListener('scroll', () => {
    header?.classList.toggle('scrolled', window.scrollY > 8);
  }, { passive: true });

  document.querySelectorAll('[data-example]').forEach((button) => {
    button.addEventListener('click', () => {
      const example = examples[button.dataset.example];
      if (!example) return;
      document.querySelectorAll('[data-example]').forEach((item) => item.classList.remove('active'));
      button.classList.add('active');
      prompt.textContent = example.prompt;
      skill.textContent = example.skill;
    });
  });

  const command = document.querySelector('[data-command]');
  const note = document.querySelector('[data-install-note]');

  document.querySelectorAll('[data-install]').forEach((button) => {
    button.addEventListener('click', () => {
      const install = installs[button.dataset.install];
      if (!install) return;
      document.querySelectorAll('[data-install]').forEach((item) => {
        item.classList.remove('active');
        item.setAttribute('aria-pressed', 'false');
      });
      button.classList.add('active');
      button.setAttribute('aria-pressed', 'true');
      command.textContent = install.command;
      note.textContent = install.note;
    });
  });

  const copyButton = document.querySelector('[data-copy]');
  copyButton?.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(command.textContent);
      copyButton.textContent = 'Copied';
      setTimeout(() => { copyButton.textContent = 'Copy'; }, 1400);
    } catch {
      copyButton.textContent = 'Select text';
    }
  });

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const revealTargets = document.querySelectorAll('.argument, .workflow-heading, .workflow-rail, .skills-copy, .skill-list, .principles, .install');
  revealTargets.forEach((target) => target.setAttribute('data-reveal', ''));

  if (reducedMotion || !('IntersectionObserver' in window)) {
    revealTargets.forEach((target) => target.classList.add('visible'));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -55px' });

  revealTargets.forEach((target) => observer.observe(target));
});
