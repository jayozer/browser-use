import asyncio
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from browser_use import Agent
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.session import BrowserSession
from browser_use.llm import ChatOpenAI

# Set up the download path
download_path = Path("/Users/acrobat/GitHubAcrobat/browser-use/jay_examples/downloads")
download_path.mkdir(parents=True, exist_ok=True)
print(f"Downloads will be saved to: {download_path}")


async def main():
    """
    Navigate to collin.tx.publicsearch.us, log in, search for a document, and download it.
    """
    
    # Create browser session with downloads_path configured
    browser_session = BrowserSession(
        browser_profile=BrowserProfile(
            downloads_path=str(download_path),  # This is the key - browser-use will save downloads here
            headless=False,  # Set to see the browser in action
            user_data_dir=None,  # Use incognito mode
        )
    )
    
    # Start the browser session
    await browser_session.start()
    
    task = """
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
    """

    # Initialize the language model
    model = ChatOpenAI(model='gpt-4.1-mini')

    # Create and run the agent
    agent = Agent(
        task=task, 
        llm=model,
        browser_session=browser_session,
        max_actions_per_step=10,  # Allow more actions per step for complex navigation
        use_vision=True,  # Use vision to better understand the page
    )

    try:
        result = await agent.run(max_steps=25)
        print(f'\n🎯 Task completed: {result}')
        
        # Check for downloaded files
        print("\n📁 Checking for downloaded files...")
        downloaded_files = browser_session.downloaded_files  # Get list of files downloaded during session
        
        if downloaded_files:
            print(f"✅ Downloaded {len(downloaded_files)} file(s):")
            for file_path in downloaded_files:
                print(f"  - {file_path}")
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"    Size: {file_size:,} bytes")
        else:
            # Also check the download directory manually
            print("⚠️ No downloads tracked by browser session. Checking download directory...")
            pdf_files = list(download_path.glob("*.pdf"))
            if pdf_files:
                print(f"Found {len(pdf_files)} PDF file(s) in download directory:")
                for pdf_file in pdf_files:
                    print(f"  - {pdf_file}")
                    print(f"    Size: {pdf_file.stat().st_size:,} bytes")
            else:
                print("❌ No PDF files found in download directory")
                
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        
    finally:
        # Always close the browser session
        await browser_session.close()
        print("\n🔒 Browser session closed")


if __name__ == '__main__':
    asyncio.run(main()) 