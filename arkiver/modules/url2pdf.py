import asyncio

from pyppeteer import launch


async def _generate_media_pdf(url, media):
    browser = await launch()
    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()

    await page.setJavaScriptEnabled(False)
    await page.goto(url)

    await page.emulateMedia(media)
    await page.setViewport({"width": 1200, "height": 800})

    await page.pdf(
        {
            "path": media + ".pdf",
            "printBackground": True,
            "margin": {"top": 0, "bottom": 0, "left": 0, "right": 0},
        }
    )

    await browser.close()


async def generate_pdfs(url):
    try:
        print("generating screen pdf...")
        await _generate_media_pdf(url, "screen")
    except KeyboardInterrupt:
        print("user interrupted handler, skipping.")
    except Exception as error:
        print(repr(error))

    try:
        print("generating print pdf...")
        await _generate_media_pdf(url, "print")
    except KeyboardInterrupt:
        print("user interrupted handler, skipping.")
    except Exception as error:
        print(repr(error))
