"""
tools for the bot admin
"""

import os
import sys
import json
import inspect
import requests

import discord
from discord.ext import commands


class Admin:
  def __init__(self, bot_):
    self.bot = bot_
    with open('config.json') as file_in:
      self.config = json.load(file_in)

  def update_config(self):
    with open('config.json', 'r') as file_in:
      self.config = json.load(file_in)

  def update_file(self):
    with open('config.json', 'w') as file_out:
      json.dump(self.config, file_out, indent=2, sort_keys=True)

  @commands.command(name="gitpull", hidden=True, pass_context=True)
  async def gitpull(self, ctx):
    if not ctx.message.author.id in self.config['admin_ids']: return
    os.popen("git pull origin master")
    await self.bot.say("Done!")

  @commands.command(name="restart", hidden=True, pass_context=True)
  async def restart(self, ctx):
    if not ctx.message.author.id in self.config['admin_ids']: return
    await self.bot.say("Restarting bot...")
    python = sys.executable
    os.execl(python, python, * sys.argv)

  @commands.command(name="exit", hidden=True, pass_context=True)
  async def stop(self, ctx):
    if not ctx.message.author.id in self.config['admin_ids']: return
    await self.bot.say("Stopping bot...")
    sys.exit()

  @commands.command(name="oinvite", pass_context=True, hidden=True)
  async def get_server_invite(self, ctx, *server):
    if not ctx.message.author.id in self.config['admin_ids']: return
    if not self.bot.get_server(server[0]) is None:
      invite = await self.bot.create_invite(self.bot.get_server(server[0]))
      await self.bot.send_message(ctx.message.author, invite.url)

  @commands.command(name="eval", pass_context=True, hidden=True)
  async def debug(self, ctx, *, code: str):
    """evaluates python code"""
    if not ctx.message.author.id in self.config['admin_ids']: return
    self.update_config()
    code = code.strip('` ')
    python = '```py\n{}\n```'
    result = None
    env = {
      'bot': self.bot,
      'ctx': ctx,
      'message': ctx.message,
      'server': ctx.message.server,
      'channel': ctx.message.channel,
      'author': ctx.message.author
    }
    env.update(globals())
    env.update(locals())
    try:
      result = eval(code, env)
      if inspect.isawaitable(result):
        result = await result
    except Exception as e:
      await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
      return
    await self.bot.say(python.format(result))
    self.update_file()

  @commands.command(name="debug", pass_context=True, hidden=True)
  async def exec_command(self, ctx, *code):
    """
    executes python code
    """
    if not ctx.message.author.id in self.config['admin_ids']: return
    code = ' '.join(code)
    code = code.strip('`')
    self.update_config()
    python = '```py\n{}\n```'
    result = None
    env = {
      'bot': self.bot,
      'ctx': ctx,
      'message': ctx.message,
      'server': ctx.message.server,
      'channel': ctx.message.channel,
      'author': ctx.message.author
    }
    env.update(globals())
    env.update(locals())
    try:
      result = exec(code, env)
      if inspect.isawaitable(result):
        result = await result
    except Exception as e:
      await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
      return
    await self.bot.say(python.format(result))
    self.update_file()


  @commands.command(name="exec", pass_context=True, hidden=True)
  async def bash_exec(self, ctx, *code):
    """
    executes bash code
    """
    if not ctx.message.author.id in self.config['admin_ids']: return
    code = ' '.join(code)
    code = code.strip('`')
    result = "There was an error, check console for details."
    result = os.popen(code).read().strip('`')
    await self.bot.say("```\n{}\n```".format(result))

  @commands.command(name="addadmin", pass_context=True, hidden=True)
  async def add_admin(self, ctx, *new_admin):
    if not ctx.message.author.id in self.config['admin_ids']: return
    try:
      member = ctx.message.mentions[0].id
    except IndexError:
      member = new_admin
    self.config['admin_ids'].append(member)
    self.update_file()
    added_admin = [members.mention for members in self.bot.get_all_members() if members.id == member][0]
    await self.bot.say("{} has been added as an admin! :smile:".format(added_admin))

  @commands.command(name="removeadmin", pass_context=True, hidden=True)
  async def remove_admin(self, ctx, *admin):
    if not ctx.message.author.id in self.config['admin_ids']: return
    try:
      member = ctx.message.mentions[0].id
    except IndexError:
      member = new_admin
    self.config['admin_ids'].remove(member)
    self.update_file()
    removed_admin = [members.mention for members in self.bot.get_all_members() if members.id == member][0]
    await self.bot.say("{} has been removed as an admin".format(removed_admin))

def setup(bot):
  bot.add_cog(Admin(bot))
