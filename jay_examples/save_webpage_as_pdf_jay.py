import asyncio
import os
import re
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from browser_use import ActionResult, Agent, Controller
from browser_use.browser.types import Page
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.session import BrowserSession
from browser_use.llm import ChatOpenAI

# Initialize controller
controller = Controller()

# Set up the download path
download_path = Path("/Users/acrobat/GitHubAcrobat/browser-use/jay_examples/downloads")
download_path.mkdir(parents=True, exist_ok=True)


# Custom action to save current page as PDF
@controller.registry.action('Save the current page as a PDF file')
async def save_pdf(page: Page):
    """Save the current webpage as a PDF file."""
    # Extract a clean filename from the URL
    short_url = re.sub(r'^https?://(?:www\.)?|/$', '', page.url)
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', short_url).strip('-').lower()
    sanitized_filename = f'{slug}.pdf'
    
    # Full path for the PDF
    pdf_path = download_path / sanitized_filename

    # Save the page as PDF
    await page.emulate_media(media='screen')
    await page.pdf(path=str(pdf_path), format='A4', print_background=True)
    
    msg = f'Saved page {page.url} as PDF to {pdf_path}'
    print(f"✅ {msg}")
    
    return ActionResult(
        extracted_content=msg, 
        include_in_memory=True, 
        long_term_memory=f'Saved PDF to {sanitized_filename}'
    )


async def main():
    """
    Example: Navigate to browser-use.com and save the page as a PDF
    """
    
    # Create browser session
    browser_session = BrowserSession(
        browser_profile=BrowserProfile(
            headless=False,  # Set to see the browser in action
            user_data_dir=None,  # Use incognito mode
        )
    )
    
    # Start the browser session
    await browser_session.start()
    
    task = """
    1. Go to https://browser-use.com/
    2. Wait for the page to fully load
    3. Save the current page as a PDF file using the custom save PDF action
    4. Then go to https://docs.browser-use.com/
    5. Save that page as a PDF file as well
    """

    # Initialize the language model
    model = ChatOpenAI(model='gpt-4.1-mini')

    # Create and run the agent with custom controller
    agent = Agent(
        task=task, 
        llm=model,
        controller=controller,  # Use our custom controller with save_pdf action
        browser_session=browser_session,
    )

    try:
        result = await agent.run(max_steps=10)
        print(f'\n🎯 Task completed: {result}')
        
        # Check for saved PDFs
        print("\n📁 Checking for saved PDF files...")
        pdf_files = list(download_path.glob("*.pdf"))
        
        if pdf_files:
            print(f"✅ Found {len(pdf_files)} PDF file(s):")
            for pdf_file in sorted(pdf_files, key=lambda f: f.stat().st_mtime, reverse=True)[:5]:
                print(f"  - {pdf_file.name}")
                print(f"    Size: {pdf_file.stat().st_size:,} bytes")
                print(f"    Modified: {pdf_file.stat().st_mtime}")
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