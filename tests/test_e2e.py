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

    # Use frame_locator for better stability
    frame_locator = page.frame_locator("#viewer iframe")
    expect(frame_locator.locator("img.x-ebookmaker-cover")).to_be_visible()

    # Take a screenshot on success
    page.screenshot(path=f"{SCREENSHOT_DIR}/test_renders_first_chapter_passed.png")

    # Assert that there were no uncaught exceptions
    if error_logs:
        # On failure, take a screenshot
        page.screenshot(path=f"{SCREENSHOT_DIR}/test_renders_first_chapter_failed.png")
        pytest.fail(f"Uncaught exception in browser console: {error_logs[0]}")

def test_navigation_buttons(page: Page, http_server):
    page.goto(http_server)

    # Wait for app to load
    iframe = page.locator("#viewer iframe")
    expect(iframe).to_be_visible(timeout=15000)

    prev_button = page.locator("#prev")
    next_button = page.locator("#next")

    # Initially "Previous" should be disabled
    expect(prev_button).to_be_disabled()
    expect(next_button).to_be_enabled()

    frame_locator = page.frame_locator("#viewer iframe")
    initial_text = frame_locator.locator("body").text_content() or ""

    # Click "Next"
    next_button.click()

    # Wait for "Previous" to become enabled
    expect(prev_button).to_be_enabled()

    # Verify content changed
    expect(frame_locator.locator("body")).not_to_have_text(initial_text, timeout=10000)

    # Click "Previous"
    prev_button.click()
    expect(prev_button).to_be_disabled()
    expect(frame_locator.locator("body")).to_have_text(initial_text)

def test_toc_navigation(page: Page, http_server):
    page.goto(http_server)

    # Wait for app to load
    expect(page.locator("#viewer iframe")).to_be_visible(timeout=15000)

    toc_links = page.locator("#toc a")
    # test_book.epub has 24 TOC links
    expect(toc_links).to_have_count(24)

    frame_locator = page.frame_locator("#viewer iframe")
    initial_text = frame_locator.locator("body").text_content() or ""

    # Click a link that is definitely in another file (e.g. STAVE TWO)
    # Stave Two is link index 12 (playOrder 13)
    stave_two_link = toc_links.nth(12)
    expect(stave_two_link).to_have_text("STAVE TWO.")
    stave_two_link.click()

    # Verify it is now active
    expect(stave_two_link).to_have_class("active")

    # Verify content changed
    expect(frame_locator.locator("body")).not_to_have_text(initial_text, timeout=10000)

    # Verify buttons state
    expect(page.locator("#prev")).to_be_enabled()
    expect(page.locator("#next")).to_be_enabled()
