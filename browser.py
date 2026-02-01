from playwright.sync_api import sync_playwright, Page, Browser
from config import config
import re


class BrowserController:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser: Browser | None = None
        self.page: Page | None = None

    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(config.ACTION_TIMEOUT)

    def stop(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def navigate(self, url: str) -> dict:
        self.page.goto(url)
        return {"status": "ok", "url": self.page.url}

    def click(self, selector: str) -> dict:
        try:
            self.page.click(selector, timeout=config.ACTION_TIMEOUT)
            self.page.wait_for_load_state("networkidle", timeout=5000)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def fill(self, selector: str, text: str) -> dict:
        try:
            self.page.fill(selector, text)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def select(self, selector: str, value: str) -> dict:
        try:
            self.page.select_option(selector, value)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def screenshot(self, path: str = "screenshot.png") -> dict:
        self.page.screenshot(path=path)
        return {"status": "ok", "path": path}

    def get_page_state(self) -> dict:
        url = self.page.url
        title = self.page.title()
        html = self._get_simplified_html()
        return {
            "url": url,
            "title": title,
            "html": html,
        }

    def _get_simplified_html(self) -> str:
        """Extract simplified HTML with interactive elements and text."""
        script = """
        () => {
            const elements = [];

            // Get all interactive and content elements
            const selectors = 'a, button, input, select, textarea, form, h1, h2, h3, h4, label, [role="button"], [onclick]';
            document.querySelectorAll(selectors).forEach((el, idx) => {
                const tag = el.tagName.toLowerCase();
                const text = el.innerText?.slice(0, 100) || '';
                const attrs = [];

                if (el.id) attrs.push(`id="${el.id}"`);
                if (el.name) attrs.push(`name="${el.name}"`);
                if (el.className) attrs.push(`class="${el.className}"`);
                if (el.type) attrs.push(`type="${el.type}"`);
                if (el.href) attrs.push(`href="${el.href}"`);
                if (el.placeholder) attrs.push(`placeholder="${el.placeholder}"`);
                if (el.value && tag === 'input') attrs.push(`value="${el.value}"`);

                const attrStr = attrs.length ? ' ' + attrs.join(' ') : '';
                elements.push(`<${tag}${attrStr}>${text.trim()}</${tag}>`);
            });

            return elements.join('\\n');
        }
        """
        return self.page.evaluate(script)

    def login(self, username: str, password: str) -> dict:
        """Attempt to log in - this is site-specific and may need adjustment."""
        try:
            # Navigate to the site first
            self.navigate(config.CRANKCASE_URL)

            # Look for common login patterns
            # This may need customization based on CrankCase's actual login flow
            self.page.wait_for_load_state("networkidle")

            # Try to find and fill login form
            if self.page.locator('input[type="email"], input[name="email"]').count() > 0:
                self.page.fill('input[type="email"], input[name="email"]', username)
            if self.page.locator('input[type="password"]').count() > 0:
                self.page.fill('input[type="password"]', password)

            # Click submit button
            if self.page.locator('button[type="submit"]').count() > 0:
                self.page.click('button[type="submit"]')
                self.page.wait_for_load_state("networkidle")

            return {"status": "ok", "url": self.page.url}
        except Exception as e:
            return {"status": "error", "message": str(e)}
