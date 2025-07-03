from langchain_openai import ChatOpenAI
from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
import asyncio
from dotenv import load_dotenv
import os
import time
from pathlib import Path
load_dotenv()

async def main():
    # Use home directory downloads folder (lowercase) to match the example exactly
    downloads_path = os.path.join(os.path.expanduser('~'), 'downloads')
    os.makedirs(downloads_path, exist_ok=True)  # Create if it doesn't exist
    print(f"Downloads will be saved to: {downloads_path}")
    
    # Configure browser with download settings - exact match to example
    browser = Browser(
        config=BrowserConfig(
            headless=False,  # Set to false to see the browser in action
            new_context_config=BrowserContextConfig(
                save_downloads_path=downloads_path
            )
        )
    )
    
    agent = Agent(
        task="""
        1. Go to https://collin.tx.publicsearch.us/
        2. If a login page appears, log in with:
           - Username: jay.ozer@doma.com
           - Password: Domadomadoma00!
        3. Search for document number: 2024000146530
        4. After the search results appear, look for the "Download (Free)" option. 
           DO NOT click on "Export all Results" or any paid options.
        5. If you accidentally reach a payment/cart page, go back to the search results and look for the free download option.
        6. Click on the "Download (Free)" button/link to download the document.
        7. Wait for the download to complete and confirm when the "Download (Free)" button no longer shows "Loading".
        8. Report the download was successful.
        """,
        llm=ChatOpenAI(model="gpt-4.1"),
        browser=browser,
        max_actions_per_step=8,
        use_vision=True,
    )
    
    try:
        await agent.run(max_steps=25)
        
        # Wait longer to ensure download completes
        print("Waiting 30 seconds for download to complete...")
        time.sleep(30)  # Increased to 30 seconds
        
        # Check multiple possible download paths
        potential_paths = [
            downloads_path,  # lowercase 'downloads' (from example)
            os.path.join(os.path.expanduser('~'), 'Downloads'),  # standard macOS Downloads folder
            os.path.join(os.getcwd(), 'downloads')  # local downloads folder
        ]
        
        all_found_files = []
        for path in potential_paths:
            print(f"Checking for files in: {path}")
            if os.path.exists(path):
                # Check with multiple patterns
                patterns = ["*2024000146530*", "*deed*", "*.pdf", "*.PDF"]
                for pattern in patterns:
                    found = list(Path(path).glob(pattern))
                    if found:
                        # Filter to recent files (last 10 minutes)
                        recent = [f for f in found if (time.time() - f.stat().st_mtime) < 600]
                        all_found_files.extend(recent)
        
        if all_found_files:
            # Sort by modification time (most recent first)
            recent_files = sorted(all_found_files, key=lambda f: f.stat().st_mtime, reverse=True)[:5]
            print(f"✅ Download successful! Most recent files found:")
            for file in recent_files:
                print(f"  - {file} (modified {time.ctime(file.stat().st_mtime)})")
        else:
            print("❌ No matching downloaded files found in any of the checked folders.")
            
    finally:
        # Always close the browser
        await browser.close()
        print("Browser closed")

asyncio.run(main())