import asyncio
from playwright.async_api import async_playwright
import aiohttp
import aiofiles
import os
import random
from urllib.parse import urlparse, urljoin

async def download_image(session, url, folder):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                filename = os.path.join(folder, url.split("/")[-1].split("?")[0])
                async with aiofiles.open(filename, mode='wb') as f:
                    await f.write(await response.read())
                print(f"Downloaded: {filename}")
            else:
                print(f"Failed to download {url}. Status code: {response.status}")
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")

async def process_page(page, url, session, folder):
    try:
        await page.goto(url, wait_until="networkidle")
        
        # Wait for the main image to be visible
        await page.wait_for_selector(".detail-main-img", state="visible", timeout=30000)
        
        # Extract all main image URLs
        main_images = await page.evaluate('''
            () => Array.from(document.querySelectorAll('.detail-main-img'))
                .map(img => img.src)
        ''')
        
        # Download images
        tasks = [download_image(session, urljoin(url, img_url), folder) for img_url in main_images]
        await asyncio.gather(*tasks)
        
        print(f"Finished processing {url}")
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")

async def main(url_file):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        
        # Configure the page to bypass common anti-bot measures
        await page.route("**/*", lambda route: route.continue_())
        await page.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
        
        folder = "downloaded_images"
        os.makedirs(folder, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            with open(url_file, 'r') as file:
                urls = file.read().splitlines()
            
            for url in urls:
                await process_page(page, url, session, folder)
                await asyncio.sleep(random.uniform(2, 5))  # Random delay between requests
        
        await browser.close()

if __name__ == "__main__":
    url_file = "C:\\Users\\zanca\\Documents\\dropshipping_products.txt"
    asyncio.run(main(url_file))