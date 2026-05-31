import logging
from typing import Optional

logger = logging.getLogger(__name__)


class WebFetcher:
    async def fetch_page(self, url: str) -> dict:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return {"error": "Playwright not installed", "title": "", "content": "", "url": url}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)

                title = await page.title()

                content = await page.evaluate("""
                    () => {
                        const selectors = ['article', 'main', '.job-detail', '.jd-content', '.job-description', '.post-content', '#job-detail'];
                        for (const sel of selectors) {
                            const el = document.querySelector(sel);
                            if (el && el.textContent.trim().length > 200) {
                                return el.textContent.trim();
                            }
                        }
                        const body = document.body;
                        if (body) {
                            // Remove nav, header, footer
                            const exclude = body.querySelectorAll('nav, header, footer, script, style, .nav, .header, .footer, .sidebar, .comment');
                            exclude.forEach(e => e.remove());
                            return body.textContent.trim();
                        }
                        return '';
                    }
                """)

                await browser.close()

                content = self._clean_text(content)

                return {
                    "title": title,
                    "content": content[:8000],
                    "url": url,
                }
        except Exception as e:
            logger.warning(f"Web fetch failed for {url}: {e}")
            return {"error": str(e), "title": "", "content": "", "url": url}

    def _clean_text(self, text: str) -> str:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        return "\n".join(lines)
