import asyncio

from pyppeteer import launch


async def generate_pdfs(url):
    browser = await launch()
    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()

    await page.setJavaScriptEnabled(False)
    await page.setViewport({"width": 1200, "height": 800})
    await page.emulateMedia("screen")
    await page.goto(url)

    print("generating screen pdf...")
    await page.emulateMedia("screen")
    await page.pdf(
        {
            "path": "screen.pdf",
            "printBackground": True,
            "margin": {"top": 0, "bottom": 0, "left": 0, "right": 0},
        }
    )

    print("generating print pdf...")
    await page.emulateMedia("print")
    await page.pdf(
        {
            "path": "print.pdf",
            "printBackground": True,
            "margin": {"top": 0, "bottom": 0, "left": 0, "right": 0},
        }
    )

    await browser.close()
