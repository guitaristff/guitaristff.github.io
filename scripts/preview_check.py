"""Acceptance checks for the bilingual academic profile using local Chrome."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from zipfile import ZipFile
import json
import mimetypes
import sys
import threading
from urllib.parse import urlsplit
from build import PUBLIC_FILES

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
OUT = ROOT / ".preview"
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / ".tools"))
from playwright.sync_api import sync_playwright

EMAIL = "zhaofeng_du@bit.edu.cn"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print(f"PASS: {message}", flush=True)


def overflow(page):
    return page.evaluate("document.documentElement.scrollWidth > innerWidth + 1")


def check_audio_recovery(browser, base):
    audio_url = "https://music.163.com/song/media/outer/url*"
    context = browser.new_context(viewport={"width": 1440, "height": 1000})
    context.route(audio_url, lambda route: route.abort("failed"))
    page = context.new_page()
    page.goto(base + "?lang=zh", wait_until="networkidle")
    page.locator("#music-toggle").click()
    page.wait_for_function("document.querySelector('#audio-status').classList.contains('music-error')")
    check(page.locator("#music-label").inner_text() == "重新播放", "Failed source offers a retry")
    check(page.locator("#music-toggle").is_enabled(), "Failed source does not disable the player")
    check(page.locator("#music-toggle").get_attribute("aria-pressed") == "false", "Failed source is not shown as playing")
    check(not page.locator("#music-progress").is_enabled(), "Failed source disables seeking")
    page.locator("#language-toggle").click()
    check("could not load" in page.locator("#audio-status").inner_text(), "Persistent source error translates to English")
    page.set_viewport_size({"width": 390, "height": 844})
    check(not overflow(page), "English playback error fits on mobile")
    page.locator(".music-panel").screenshot(path=str(OUT / "music-error-en.png"))
    context.unroute(audio_url)
    page.locator("#music-toggle").click()
    page.wait_for_function("document.querySelector('audio').currentTime > .2", timeout=15000)
    check(page.locator("#music-player").evaluate("a => !a.paused && !a.error"), "Retry reloads a failed source and plays the real NetEase track")
    check(page.locator("#audio-status").get_attribute("class") == "sr-only", "Successful retry clears the error message")
    context.close()

    context = browser.new_context(viewport={"width": 1440, "height": 1000})
    pending = []
    context.route(audio_url, lambda route: pending.append(route))
    page = context.new_page()
    page.goto(base + "?lang=zh", wait_until="networkidle")
    page.locator("#music-toggle").click()
    check(page.locator("#music-toggle").get_attribute("aria-busy") == "true", "Pending track shows its loading state")
    page.locator("#music-toggle").click()
    page.wait_for_timeout(150)
    check(page.locator("#music-player").evaluate("a => a.paused && !a.getAttribute('src')"), "Cancel aborts the pending media request")
    check(page.locator("#audio-status").get_attribute("class") == "sr-only", "Intentional cancellation does not show a playback failure")
    page.locator("#music-toggle").click()
    page.wait_for_function("document.querySelector('#audio-status').classList.contains('music-error')", timeout=14500)
    check("加载超时" in page.locator("#audio-status").inner_text(), "A stalled source times out with an actionable message")
    check(page.locator("#music-toggle").is_enabled(), "Timeout leaves retry available")
    check(page.locator("#music-player").evaluate("a => a.paused && !a.getAttribute('src')"), "Timeout stops and clears the stalled request")
    for route in pending:
        route.abort("aborted")
    context.unroute(audio_url)
    context.close()

    context = browser.new_context(viewport={"width": 1440, "height": 1000})
    context.add_init_script("HTMLMediaElement.prototype.play = function () { return Promise.reject(new DOMException('Playback blocked', 'NotAllowedError')); };")
    page = context.new_page()
    page.goto(base + "?lang=zh", wait_until="networkidle")
    page.locator("#music-toggle").click()
    page.wait_for_function("document.querySelector('#audio-status').classList.contains('music-error')")
    check("浏览器限制" in page.locator("#audio-status").inner_text(), "Browser restrictions are distinguished from source failures")
    context.close()


def check_https_audio(browser):
    context = browser.new_context(viewport={"width": 1440, "height": 1000})
    def serve(route):
        name = urlsplit(route.request.url).path.lstrip("/") or "index.html"
        if name in PUBLIC_FILES:
            route.fulfill(path=str(SITE / name), content_type=mimetypes.guess_type(name)[0] or "application/octet-stream")
        else:
            route.fulfill(status=404, body="Not found")
    context.route("https://profile.test/**", serve)
    page = context.new_page()
    audio_responses = []
    page.on("response", lambda r: audio_responses.append(r.url) if (urlsplit(r.url).hostname or "").endswith("music.126.net") else None)
    page.goto("https://profile.test/", wait_until="networkidle")
    check(page.evaluate("isSecureContext"), "Music is also checked in an HTTPS context")
    page.locator("#music-toggle").click()
    page.wait_for_function("document.querySelector('audio').currentTime > .2", timeout=15000)
    check(page.locator("#music-player").evaluate("a => !a.paused && !a.error"), "NetEase audio plays within the HTTPS page")
    check(audio_responses and all(url.startswith("https://") for url in audio_responses), "NetEase CDN redirects are upgraded to HTTPS")
    page.locator(".music-panel").screenshot(path=str(OUT / "netease-playing.png"))
    context.close()


def run():
    if not (SITE / "index.html").is_file():
        raise FileNotFoundError("Run python scripts/build.py first.")
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(SITE)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"
    errors = []
    missing = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                headless=True,
            )
            context = browser.new_context(viewport={"width": 1440, "height": 1000})
            context.grant_permissions(["clipboard-read", "clipboard-write"])
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("response", lambda response: missing.append(response.url) if response.status >= 400 else None)
            page.goto(base, wait_until="networkidle")
            check(page.locator("html").get_attribute("lang") == "zh-CN", "Chinese is the initial language")
            check(page.locator(".research-item").count() == 2, "Research contains exactly FBSR and RAFT")
            check(page.locator(".research-item").evaluate_all("items => items.map(item => item.id)") == ["fbsr", "raft"], "Project names are correct")
            check(page.locator("[data-project], [data-filter], #project-dialog").count() == 0, "Detailed research expansion has been removed")
            check(page.locator('a[href*="cv."], a[download], a[href$=".pdf"]').count() == 0, "No CV or PDF download links")
            check(page.locator('a[href^="mailto:"]').evaluate_all("links => links.every(a => a.getAttribute('href') === 'mailto:zhaofeng_du@bit.edu.cn')"), "Every email link uses the BIT address")
            check(page.locator(".profile-avatar").get_attribute("src") == "assets/github-avatar.png", "Personal portrait remains the GitHub avatar")
            check(page.locator("[data-mode]").count() == 2, "Animation offers two modes")
            check(page.locator('[data-mode="occlusion"], #occlusion-cloud').count() == 0, "Occlusion option and overlay are removed")
            check(page.locator("#motorcycle image").get_attribute("href") == "assets/bmw-r-ninet.svg", "Animated motorcycle uses the BMW R nineT illustration")
            check(not overflow(page), "Desktop Chinese has no horizontal overflow")
            check(page.locator("#music-player").evaluate("a => a.paused && a.currentTime === 0"), "Music does not autoplay")
            page.screenshot(path=str(OUT / "desktop-zh.png"), full_page=True)
            page.screenshot(path=str(OUT / "desktop-hero.png"))

            for index in range(3):
                image = page.locator(".platform-photo img").nth(index)
                image.scroll_into_view_if_needed()
                page.wait_for_function("(index) => { const img = document.querySelectorAll('.platform-photo img')[index]; return img.complete && img.naturalWidth > 0; }", arg=index)
            check(page.locator(".platform-photo").count() == 3, "Three real UAV photographs load")
            page.locator('[data-platform="0"]').click()
            check(page.locator("#platform-dialog").is_visible(), "Platform photo opens in a large viewer")
            check(page.locator("#platform-count").inner_text() == "1 / 3", "Viewer starts at the selected photograph")
            page.locator("#platform-next").click()
            check(page.locator("#platform-large-image").get_attribute("src").endswith("02.png"), "Next moves to the second platform")
            page.keyboard.press("ArrowRight")
            check(page.locator("#platform-large-image").get_attribute("src").endswith("03.png"), "Keyboard navigation moves to the third platform")
            page.locator("#platform-next").click()
            check(page.locator("#platform-count").inner_text() == "1 / 3", "Photo navigation wraps correctly")
            page.keyboard.press("Escape")
            check(not page.locator("#platform-dialog").is_visible(), "Escape closes the photo viewer")
            check(page.locator('[data-platform="0"]').evaluate("e => e === document.activeElement"), "Closing restores focus to the photograph")

            page.locator("#language-toggle").click()
            check(page.locator("html").get_attribute("lang") == "en", "Language switches to English")
            check(page.locator("#research-title").inner_text() == "Selected Research", "Research title translates")
            check(page.locator("#platforms-title").inner_text() == "UAV Platforms", "Platform title translates")
            check(page.locator("#music-label").inner_text() == "Play 四相", "Music control translates")
            page.reload(wait_until="networkidle")
            check(page.locator("html").get_attribute("lang") == "en", "Language preference persists")
            check(not overflow(page), "Desktop English has no horizontal overflow")
            page.screenshot(path=str(OUT / "desktop-en.png"), full_page=True)
            page.locator('[data-mode="cooperation"]').click()
            check(page.locator("#uav-second").get_attribute("visibility") == "visible", "Cooperation shows two UAVs")
            page.locator('[data-mode="tracking"]').click()
            check(page.locator("#uav-second").get_attribute("visibility") == "hidden", "Tracking restores the single-UAV view")
            page.locator("#motion-toggle").click()
            position = page.locator("#motorcycle").get_attribute("transform")
            page.wait_for_timeout(250)
            check(page.locator("#motorcycle").get_attribute("transform") == position, "Pause freezes the motorcycle")
            page.locator("#motion-toggle").click()
            page.wait_for_timeout(300)
            check(page.locator("#motorcycle").get_attribute("transform") != position, "Resume animates the motorcycle")

            page.locator("#music-toggle").click()
            page.wait_for_function("document.querySelector('audio').currentTime > .2", timeout=25000)
            check(page.locator("#music-player").evaluate("a => !a.paused && a.readyState >= 3"), "NetEase song plays directly in the page")
            duration = page.locator("#music-player").evaluate("a => a.duration")
            check(308 < duration < 310, "The song duration is about 5 minutes 9 seconds")
            page.locator("#music-toggle").click()
            check(page.locator("#music-player").evaluate("a => a.paused"), "Music pauses on request")
            page.locator("#music-progress").evaluate("e => { e.value = 50; e.dispatchEvent(new Event('input', {bubbles:true})); }")
            check(page.locator("#music-player").evaluate("a => Math.abs(a.currentTime - a.duration / 2) < .5"), "Song progress is seekable")
            check(page.locator(".music-source a").get_attribute("href") == "https://music.163.com/song?id=439121264", "External listening opens the NetEase song page")
            page.locator("#copy-email").click()
            check(page.evaluate("navigator.clipboard.readText()") == EMAIL, "Copy email uses the BIT address")
            page.locator(".more-honors summary").click()
            check(page.locator(".more-honors").get_attribute("open") is not None, "Additional honours expand")

            for width in [320, 375, 390, 640, 768, 900, 1024, 1280]:
                page.set_viewport_size({"width": width, "height": 844})
                for lang in ["zh", "en"]:
                    page.goto(f"{base}/index.html?lang={lang}", wait_until="networkidle")
                    check(not overflow(page), f"Responsive layout fits {width}px, {lang}")
                    if width == 390:
                        page.screenshot(path=str(OUT / f"mobile-{lang}.png"), full_page=True)
                        page.screenshot(path=str(OUT / f"mobile-hero-{lang}.png"))
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(base + "/index.html?lang=zh", wait_until="networkidle")
            page.locator("#menu-toggle").click()
            check(page.locator("#main-nav").is_visible(), "Mobile menu opens")
            page.locator('.main-nav a[href="#platforms"]').click()
            check(page.locator("#menu-toggle").get_attribute("aria-expanded") == "false", "Mobile navigation closes after a selection")
            page.locator('[data-platform="1"]').click()
            check(not overflow(page), "Mobile photo viewer fits the viewport")
            check(page.locator("#platform-count").inner_text() == "2 / 3", "Mobile viewer opens the selected photo")
            page.locator("#platform-close").click()

            reduced = browser.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
            reduced_page = reduced.new_page()
            reduced_page.goto(base, wait_until="networkidle")
            check(reduced_page.locator("#motion-toggle").get_attribute("aria-pressed") == "true", "Reduced-motion preference pauses the animation")
            reduced.close()
            local = context.new_page()
            local.on("pageerror", lambda error: errors.append(str(error)))
            local.goto((SITE / "index.html").as_uri(), wait_until="load")
            local.locator("#language-toggle").click()
            check(local.locator(".research-item").count() == 2, "Local file entry works")
            check(local.locator(".profile-avatar").evaluate("e => e.complete && e.naturalWidth > 0"), "Local file entry loads the GitHub photo")
            check(context.request.get(base + "/cv.html").status == 404, "Removed CV page is not publicly served")
            check(context.request.get(base + "/cv.css").status == 404, "Removed CV styles are not publicly served")
            check(not errors, f"No JavaScript errors: {errors}")
            check(not missing, f"No failed page resources: {missing}")
            check_audio_recovery(browser, base)
            check_https_audio(browser)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

    with ZipFile(ROOT / "zhaofeng-du-website.zip") as archive:
        names = archive.namelist()
        check(len(names) == 13, "Publish archive contains exactly 13 public files")
        check(not any("cv." in name.lower() or name.lower().endswith(".pdf") for name in names), "Publish archive contains no CV or PDF")
    check(not any(p.suffix == ".pdf" or p.name.startswith("cv.") for p in SITE.rglob("*")), "Public directory has no residual CV files")
    report = {"passed": True, "javascript_errors": errors, "failed_resources": missing, "audio_duration_seconds": duration, "audio_provider": "NetEase Music", "https_audio": True, "audio_failure_recovery": True, "projects": ["FBSR", "RAFT"], "platform_photos": 3, "email": EMAIL}
    (OUT / "check-result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Browser acceptance checks complete.", flush=True)


if __name__ == "__main__":
    run()
