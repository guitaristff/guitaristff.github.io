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
            dock = page.locator("#companion-dock")
            bounds = dock.bounding_box()
            check(bounds is not None and bounds["y"] > height * .7 and bounds["y"] + bounds["height"] <= height,
                  f"{width}px: both companions are visible on the first screen")
            check(bounds["height"] < 85, f"{width}px: the initial floating bar stays compact")
            check(not overflow(page), f"{width}px: no horizontal overflow")
            check(page.locator("#companion-ride-preview #tracking-scene").count() == 1,
                  f"{width}px: the original live scene appears in the preview")
            check(page.locator("#tracking-scene").count() == 1 and page.locator("audio").count() == 1,
                  f"{width}px: only one scene and one audio player exist")
            check(page.locator("audio").evaluate("a => a.paused && a.currentTime === 0"),
                  f"{width}px: showing the floating bar does not autoplay music")
            position = page.locator("#motorcycle").get_attribute("transform")
            page.wait_for_timeout(350)
            check(page.locator("#motorcycle").get_attribute("transform") != position,
                  f"{width}px: the miniature riding scene animates")
            page.screenshot(path=str(OUT / f"floating-{width}-zh.png"))
            page.locator("#language-toggle").click()
            check("On the road" in page.locator("#companion-ride").inner_text(), f"{width}px: floating labels translate")
            check(page.locator("#companion-restore").get_attribute("aria-label").startswith("Show"),
                  f"{width}px: hidden controls also translate")
            check(page.locator(".companion-caption strong").evaluate_all(
                "els => els.every(e => e.scrollWidth <= e.clientWidth + 1)"), f"{width}px: both titles fit in English")
            page.screenshot(path=str(OUT / f"floating-{width}-en.png"))
            page.locator("#companion-ride").click()
            check(page.locator("#ride-panel").is_visible() and not page.locator("#music-panel").is_visible(),
                  f"{width}px: opening riding shows one window")
            check(page.locator("#ride-panel #tracking-scene").count() == 1,
                  f"{width}px: the same scene moves into the full window")
            page.locator('[data-mode="cooperation"]').click()
            check(page.locator("#uav-second").get_attribute("visibility") == "visible", f"{width}px: scene controls work")
            page.screenshot(path=str(OUT / f"floating-{width}-ride.png"))
            page.locator("#companion-music").click()
            check(page.locator("#music-panel").is_visible() and not page.locator("#ride-panel").is_visible(),
                  f"{width}px: switching windows keeps the main page available")
            page.screenshot(path=str(OUT / f"floating-{width}-music.png"))
            page.keyboard.press("Escape")
            check(not page.locator("#music-panel").is_visible(), f"{width}px: Escape closes the window")
            check(page.locator("#companion-music").evaluate("e => e === document.activeElement"),
                  f"{width}px: keyboard focus returns to the launcher")
            page.locator("#companion-ride").click()
            page.evaluate("window.scrollTo({top: 250, behavior: 'instant'})")
            page.wait_for_timeout(150)
            check(not page.locator("#ride-panel").is_visible() and dock.is_visible(),
                  f"{width}px: reading scroll closes the expanded card and keeps the small bar")
            page.locator("#companion-minimize").click()
            check(not dock.is_visible() and page.locator("#companion-restore").is_visible(),
                  f"{width}px: the whole bar folds into a small button")
            page.wait_for_timeout(150)
            position = page.locator("#motorcycle").get_attribute("transform")
            page.wait_for_timeout(250)
            check(page.locator("#motorcycle").get_attribute("transform") == position,
                  f"{width}px: the hidden scene stops rendering")
            page.screenshot(path=str(OUT / f"floating-{width}-minimized.png"))
            page.reload(wait_until="networkidle")
            check(page.locator("#companion-restore").is_visible(), f"{width}px: minimization survives a same-tab reload")
            page.locator("#companion-restore").click()
            check(dock.is_visible(), f"{width}px: the bar can be restored")
            results.append({"width": width, "height": height, "passed": True})
            context.close()

        context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(base, wait_until="networkidle")
        page.locator("#menu-toggle").click()
        page.locator('.main-nav a[href="#off-duty"]').click()
        check(page.locator("#ride-panel").is_visible(), "Phone navigation opens the riding window without jumping to the footer")
        check(page.evaluate("scrollY") == 0, "Opening a floating window keeps the reading position")
        page.locator("#companion-music").click()
        page.locator("#music-toggle").click()
        page.wait_for_function("document.querySelector('audio').currentTime > .3", timeout=20000)
        check(page.locator("#companion-music-status").inner_text() == "正在播放", "Compact music status follows real playback")
        page.locator("#music-panel .companion-close").click()
        time_before = page.locator("audio").evaluate("a => a.currentTime")
        page.wait_for_timeout(500)
        check(page.locator("audio").evaluate("a => !a.paused && a.currentTime") > time_before,
              "Closing the music window does not interrupt the track")
        page.locator("#companion-minimize").click()
        check(page.locator("audio").evaluate("a => !a.paused"), "Minimizing the bar also preserves playback")
        check(page.locator("#companion-restore .companion-playing").is_visible(), "The small button indicates ongoing playback")
        page.locator("#companion-restore").click()
        page.locator("#companion-music").click()
        page.locator("#music-toggle").click()
        check(page.locator("audio").evaluate("a => a.paused"), "Music can be paused after restoring the window")
        page.locator("#music-panel .companion-close").click()
        for width in [768, 900, 1440]:
            page.set_viewport_size({"width": width, "height": 1000})
            check(not page.locator("#mobile-companions").is_visible(), f"{width}px: no floating controls appear on desktop/tablet")
            check(page.locator("#ride-panel").is_visible() and page.locator("#music-panel").is_visible(),
                  f"{width}px: both original sidebar cards are restored")
            check(page.locator("#ride-panel #tracking-scene").count() == 1, f"{width}px: scene returns to the original sidebar")
            check(not overflow(page), f"{width}px: original responsive layout fits")
        context.close()

        reduced = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
        page = reduced.new_page()
        page.goto(base, wait_until="networkidle")
        check(page.locator("#motion-toggle").get_attribute("aria-pressed") == "true", "The phone preview respects reduced motion")
        reduced.close()
        fallback = browser.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False)
        page = fallback.new_page()
        page.goto(base, wait_until="networkidle")
        check(page.locator("#ride-panel").is_visible() and page.locator("#music-panel").is_visible(),
              "Without JavaScript, both cards remain available in the document")
        check(not page.locator("#mobile-companions").is_visible(), "No unusable floating controls appear without JavaScript")
        fallback.close()
        browser.close()
    check(not errors, f"No JavaScript errors: {errors}")
    (OUT / "mobile-check-result.json").write_text(json.dumps({"passed": True, "url": base, "viewports": results,
        "real_audio": True, "javascript_errors": errors}, indent=2), encoding="utf-8")


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
