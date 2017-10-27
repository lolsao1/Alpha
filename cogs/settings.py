"""
for changing server-wide bot settings
"""
import discord
from discord.ext import commands
import json
import os

class Settings:
  def __init__(self, bot_):
    self.bot = bot_
    with open('config.json') as file_in:
      self.config = json.load(file_in)

  def update_file(self, *args):
    with open('config.json', 'w') as file_out:
      json.dump(self.config, file_out, indent=2, sort_keys=True)

  def is_mod(self, context):
    if context.message.channel.permissions_for(context.message.author).administrator or context.message.author.id in self.config['admin_ids']:
      return True
    for server in self.config['servers']:
      if server['id'] == context.message.server.id:
        if context.message.author.id in server['mod_ids']:
          return True
        break
    return False

  def is_module(self, module):
    if module.lower() + ".py" in os.listdir('cogs'):
      return True
    return False

  @commands.group()
  async def module(self):
    """
    enables and disables server modules. 'help module' for more info
    """
    pass

  @module.command(name="enable", pass_context=True)
  async def enable_module(self, ctx, *module):
    """
    Enables a module in the current server
    """
    if not self.is_mod(ctx): print('nope'); return
    module = module[0].title()
    if not self.is_module(module): print('not nodule'); return
    for server in self.config['servers']:
      if server['id'] == ctx.message.server.id:
        if not module in server['enabled_modules']:
          server['enabled_modules'].append(module)
          await self.bot.say('{} has been enabled'.format(module))
          self.update_file(self)
        else:
          await self.bot.say('{} is already enabled'.format(module))
        break

  @module.command(name="disable", pass_context=True)
  async def disable_module(self, ctx, *module):
    """
    Disables a module in the current server
    """
    if not self.is_mod(ctx): return
    module = module[0].title()
    if not self.is_module(module): return
    for server in self.config['servers']:
      if server['id'] == ctx.message.server.id:
        if module in server['enabled_modules']:
          server['enabled_modules'].remove(module)
          await self.bot.say('{} has been disabled'.format(module))
          self.update_file(self)
        else:
          await self.bot.say('{} is already disabled'.format(module))
        break

  @module.command(name="list", pass_context=True)
  async def list_modules(self, ctx):
    """
    Lists all of the available modules
    """
    modules = "**Available modules:**\n```\n"
    for module in os.listdir('cogs'):
      if not module.startswith('.') and not module.startswith('_'):
        modules += module.split('.')[0].title() + "\n"
    modules += "```"
    await self.bot.say(modules)


  @commands.command(name="prefix", pass_context=True)
  async def change_prefix(self, ctx, *new_prefix):
    """
    Changes the bot prefix for the current server
    """
    if not self.is_mod(ctx): return
    if new_prefix == ():
      for server in self.config['servers']:
        if server['id'] == ctx.message.server.id:
          await self.bot.say("This server's prefix is {}".format(server['prefix']))
          break
      return
    for server in self.config['servers']:
      if server['id'] == ctx.message.server.id:
        server['prefix'] = ' '.join(new_prefix).strip(',')
        break
    self.update_file(self)
    await self.bot.say('Prefix set to {}'.format(' '.join(new_prefix).strip(',')))

  @commands.group()
  async def mod(self):
    """
    add, remove, list server mods. 'help mod' for more info
    """
    pass

  @mod.command(name="list", pass_context=True)
  async def list_mods(self, ctx):
    """
    Lists all of the mods in the server
    """
    mod_list = []
    for member in ctx.message.server.members:
      if ctx.message.channel.permissions_for(member).administrator:
        mod_list.append(member.name + "#" + member.discriminator)
      for server in self.config['servers']:
        if server['id'] == ctx.message.server.id:
          if member.id in server['mod_ids']:
            mod_list.append(member.name + "#" + member.discriminator)
    await self.bot.say('**Mods in {}**\n{}'.format(ctx.message.server.name, ', '.join(mod_list)))

  @mod.command(name="add", pass_context=True)
  async def add_mod(self, ctx, *mod):
    """
    Adds a user as a server mod (from mention or id)
    """
    if not self.is_mod(ctx): return
    if not ctx.message.mentions == []:
      mod = ctx.message.mentions[0].id
    for server in self.config['servers']:
      if server['id'] == ctx.message.server.id:
        if not mod in server['mod_ids']:
          server['mod_ids'].append(mod)
          await self.bot.say('{0.mention} has been added as a moderator'.format(await self.bot.get_user_info(mod)))
          self.update_file(self)
        else:
          await self.bot.say('{0.mention} is already a moderator'.format(await self.bot.get_user_info(mod)))
        break

  @mod.command(name="remove", pass_context=True)
  async def remove_mod(self, ctx, *mod):
    """
    Removes a user as a server mod (from mention or id)
    """
    if not self.is_mod(ctx): return
    if not ctx.message.mentions == []:
      mod = ctx.message.mentions[0].id
    for server in self.config['servers']:
      if server['id'] == ctx.message.server.id:
        if mod in server['mod_ids']:
          server['mod_ids'].remove(mod)
          self.update_file(self)
          await self.bot.say('{0.mention} has been removed as a moderator'.format(await self.bot.get_user_info(mod)))
        else:
          await self.bot.say('{0.mention} is not a moderator'.format(await self.bot.get_user_info(mod)))
        break

  @commands.group(name="welcome")
  async def welcome(self):
    """
    'welcome channel' to set welcome channel
    """
    pass

  @welcome.command(name="channel", pass_context=True)
  async def channel_welcome(self, ctx, *channel):
    """
    change the channel for welcome messages
    """
    if not self.is_mod(ctx): return
    if channel is None: return
    channel =  ' '.join(channel).strip('<#').strip('>')
    for server in self.config['servers']:
      if server['id'] == ctx.message.server.id:
        server['welcome_channel'] = channel
        break
    self.update_file()
    await self.bot.say("Welcome channel set to {}!".format(ctx.message.server.get_channel(channel)))

def setup(bot):
  bot.add_cog(Settings(bot))
