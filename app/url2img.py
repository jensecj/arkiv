import asyncio

from pyppeteer import launch


async def generate_images(url):
    browser = await launch()
    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()

    await page.setJavaScriptEnabled(False)
    await page.setViewport({"width": 1200, "height": 800})
    await page.emulateMedia("screen")
    await page.goto(url)

    print("generating thumbnail...")
    await page.screenshot({"path": "thumbnail.png"})

    print("generating full-page image...")
    await page.screenshot({"path": "screenshot.png", "fullPage": True})

    await browser.close()
