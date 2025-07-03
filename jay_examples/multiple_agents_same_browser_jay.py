import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
	from dotenv import load_dotenv
	load_dotenv()
except ImportError:
	# dotenv not installed, skip loading .env file
	pass


from browser_use import Agent
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.session import BrowserSession
from browser_use.llm import ChatOpenAI


async def main():
	# Create downloads directory if it doesn't exist
	downloads_dir = "/Users/acrobat/GitHubAcrobat/browser-use/jay_examples/downloads"
	os.makedirs(downloads_dir, exist_ok=True)
	
	browser_session = BrowserSession(
		browser_profile=BrowserProfile(
			keep_alive=True,
			user_data_dir=None,
			headless=False,
		)
	)
	await browser_session.start()

	current_agent = None
	llm = ChatOpenAI(model='gpt-4.1-mini')

	task1 = f'find todays weather on Istanbul and extract it as json. Save the JSON data to a file named "istanbul_weather.json" in the directory {downloads_dir}'
	task2 = f'find todays weather in Berlin and extract it as json. Save the JSON data to a file named "berlin_weather.json" in the directory {downloads_dir}'

	agent1 = Agent(
		task=task1,
		browser_session=browser_session,
		llm=llm,
	)
	agent2 = Agent(
		task=task2,
		browser_session=browser_session,
		llm=llm,
	)

	await asyncio.gather(agent1.run(), agent2.run())
	await browser_session.kill()


asyncio.run(main())
