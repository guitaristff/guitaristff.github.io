"""Check phone floating windows locally or with --url https://guitaristff.github.io/."""
import argparse
from functools import partial
from http.server import ThreadingHTTPServer
import json
import threading
from preview_check import SITE, OUT, QuietHandler, check, overflow, sync_playwright


def run(base):
    errors = []
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe", headless=True)
        for width, height in [(320, 568), (390, 844), (640, 900), (844, 390)]:
            context = browser.new_context(viewport={"width": width, "height": height}, is_mobile=True, has_touch=True)
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(base, wait_until="networkidle")
            initial = {}
            for name in ("ride", "music"):
                bounds = page.locator(f"#{name}-panel").bounding_box()
                check(bounds is not None and bounds["y"] > 70 and bounds["y"] + bounds["height"] <= height,
                      f"{width}px: {name} content is directly visible on the first screen")
                check(bounds["height"] <= 220, f"{width}px: {name} window remains compact")
                initial[name] = bounds
            scene_bounds = page.locator("#tracking-scene").bounding_box()
            check(scene_bounds["width"] >= 130 and scene_bounds["height"] >= 80,
                  f"{width}px: the full animation is visible without opening a thumbnail")
            check(page.locator("#music-toggle").evaluate("e => { const r = e.getBoundingClientRect(); return e.contains(document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2)); }"),
                  f"{width}px: the real play button is immediately accessible")
            check(not overflow(page), f"{width}px: no horizontal overflow")
            check(page.locator("#tracking-scene").count() == 1 and page.locator("audio").count() == 1,
                  f"{width}px: no duplicate scene or audio player")
            position = page.locator("#motorcycle").get_attribute("transform")
            page.wait_for_timeout(300)
            check(page.locator("#motorcycle").get_attribute("transform") != position,
                  f"{width}px: animation runs before any click")
            page.screenshot(path=str(OUT / f"direct-{width}-zh.png"))
            page.locator("#language-toggle").click()
            check(page.locator("#ride-title").inner_text() == "On the road", f"{width}px: visible windows translate")
            check(page.locator(".life-sidebar .panel-heading h2").evaluate_all(
                "els => els.every(e => e.scrollWidth <= e.clientWidth + 1)"), f"{width}px: English window titles fit")
            page.screenshot(path=str(OUT / f"direct-{width}-en.png"))
            page.evaluate("window.scrollTo({top: 350, behavior: 'instant'})")
            page.wait_for_timeout(150)
            check(page.evaluate("scrollY") == 350, f"{width}px: the main document scrolls normally")
            check(all(abs(page.locator(f'#{name}-panel').bounding_box()['y'] - initial[name]['y']) < 1
                      for name in ("ride", "music")), f"{width}px: both windows remain visible while reading")
            page.locator("#ride-panel .companion-close").click()
            check(not page.locator("#ride-panel").is_visible() and page.locator("#music-panel").is_visible(),
                  f"{width}px: riding minimizes independently")
            check(page.locator("#companion-ride").is_visible(), f"{width}px: a small button can restore riding")
            page.wait_for_timeout(100)
            position = page.locator("#motorcycle").get_attribute("transform")
            page.wait_for_timeout(200)
            check(page.locator("#motorcycle").get_attribute("transform") == position,
                  f"{width}px: minimized animation stops rendering")
            page.locator("#music-panel .companion-close").click()
            check(not page.locator("#music-panel").is_visible() and page.locator("#companion-music").is_visible(),
                  f"{width}px: music also minimizes independently")
            page.screenshot(path=str(OUT / f"direct-{width}-minimized.png"))
            page.reload(wait_until="networkidle")
            check(page.locator("#companion-ride").is_visible() and page.locator("#companion-music").is_visible(),
                  f"{width}px: same-tab reload respects manual minimization")
            page.locator("#companion-ride").click()
            check(page.locator("#ride-panel").is_visible() and not page.locator("#music-panel").is_visible(),
                  f"{width}px: riding restores without forcing music open")
            page.locator("#companion-music").click()
            check(page.locator("#music-panel").is_visible(), f"{width}px: music restores independently")
            results.append({"width": width, "height": height, "default_windows_visible": True})
            context.close()

        context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(base, wait_until="networkidle")
        # The first interaction is the actual play button, with no launcher click.
        page.locator("#music-toggle").click()
        page.wait_for_function("document.querySelector('audio').currentTime > .3", timeout=20000)
        check(page.locator("audio").evaluate("a => !a.paused && a.duration > 308"),
              "One click from the initial page plays the real NetEase song")
        page.locator("#music-panel .companion-close").click()
        time_before = page.locator("audio").evaluate("a => a.currentTime")
        page.wait_for_timeout(500)
        check(page.locator("audio").evaluate("a => !a.paused && a.currentTime") > time_before,
              "Minimizing the music window does not interrupt playback")
        check(page.locator("#companion-music .companion-playing").is_visible(), "Minimized music indicates ongoing playback")
        page.locator("#ride-panel .companion-close").click()
        check(page.locator("audio").evaluate("a => !a.paused"), "Music continues when both windows are minimized")
        page.locator("#companion-music").click()
        page.locator("#music-toggle").click()
        check(page.locator("audio").evaluate("a => a.paused"), "Restored music controls can pause playback")
        page.locator("#music-panel .companion-close").click()
        page.locator("#menu-toggle").click()
        page.locator('.main-nav a[href="#off-duty"]').click()
        check(page.locator("#ride-panel").is_visible() and page.locator("#music-panel").is_visible(),
              "Phone navigation restores both windows")
        check(page.evaluate("scrollY") == 0, "Restoring windows preserves the reading position")
        page.locator('[data-platform="0"]').click()
        check(page.locator("#platform-dialog").is_visible(), "Real-platform gallery opens above the floating windows")
        page.keyboard.press("Escape")
        check(not page.locator("#platform-dialog").is_visible() and page.locator("#ride-panel").is_visible(),
              "Closing the gallery leaves the floating windows intact")
        for width in [768, 900, 1440]:
            page.set_viewport_size({"width": width, "height": 1000})
            check(not page.locator("#mobile-companions").is_visible(), f"{width}px: floating controls stay off desktop/tablet")
            check(page.locator("#ride-panel").is_visible() and page.locator("#music-panel").is_visible(),
                  f"{width}px: original sidebar cards remain visible")
            check(page.locator("#off-duty").evaluate("e => getComputedStyle(e).position !== 'fixed'"),
                  f"{width}px: desktop sidebar keeps its original positioning")
            check(not overflow(page), f"{width}px: original responsive layout fits")
        context.close()
        reduced = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
        page = reduced.new_page()
        page.goto(base, wait_until="networkidle")
        check(page.locator("#motion-toggle").get_attribute("aria-pressed") == "true", "Visible phone animation respects reduced motion")
        reduced.close()
        fallback = browser.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False)
        page = fallback.new_page()
        page.goto(base, wait_until="networkidle")
        check(page.locator("#ride-panel").is_visible() and page.locator("#music-panel").is_visible(),
              "Both cards remain in the document when JavaScript is disabled")
        fallback.close()
        browser.close()
    check(not errors, f"No JavaScript errors: {errors}")
    (OUT / "mobile-check-result.json").write_text(json.dumps({"passed": True, "url": base, "viewports": results,
        "one_click_audio": True, "javascript_errors": errors}, indent=2), encoding="utf-8")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    args = parser.parse_args()
    if args.url:
        run(args.url)
    else:
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(SITE)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            run(f"http://127.0.0.1:{server.server_port}/")
        finally:
            server.shutdown()
            server.server_close()
