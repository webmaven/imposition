from playwright.sync_api import Page, expect
import os
import pytest

SCREENSHOT_DIR = "tests/screenshots"

def test_renders_first_chapter(page: Page, http_server):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # Listen for uncaught exceptions
    error_logs = []
    page.on("pageerror", lambda exc: error_logs.append(exc))

    page.goto(http_server)

    # The viewer div should be present
    viewer = page.locator("#viewer")
    expect(viewer).to_be_visible()

    # The iframe should be created inside the viewer
    iframe = viewer.locator("iframe")
    expect(iframe).to_be_visible(timeout=15000)

    # The iframe should contain the cover image
    iframe_element = iframe.element_handle()
    frame = iframe_element.content_frame()
    expect(frame.locator("img.x-ebookmaker-cover")).to_be_visible()

    # Take a screenshot on success
    page.screenshot(path=f"{SCREENSHOT_DIR}/test_renders_first_chapter_passed.png")

    # Assert that there were no uncaught exceptions
    if error_logs:
        # On failure, take a screenshot
        page.screenshot(path=f"{SCREENSHOT_DIR}/test_renders_first_chapter_failed.png")
        pytest.fail(f"Uncaught exception in browser console: {error_logs[0]}")
