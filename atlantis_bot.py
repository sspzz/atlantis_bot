from discord.ext import commands
import discord
import logging
import logging.config
import json
import whitelist
from web3 import Web3

# Utilities related to Discord
class DiscordUtils:
	@staticmethod
	async def embed(ctx, title, description, thumbnail=None, image=None, url=None, color=None):
		color = color if color is not None else 0x9B59B6
		embed = discord.Embed(title=title, description=description, color=color)
		if thumbnail is not None:
			embed.set_thumbnail(url=thumbnail)
		if image is not None:
			embed.set_image(url=image)
		if url is not None:
			embed.url = url
		await ctx.send(embed=embed)

	@staticmethod
	async def embed_fields(ctx, title, description, fields, inline=True, thumbnail=None, color=None):
		color = color if color is not None else 0x9B59B6
		embed = discord.Embed(title=title, description=description, color=color)
		if thumbnail is not None:
			embed.set_thumbnail(url=thumbnail)
		for field in fields:
			embed.add_field(name=field[0], value=field[1], inline=inline)			
		await ctx.send(embed=embed)

#
# Setup
#
bot = commands.Bot(command_prefix="!")

logging.basicConfig(filename='atlantis_bot.log',
                    filemode='a',
                    format='[%(asctime)s] %(name)s - %(message)s',
                    datefmt='%d-%m-%Y @ %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger('atlantis_bot')


def get_admins():
	with open('admins.txt', 'r') as file:
		return [int(line.rstrip()) for line in file.readlines()]
	return []

def is_admin():
	def predicate(ctx):
		return ctx.message.author.id in get_admins()
	return commands.check(predicate)

def has_access():
	def predicate(ctx):
		channel_ok = ctx.message.channel.id == 437876896664125443 #???
		role_id = 930398242540249090 #918603419646832710
		role_ok = wl_role = discord.utils.find(lambda r: r.id == role_id, ctx.message.guild.roles) in ctx.message.author.roles
		return channel_ok and role_ok
	return commands.check(predicate)

@is_admin()
@bot.command(name="whitelist", aliases=["wl"])
async def show_whitelist(ctx):
	wl = whitelist.get_entries(ctx.guild.id)

	if len(wl) < 1:
		await ctx.send("No wallets in whitelist.")
		return

	lines = list(map(lambda e: e.wallet, wl))
	await DiscordUtils.embed(ctx=ctx, title="Whitelist wallets", description=", ".join(lines))

@has_access()
@bot.command(name="reg")
async def reg_whitelist(ctx, wallet):
	if Web3.isAddress(wallet):
		whitelist.save_entry(ctx.message.author.id, wallet, ctx.message.guild.id)
		await ctx.message.add_reaction('✅')
	else:
		await ctx.message.add_reaction('❌')

@has_access()
@bot.command(name="unreg")
async def unreg_whitelist(ctx):
	if whitelist.delete_entry(ctx.message.author.id, ctx.guild.id):
		await ctx.message.add_reaction('✅')
	else:
		await ctx.message.add_reaction('❌')

@has_access()
@bot.command(name="check")
async def check_whitelist(ctx):
	user = whitelist.get_entry(ctx.message.author.id, ctx.guild.id)
	if user is not None:
		await ctx.message.add_reaction('✅')
	else:
		await ctx.message.add_reaction('❌')


#
# Run bot
#
try:
	file = open('creds.json', 'r')
	access_token = json.load(file)['access_token']	
	bot.run(access_token)
except:
	print("Missing or faulty creds.json")
