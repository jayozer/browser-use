import asyncio
import os
import shutil
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

	llm = ChatOpenAI(model='gpt-4.1-mini')

	# Simplified tasks - let agents choose their own file strategy
	task1 = 'find todays weather on Istanbul and extract it as json'
	task2 = 'find todays weather in Berlin and extract it as json'

	# Remove shared file_system_path - let each agent use its own temp directory
	agent1 = Agent(
		task=task1,
		browser_session=browser_session,
		llm=llm,
		# No file_system_path specified - use default temp directories
	)
	agent2 = Agent(
		task=task2,
		browser_session=browser_session,
		llm=llm,
		# No file_system_path specified - use default temp directories
	)

	# Run both agents
	results = await asyncio.gather(agent1.run(), agent2.run())
	
	# Copy files from agent temp directories to downloads directory
	print("\nCopying files to downloads directory...")
	
	# Get the actual temp directories where files were saved
	agent1_dir = agent1.file_system.get_dir()
	agent2_dir = agent2.file_system.get_dir()
	
	# Copy any files from agent workspaces to downloads directory with clear names
	for i, (agent_dir, city) in enumerate([(agent1_dir, "istanbul"), (agent2_dir, "berlin")]):
		if os.path.exists(agent_dir):
			for filename in os.listdir(agent_dir):
				if filename.endswith('.md') or filename.endswith('.json'):
					src_path = os.path.join(agent_dir, filename)
					
					# Create clear destination filename with city name
					dst_filename = f"{city}_weather_data.md"
					dst_path = os.path.join(downloads_dir, dst_filename)
					
					shutil.copy2(src_path, dst_path)
					print(f"Copied {city} weather data to {dst_path}")
	
	await browser_session.kill()
	print("\nBoth agents completed successfully!")


asyncio.run(main())