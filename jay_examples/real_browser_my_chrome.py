"""
This real_browser.py script demonstrates how to use browser-use with your actual Chrome browser 
instead of a separate Playwright-managed browser instance.
My actual chrome, same profile, cookies, has my bookmarks, loged into my accounts, 
my chrome extensions play a role. best to use my passwords!
"""



import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv()

from browser_use import Agent
from browser_use.browser import BrowserProfile, BrowserSession
from browser_use.llm import ChatOpenAI

browser_profile = BrowserProfile(
	# NOTE: you need to close your chrome browser - so that this can open your browser in debug mode
	executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
	user_data_dir='~/.config/browseruse/profiles/default',
	headless=False,
)
browser_session = BrowserSession(browser_profile=browser_profile)


async def main():
	agent = Agent(
		task='Find todays DOW stock price',
		llm=ChatOpenAI(model='gpt-4.1-mini'),
		browser_session=browser_session, # single agent task, no multiple agents
	)

	await agent.run()
	await browser_session.close()

	input('Press Enter to close...')


if __name__ == '__main__':
	asyncio.run(main())
