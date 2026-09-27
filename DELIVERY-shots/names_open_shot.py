"""One-off screenshot: names screen at 390x844 with the How it works toggle open.
Written to satisfy stream-3's mission-order evidence bar. Not part of the app or the check."""
from playwright.sync_api import sync_playwright

URL = "https://joshuamatalon.github.io/which-pokemon/"
VIEWPORT = {"width": 390, "height": 844}


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT)
        page.goto(URL, wait_until="networkidle")
        page.wait_for_selector("#names-grid button")
        page.click(".how-it-works summary")
        page.wait_for_selector(".how-it-works[open]")
        page.wait_for_timeout(200)
        page.screenshot(path="DELIVERY-shots/names-open.png", full_page=True)
        browser.close()
        print("done")


if __name__ == "__main__":
    main()
