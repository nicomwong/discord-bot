from logging import error
import os
import sys
import json
from dotenv import load_dotenv

from discord.ext.commands.errors import ArgumentParsingError

import discord
from discord.ext import commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from multiprocessing import Process


this = sys.modules[__name__]
this.running = False

load_dotenv()


def main():

    bot = commands.Bot(command_prefix="!")

    @bot.event
    async def on_ready():
        if this.running:
            return

        this.running = True
        print('Bot is running now!')

    @bot.event
    async def on_guild_join(guild):
        file = open("./filters.json", "r")
        obj = json.load(file)
        obj[guild.id] = {"words": []}
        file.close()
        file = open("./filters.json", "w")
        json.dump(obj, file, indent=4)
        file.close()
        pun = open("./punishment.json", "r")
        obj2 = json.load(pun)
        obj2[guild.id] = {}
        pun.close()
        pun = open("./punishment.json", "w")
        json.dump(obj2, pun, indent=4)
        pun.close()
        lim = open("./violimit.json", "r")
        obj3 = json.load(lim)
        obj3[guild.id] = {"limit": 999}
        lim.close()
        lim = open("./violimit.json", "w")
        json.dump(obj3, lim, indent=4)
        lim.close()

    @bot.event
    async def on_message(message):
        if message.author != bot.user and len(message.content) > 0 and message.content[0] != "!":
            file = open("./filters.json", "r")
            obj = json.load(file)
            guild = obj.get(str(message.guild.id))
            words = guild.get("words")
            filter = any(ele.lower() in message.content.lower()
                         for ele in words)
            if filter == True:
                await message.delete()
                pun = open("./punishment.json", "r")
                lim = open("./violimit.json", "r")
                obj2 = json.load(pun)
                obj3 = json.load(lim)
                guild2 = obj2.get(str(message.guild.id))
                guild3 = obj3.get(str(message.guild.id))
                numVio = guild2.get(str(message.author.id), 0)
                limit = guild3.get("limit")
                numVio += 1
                guild2[str(message.author.id)] = numVio
                pun.close()
                lim.close()
                pun = open("./punishment.json", "w")
                json.dump(obj2, pun, indent=4)
                await message.channel.send("User: " + message.author.display_name + ", has violated the rules (" + str(numVio) + ") times.")
                if numVio >= limit:
                    await message.author.ban(reason="User" + message.author.display_name + ", has been banned.")
                    await message.channel.send("User" + message.author.display_name + ", has been banned.")
                pun.close()
            file.close()
        else:
            await bot.process_commands(message)

    @bot.command()
    async def add(ctx, *args):
        file = open("./filters.json", "r")
        obj = json.load(file)
        guild = obj.get(str(ctx.guild.id))
        words = guild.get("words")
        file.close()
        if len(args) == 0:
            await ctx.send("No word was given.")
        else:
            for word in args:
                if word in words:
                    await ctx.send("Word is already banned.")
                else:
                    words.append(word)
                    await ctx.channel.send("Word has been banned from server by: " + ctx.message.author.display_name)
            file = open("./filters.json", "w")
            json.dump(obj, file, indent=4)
            file.close()
        await ctx.message.delete()

    @bot.command()
    async def remove(ctx, *args):
        file = open("./filters.json", "r")
        obj = json.load(file)
        guild = obj.get(str(ctx.guild.id))
        words = guild.get("words")
        file.close()
        if len(args) == 0:
            await ctx.send("No word was given.")
        else:
            for word in args:
                if word in words:
                    words.remove(word)
                    await ctx.channel.send("The word " + word + " has been unbanned.")
                else:
                    await ctx.channel.send("The word has not been banned.")
            file = open("./filters.json", "w")
            json.dump(obj, file, indent=4)
            file.close()

    @bot.command()
    @commands.has_permissions(ban_members=True)
    async def setv(ctx, *args):
        lim = open("./violimit.json", "r")
        obj3 = json.load(lim)
        guild3 = obj3.get(str(ctx.guild.id))
        lim.close()
        if len(args) == 0:
            await ctx.send("No number was given.")
        else:
            limit = args[0]
            guild3["limit"] = int(limit)
            await ctx.channel.send("The violation limit has been changed to: " + limit + " violations.")
            lim = open("./violimit.json", "w")
            json.dump(obj3, lim, indent=4)
            lim.close()

    @bot.event
    async def on_command_error(ctx, error):
        file = open("./filters.json", "r")
        obj = json.load(file)
        guild = obj.get(str(ctx.guild.id))
        words = guild.get("words")
        filter = any(ele.lower() in ctx.message.content.lower()
                     for ele in words)
        if filter == True:
            await ctx.message.delete()
            pun = open("./punishment.json", "r")
            obj2 = json.load(pun)
            guild2 = obj2.get(str(ctx.guild.id))
            numVio = guild2.get(str(ctx.author.id), 0)
            numVio += 1
            guild2[str(ctx.author.id)] = numVio
            pun.close()
            pun = open("./punishment.json", "w")
            json.dump(obj2, pun, indent=4)
            await ctx.channel.send("User: " + ctx.author.display_name + ", has violated the rules (" + str(numVio) + ") times.")
            pun.close()
        file.close()

    @bot.command()
    @commands.has_permissions(ban_members=True)
    async def ban(ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send("User " + member.display_name + " has been banned.")

    @bot.command()
    @commands.has_permissions(ban_members=True)
    async def unban(ctx, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user
            if(user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(member_name + " has been unbanned.")

    bot.run(os.getenv("BOT_TOKEN"))


if __name__ == "__main__":
    main()
