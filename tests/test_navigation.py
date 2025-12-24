import re
from playwright.sync_api import Page, expect
import os
import pytest

SCREENSHOT_DIR = "tests/screenshots"

def test_navigation_features(page: Page, http_server):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    page.goto(http_server)

    # Wait for the app to be initialized
    page.wait_for_function("window.rendition", timeout=15000)

    # --- Test TOC ---
    toc_items = page.evaluate("window.rendition.book.toc")
    assert len(toc_items) == 24

    # --- Test Navigation ---
    # Navigate to "STAVE ONE."
    page.evaluate("window.rendition.display('OEBPS/816934448499000088_46-h-0.htm.html')")

    # Verify the current chapter index
    current_chapter_index = page.evaluate("window.rendition.current_chapter_index")
    assert current_chapter_index == 4

    # --- Test Next/Previous ---
    # Click next to go to Stave II
    page.evaluate("window.rendition.next_chapter()")
    current_chapter_index = page.evaluate("window.rendition.current_chapter_index")
    assert current_chapter_index == 5

    # Click previous to go back to Stave I
    page.evaluate("window.rendition.previous_chapter()")
    current_chapter_index = page.evaluate("window.rendition.current_chapter_index")
    assert current_chapter_index == 4
