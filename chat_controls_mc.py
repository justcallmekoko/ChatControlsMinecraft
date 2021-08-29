import os
import re
import sys
import asyncio
import time
import socket
import threading
import discord
from string import printable
from dotenv import load_dotenv
from mcrcon import MCRcon
from datetime import datetime
from discord.ext.tasks import loop
from twitchio.ext import commands
from ast import literal_eval as make_tuple
import random
import pkgutil

sys.dont_write_bytecode = True

W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green
O  = '\033[33m' # orange
B  = '\033[34m' # blue
P  = '\033[35m' # purple
C  = '\033[36m' # cyan
GR = '\033[37m' # gray
T  = '\033[93m' # tan

load_dotenv()

global obj_list
obj_list = []

path = os.path.join(os.path.dirname(__file__), "plugins")
modules = pkgutil.iter_modules(path=[path])

random.seed(datetime.now())

class Bot(commands.Bot):
	global obj_list

	def __init__(self):
		load_dotenv()
		TWITCH_TOKEN = os.getenv('TWITCH_TOKEN')
		RCON_PASSWORD = os.getenv('RCON_PASSWORD')
		RCON_IP = os.getenv('RCON_IP')
		NICK = str(os.getenv('NICK'))
		INITIAL_CHANNELS = str(os.getenv('INITIAL_CHANNELS'))
		CLIENT_ID=os.getenv('CLIENT_ID')
		API_TOKEN=os.getenv('API_TOKEN')
		PREFIX=os.getenv('PREFIX')
		HOST_USER=os.getenv('HOST_USER')
		super().__init__(token=TWITCH_TOKEN, prefix='!', initial_channels=['WillStunForFood'])

	async def event_ready(self):
		# We are logged in and ready to chat and use commands...
		print(f'Logged in as | {self.nick}')

	async def event_join(self, user, potato):
		print('User joined: ' + str(potato.name))

	# Functions to work with twitch
	async def handle_cheers(self, message):	
		bad_chars = 'abcdefghijklmnopqrstuvwxyzABZDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()`~-_=+[{]}\|;:\'",<.>/?'
		
		contained_cheer = False
	
		cheer_amount = 0
	
		resp = str(message.content)
	
		#Parse cheers
	
		for resp_sub in resp.split(' '):
			if 'Cheer' in str(resp_sub):
				raw_cheer_amount = resp_sub.replace(':51\r\n', '').replace('Cheer', '').replace('\n', '').replace(':', '')
				cheer_amount = ''.join(char for char in raw_cheer_amount if char in printable)
				contained_cheer = True
				print('Cheer amount: ' + str(cheer_amount))
	
		bad_char_found = False
	
		for i in list(bad_chars):
			if str(i) in str(cheer_amount):
				bad_char_found = True
			
		if ((not re.search('[a-zA-Z]', str(cheer_amount))) and (not bad_char_found)):
			cheer_amount = re.sub("[^0-9]", "", str(cheer_amount))
			if (contained_cheer) and (int(cheer_amount) > 0):
				# Get bot category
				for obj in obj_list:
					if await obj.checkBits(int(cheer_amount)):
						cat = obj.cat
					
				# Stop all plugins with same category
				for obj in obj_list:
					if await obj.checkCat(cat):
						print('Stopping: ' + str(obj.name))
						run_stop = await obj.stop(resp)
					#await obj.stop(resp)
				
				# Find the plugin with the cheer amount
				for obj in obj_list:
					if await obj.checkBits(int(cheer_amount)):
						found = True
						print('Found plugin: ' + obj.name)
						#if obj.admin and not admin:
						#	await message.channel.send(message.author.mention + ' ' + str(cmd) + ' only admins may run this command')
						#	break
					
						run_run = await obj.runCheer(obj.name + ' ' + message.author.name, int(cheer_amount))
						#await obj.run(obj.name)
						break
		else:
			print('Cheer not valid: ' + str(cheer_amount))

	async def event_message(self, message):
		print(message.author.name + ': ' + message.content)
		await self.handle_cheers(message)

	@commands.command()
	async def hello(self, ctx: commands.Context):
		# Send a hello back!
		await ctx.send(f'Hello {ctx.author.name}!')


def get_class_name(mod_name):
	output = ""

	words = mod_name.split("_")[1:]

	for word in words:
		output += word.title()
	return output

for loader, mod_name, ispkg in modules:
	if mod_name not in sys.modules:

		loaded_mod = __import__(path+"."+mod_name, fromlist=[mod_name])

		class_name = get_class_name(mod_name)
		loaded_class = getattr(loaded_mod, class_name)

		instance = loaded_class()
		obj_list.append(instance)

bot = Bot()
bot.run()
