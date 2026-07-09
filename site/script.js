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
  skills: {
    command: 'npx skills add static-var/keystone',
    note: 'Works with OpenCode, GitHub Copilot, VS Code, and other Agent Skills hosts.'
  },
  codex: {
    command: 'codex plugin add keystone --marketplace keystone',
    note: 'Add the static-var/Keystone marketplace first, then install the plugin.'
  },
  claude: {
    command: '/plugin install keystone@keystone',
    note: 'Add static-var/Keystone as a Claude Code marketplace first.'
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
        item.setAttribute('aria-selected', 'false');
      });
      button.classList.add('active');
      button.setAttribute('aria-selected', 'true');
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
