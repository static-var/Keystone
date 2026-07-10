import re
import subprocess
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "index.html"
SCRIPT = ROOT / "site" / "script.js"


CODEX_SETUP = "codex plugin marketplace add static-var/Keystone --ref main\ncodex plugin add keystone --marketplace keystone"
CLAUDE_SETUP = "/plugin marketplace add static-var/Keystone\n/plugin install keystone@keystone"


def run_node(source: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["node", "-e", source],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class SiteInstallBehaviorTests(unittest.TestCase):
    def test_install_commands_include_complete_marketplace_and_install_steps(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn(CODEX_SETUP, html)
        self.assertIn(CODEX_SETUP, script)
        self.assertIn(CLAUDE_SETUP, script)
        self.assertNotIn("codex plugin add keystone --marketplace keystone',", script)
        self.assertNotIn("/plugin install keystone@keystone',", script)

    def test_footer_links_public_legal_and_support_pages(self) -> None:
        html = INDEX.read_text(encoding="utf-8")

        self.assertIn('href="/privacy/"', html)
        self.assertIn('href="/terms/"', html)
        self.assertIn('href="/support/"', html)

    def test_head_theme_bootstrap_survives_blocked_local_storage(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        inline_script = re.search(r"<script>\s*([\s\S]*?)\s*</script>", html)
        self.assertIsNotNone(inline_script)

        node = f"""
        const vm = require('node:vm');
        const context = {{
          document: {{ documentElement: {{ dataset: {{}} }} }},
          localStorage: {{ getItem() {{ throw new Error('storage blocked'); }} }},
          matchMedia() {{ return {{ matches: false }}; }}
        }};
        vm.createContext(context);
        vm.runInContext({inline_script.group(1)!r}, context);
        if (context.document.documentElement.dataset.theme !== 'light') {{
          throw new Error('expected light fallback, got ' + context.document.documentElement.dataset.theme);
        }}
        """
        result = run_node(node)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_install_selector_uses_native_buttons_and_announced_output(self) -> None:
        html = INDEX.read_text(encoding="utf-8")

        self.assertRegex(html, r'<div class="install-tabs" role="group" aria-label="Installation method">')
        self.assertNotIn('role="tablist"', html)
        self.assertNotIn('role="tab"', html)
        self.assertNotIn('aria-selected', html)
        self.assertRegex(html, r'<button class="active" type="button" aria-pressed="true" data-install="codex">Codex</button>')
        self.assertRegex(html, r'<button type="button" aria-pressed="false" data-install="claude">Claude Code</button>')
        self.assertRegex(html, r'<button type="button" aria-pressed="false" data-install="pi">Pi</button>')
        self.assertRegex(html, r'<div class="command-row"[^>]*aria-live="polite"')
        self.assertRegex(html, r'<p data-install-note[^>]*aria-live="polite"')

    def test_install_selector_click_updates_pressed_state_and_copy_payload(self) -> None:
        harness = textwrap.dedent(
            f"""
            const fs = require('node:fs');
            const vm = require('node:vm');

            class ClassList {{
              constructor() {{ this.values = new Set(); }}
              add(value) {{ this.values.add(value); }}
              remove(value) {{ this.values.delete(value); }}
              toggle(value, force) {{ force ? this.add(value) : this.remove(value); }}
              contains(value) {{ return this.values.has(value); }}
            }}

            class Element {{
              constructor(dataset = {{}}) {{
                this.dataset = dataset;
                this.attributes = {{}};
                this.classList = new ClassList();
                this.textContent = '';
                this.listeners = {{}};
              }}
              setAttribute(name, value) {{ this.attributes[name] = String(value); }}
              getAttribute(name) {{ return Object.prototype.hasOwnProperty.call(this.attributes, name) ? this.attributes[name] : null; }}
              addEventListener(name, callback) {{ (this.listeners[name] ||= []).push(callback); }}
              async click() {{
                for (const callback of this.listeners.click || []) {{
                  await callback({{ target: this }});
                }}
              }}
            }}

            const installButtons = [new Element({{ install: 'codex' }}), new Element({{ install: 'claude' }}), new Element({{ install: 'pi' }})];
            installButtons[0].classList.add('active');
            installButtons[0].setAttribute('aria-pressed', 'true');
            installButtons[1].setAttribute('aria-pressed', 'false');
            installButtons[2].setAttribute('aria-pressed', 'false');
            const command = new Element();
            command.textContent = {CODEX_SETUP!r};
            const note = new Element();
            const copy = new Element();
            const prompt = new Element();
            const skill = new Element();
            const themeToggle = new Element();
            const themeColor = new Element();
            const header = new Element();
            const documentElement = new Element();
            documentElement.dataset = {{ theme: 'light' }};
            const domContentLoaded = [];

            const document = {{
              documentElement,
              addEventListener(name, callback) {{ if (name === 'DOMContentLoaded') domContentLoaded.push(callback); }},
              querySelector(selector) {{
                return {{
                  '[data-header]': header,
                  '[data-prompt]': prompt,
                  '[data-skill]': skill,
                  '[data-theme-toggle]': themeToggle,
                  'meta[name="theme-color"]': themeColor,
                  '[data-command]': command,
                  '[data-install-note]': note,
                  '[data-copy]': copy,
                }}[selector] || null;
              }},
              querySelectorAll(selector) {{
                if (selector === '[data-install]') return installButtons;
                if (selector === '[data-example]') return [];
                return [];
              }}
            }};

            let copiedText = null;
            const window = {{
              scrollY: 0,
              matchMedia(query) {{ return {{ matches: query.includes('reduce'), addEventListener() {{}} }}; }},
              addEventListener() {{}},
            }};
            const context = {{
              document,
              window,
              localStorage: {{ getItem() {{ return null; }}, setItem() {{}} }},
              navigator: {{ clipboard: {{ async writeText(text) {{ copiedText = text; }} }} }},
              setTimeout(callback) {{ callback(); }},
              IntersectionObserver: undefined,
            }};
            vm.createContext(context);
            vm.runInContext(fs.readFileSync({str(SCRIPT)!r}, 'utf8'), context);

            (async () => {{
              for (const callback of domContentLoaded) callback();
              await installButtons[1].click();
              if (command.textContent !== {CLAUDE_SETUP!r}) throw new Error('Claude command incomplete: ' + command.textContent);
              if (installButtons[0].getAttribute('aria-pressed') !== 'false') throw new Error('Codex button still pressed');
              if (installButtons[1].getAttribute('aria-pressed') !== 'true') throw new Error('Claude button not pressed');
              await copy.click();
              if (copiedText !== {CLAUDE_SETUP!r}) throw new Error('Copied incomplete setup: ' + copiedText);
            }})().catch((error) => {{ console.error(error.stack || error.message); process.exit(1); }});
            """
        )
        result = run_node(harness)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
