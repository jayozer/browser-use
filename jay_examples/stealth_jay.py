"""
This stealth_jay.py script demonstrates how to use browser-use with a stealth browser.
This stealth.py script is a sophisticated browser anti-detection demonstration that tests different browser configurations to see how well they can avoid bot detection.
Tests Multiple Browser Configurations
It runs 4 different browser setups sequentially and compares their stealth capabilities:

1. Default Browser - Normal Playwright - No stealth feature. 
2. Patchright Stealth Browser
3. Brave Browser
4. Brave + Patchright Stealth Browser

Each browser is configured with different stealth settings and tested against a bot detection website.

Bot detection testing - Then it uses creepjs to test the stealth capabilities of the browser.
- Takes screenshots of each browser's test results
- Displays images directly in terminal using imgcat
- Shows detection scores side-by-side

Then use a modified version of Playwright - Patchright:
- Modified version of Playwright with anti-detection patches
- Hides automation signatures
- Makes the browser appear more "human"


the script has examples for 
- Bot detector, 
- CAPTCHA Challenges, 
- Corporate website with Bot protection 
- Cloudflare challenges

It basically have a 4 different browser configs and it has stealth capabilities and detection scores and screenshots

I added imgcat - I did not add brave so it only works for normal playwright and patchright Stealth. 
When I install brave it will work for that too. 
i have two screenshots normal_browser, patchright_browser.png
Neither browser passed by the way for this website - trust scores were 47.5 and 55% respectively, need at least 80%.  - can t be running these with an F grade. 
"""

# pyright: reportMissingImports=false
import asyncio
import os
import shutil
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv()

from imgcat import imgcat

from browser_use.browser import BrowserSession
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.types import async_patchright
from browser_use.llm import ChatOpenAI
from browser_use import Agent

llm = ChatOpenAI(model='gpt-4o')

terminal_width, terminal_height = shutil.get_terminal_size((80, 20))


async def main():
	patchright = await async_patchright().start()

	print('\n\nNORMAL BROWSER:')
	# Default Playwright Chromium Browser
	normal_browser_session = BrowserSession(
		# executable_path=<defaults to playwright builtin browser stored in ms-cache directory>,
		browser_profile=BrowserProfile(
			user_data_dir=None,
			headless=False,
			stealth=False,
			# deterministic_rendering=False,
			# disable_security=False,
		)
	)
	await normal_browser_session.start()
	await normal_browser_session.create_new_tab('https://abrahamjuliot.github.io/creepjs/')
	await asyncio.sleep(5)
	await (await normal_browser_session.get_current_page()).screenshot(path='normal_browser.png')
	imgcat(Path('normal_browser.png').read_bytes(), height=max(terminal_height - 15, 40))
	await normal_browser_session.close()

	print('\n\nPATCHRIGHT STEALTH BROWSER:')
	patchright_browser_session = BrowserSession(
		# cdp_url='wss://browser.zenrows.com?apikey=your-api-key-here&proxy_region=na',
		#                or try anchor browser, browserless, steel.dev, browserbase, oxylabs, brightdata, etc.
		browser_profile=BrowserProfile(
			user_data_dir='~/.config/browseruse/profiles/stealth',
			stealth=True,
			headless=False,
			disable_security=False,
			deterministic_rendering=False,
		)
	)
	await patchright_browser_session.start()
	await patchright_browser_session.create_new_tab('https://abrahamjuliot.github.io/creepjs/')
	await asyncio.sleep(5)
	await (await patchright_browser_session.get_current_page()).screenshot(path='patchright_browser.png')
	imgcat(Path('patchright_browser.png').read_bytes(), height=max(terminal_height - 15, 40))
	await patchright_browser_session.close()

	# Brave Browser
	if Path('/Applications/Brave Browser.app/Contents/MacOS/Brave Browser').is_file():
		print('\n\nBRAVE BROWSER:')
		brave_browser_session = BrowserSession(
			browser_profile=BrowserProfile(
				executable_path='/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
				headless=False,
				disable_security=False,
				user_data_dir='~/.config/browseruse/profiles/brave',
				deterministic_rendering=False,
			)
		)
		await brave_browser_session.start()
		await brave_browser_session.create_new_tab('https://abrahamjuliot.github.io/creepjs/')
		await asyncio.sleep(5)
		await (await brave_browser_session.get_current_page()).screenshot(path='brave_browser.png')
		imgcat(Path('brave_browser.png').read_bytes(), height=max(terminal_height - 15, 40))
		await brave_browser_session.close()

	if Path('/Applications/Brave Browser.app/Contents/MacOS/Brave Browser').is_file():
		print('\n\nBRAVE + PATCHRIGHT STEALTH BROWSER:')
		brave_patchright_browser_session = BrowserSession(
			playwright=patchright,
			browser_profile=BrowserProfile(
				executable_path='/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
				headless=False,
				disable_security=False,
				user_data_dir=None,
				deterministic_rendering=False,
			),
			# **patchright.devices['iPhone 13'],  # emulate other devices: https://playwright.dev/python/docs/emulation
		)
		await brave_patchright_browser_session.start()
		await brave_patchright_browser_session.create_new_tab('https://abrahamjuliot.github.io/creepjs/')
		await asyncio.sleep(5)
		await (await brave_patchright_browser_session.get_current_page()).screenshot(path='brave_patchright_browser.png')
		imgcat(Path('brave_patchright_browser.png').read_bytes(), height=max(terminal_height - 15, 40))

		input('Press [Enter] to close the browser...')
		await brave_patchright_browser_session.close()

	# print()
	# agent = Agent(
	# 	task="""
	#         Go to https://abrahamjuliot.github.io/creepjs/ and verify that the detection score is >50%.
	#     """,
	# 	llm=llm,
	# 	browser_session=browser_session, # browser_seesion should be replaced with something we have above like patchright_browser_session.
	# )
	# await agent.run()

	# input('Press Enter to close the browser...')

	# agent = Agent(
	# 	task="""
	#         Go to https://bot-detector.rebrowser.net/ and verify that all the bot checks are passed.
	#     """,
	# 	llm=llm,
	# 	browser_session=browser_session,
	# )
	# await agent.run()
	# input('Press Enter to continue to the next test...')

	# agent = Agent(
	# 	task="""
	#         Go to https://www.webflow.com/ and verify that the page is not blocked by a bot check.
	#     """,
	# 	llm=llm,
	# 	browser_session=browser_session,
	# )
	# await agent.run()
	# input('Press Enter to continue to the next test...')

	# agent = Agent(
	# 	task="""
	#         Go to https://www.okta.com/ and verify that the page is not blocked by a bot check.
	#     """,
	# 	llm=llm,
	# 	browser_session=browser_session,
	# )
	# await agent.run()

	# agent = Agent(
	# 	task="""
	#         Go to https://nowsecure.nl/ check the "I'm not a robot" checkbox.
	#     """,
	# 	llm=llm,
	# 	browser_session=browser_session,
	# )
	# await agent.run()

	# input('Press Enter to close the browser...')


if __name__ == '__main__':
	asyncio.run(main())
