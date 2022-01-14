from discord.ext import commands
import discord
import logging
import logging.config
import json
from whitelist import Whitelist
from web3 import Web3
import config

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


#
# Commands
#
def is_admin():
	def predicate(ctx):
		return ctx.message.author.id in config.discord_admins
	return commands.check(predicate)

def has_access():
	def predicate(ctx):
		channel_ok = ctx.message.channel.id == config.discord_channel_id
		role_ok = discord.utils.find(lambda r: r.id == config.discord_role_id, ctx.message.guild.roles) in ctx.message.author.roles
		return channel_ok and role_ok
	return commands.check(predicate)

@is_admin()
@bot.command(name="whitelist", aliases=["wl"])
async def show_whitelist(ctx):
	count = Whitelist.count(ctx.guild.id)
	await DiscordUtils.embed(ctx=ctx, title="Whitelist", description="There are currently {} wallets on the whitelist.".format(count))

@has_access()
@bot.command(name="reg")
async def reg_whitelist(ctx, wallet):
	if Web3.isAddress(wallet):
		Whitelist.add(ctx.message.author.id, wallet, ctx.message.guild.id)
		await ctx.message.add_reaction('✅')
	else:
		await ctx.message.add_reaction('❌')

@has_access()
@bot.command(name="unreg")
async def unreg_whitelist(ctx):
	if Whitelist.remove(ctx.message.author.id, ctx.guild.id):
		await ctx.message.add_reaction('✅')
	else:
		await ctx.message.add_reaction('❌')

@has_access()
@bot.command(name="check")
async def check_whitelist(ctx):
	if Whitelist.check(ctx.message.author.id, ctx.guild.id):
		await ctx.message.add_reaction('✅')
	else:
		await ctx.message.add_reaction('❌')


#
# Run bot
#
bot.run(config.discord_access_token)
