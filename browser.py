import time
from urllib.parse import urlparse

import jwt
from playwright.async_api import async_playwright, Page, Browser

from config import config


class BrowserController:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser: Browser | None = None
        self.page: Page | None = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        self.page.set_default_timeout(config.ACTION_TIMEOUT)

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def navigate(self, url: str) -> dict:
        await self.page.goto(url)
        return {"status": "ok", "url": self.page.url}

    async def click(self, selector: str) -> dict:
        try:
            await self.page.click(selector, timeout=config.ACTION_TIMEOUT)
            await self.page.wait_for_load_state("networkidle", timeout=5000)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def fill(self, selector: str, text: str) -> dict:
        try:
            await self.page.fill(selector, text)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def select(self, selector: str, value: str) -> dict:
        try:
            await self.page.select_option(selector, value)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def screenshot(self, path: str = "screenshot.png") -> dict:
        await self.page.screenshot(path=path)
        return {"status": "ok", "path": path}

    async def get_page_state(self) -> dict:
        url = self.page.url
        title = await self.page.title()
        html = await self._get_simplified_html()
        return {
            "url": url,
            "title": title,
            "html": html,
        }

    async def _get_simplified_html(self) -> str:
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
        return await self.page.evaluate(script)

    async def login(self) -> dict:
        """Log in by injecting a pre-authenticated JWT session cookie.

        The site uses Strava OAuth which blocks headless browsers, so we bypass
        by generating a valid JWT session cookie using credentials from config.
        """
        try:
            # Navigate to the site first
            await self.navigate(config.CRANKCASE_URL)
            await self.page.wait_for_load_state("networkidle")

            # Generate JWT token
            payload = {
                "sub": config.SESSION_USER_ID,
                "name": config.SESSION_USER_NAME,
                "exp": int(time.time()) + 60 * 60 * 24 * 7,  # 7 days
                "iat": int(time.time()),
            }
            token = jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")

            # Extract domain from URL
            parsed = urlparse(config.CRANKCASE_URL)
            domain = parsed.netloc

            # Inject session cookie
            await self.page.context.add_cookies([{
                "name": "session",
                "value": token,
                "domain": domain,
                "path": "/",
                "httpOnly": True,
                "secure": parsed.scheme == "https",
                "sameSite": "Lax",
            }])

            # Reload to apply the cookie
            await self.page.reload()
            await self.page.wait_for_load_state("networkidle")

            # Verify authentication by checking for user name or logout button
            html = await self.page.content()
            if config.SESSION_USER_NAME in html or "logout" in html.lower():
                return {"status": "ok", "url": self.page.url, "user": config.SESSION_USER_NAME}
            else:
                return {"status": "error", "message": "Cookie injection succeeded but user not authenticated"}

        except Exception as e:
            return {"status": "error", "message": str(e)}
