"""One-off observation script: take the quiz as two takers on the LIVE site, screenshot, and check
whether the animated sprite differs between two frames one second apart. Not part of the app or the
check; written to satisfy the stream's own mission-order step 8 (Observe)."""
import time
import hashlib
from playwright.sync_api import sync_playwright

URL = "https://joshuamatalon.github.io/which-pokemon/"
VIEWPORT = {"width": 390, "height": 844}


def take_quiz(page, taker_name, shot_path):
    page.goto(URL, wait_until="networkidle")
    page.wait_for_selector("#names-grid button")
    page.click(f"#names-grid button:has-text('{taker_name}')")
    for i in range(15):
        page.wait_for_selector("#answers button", state="visible")
        buttons = page.query_selector_all("#answers button")
        # deterministic-ish: pick the (i mod len) button so different items pick different positions
        idx = i % len(buttons)
        buttons[idx].click()
        page.wait_for_timeout(150)
    page.wait_for_selector("#result-name", state="visible")
    page.wait_for_timeout(500)
    name = page.inner_text("#result-name")
    genus = page.inner_text("#result-genus")
    art_src = page.get_attribute("#art-img", "src")
    ani_src = page.get_attribute("#ani-img", "src")

    # frame 1
    ani_el = page.query_selector("#ani-img")
    shot1 = ani_el.screenshot()
    time.sleep(1.0)
    page.wait_for_timeout(50)
    shot2 = ani_el.screenshot()
    frame_changed = hashlib.sha256(shot1).hexdigest() != hashlib.sha256(shot2).hexdigest()

    page.screenshot(path=shot_path, full_page=True)
    return {
        "taker": taker_name,
        "result_name": name,
        "result_genus": genus,
        "art_src": art_src,
        "ani_src": ani_src,
        "ani_frame_changed_1s_apart": frame_changed,
    }


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        results = []
        for taker, shot in [("Milo", "DELIVERY-shots/milo.png"), ("Carolyn", "DELIVERY-shots/carolyn.png")]:
            page = browser.new_page(viewport=VIEWPORT)
            r = take_quiz(page, taker, shot)
            results.append(r)
            page.close()
        browser.close()
        for r in results:
            print(r)


if __name__ == "__main__":
    main()
