import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
from discord.voice_client import VoiceClient
import _thread as thread
import random
import sqlite3

'''Currently hardcoding the challenge & flag, while it can be updated via commands, need to make it persistant. Perhaps use a txt or database for this?''' 

challenge = "The Errors"
flag = "" #SECRET



#Client Declaration & Assignment
Client = discord.Client()
bot_prefix = "!"
client = commands.Bot(command_prefix=bot_prefix)

cooldowns = []

#"/home/container/"+
def execute_query(table, query):
    conn = sqlite3.connect("/home/container/"+table) #should probably change the identifier to database instead of table, since it isn't the table that it's addressing here
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    c.close()
    conn.close()

def db_query(table, query):
    conn = sqlite3.connect("/home/container/"+table) #ditto
    c = conn.cursor()
    c.execute(query)
    result = c.fetchall()
    c.close()
    conn.close()
    return result

@client.event
async def on_ready():
    pass

'''
Promotion Requirements
Script Kiddie: 50m/w
Hacker: 100m/w
Pro Hacker: 150m/w
Elite Hacker: 250m/w
Guru: 500m/w
Omniscient: 1000m/w
Additionally must be in Top 15
'''

def create_user(user):
    if len(db_query("users.db", "SELECT user_id FROM users WHERE user_id = %s" % (str(user.id)))) == 0:
        execute_query("users.db", "INSERT INTO users (user_id) VALUES (%s)" % (str(user.id)))

@client.event
async def on_message(message):
    global flag #Need to find a way to not have to make this global
    global challenge #ditto
    if message.channel.id == 439434153629319168:
        if message.content.upper() == "!ACCEPT":
            member = message.author
            role = discord.utils.get(message.guild.roles, name="Registered")
            role_level = discord.utils.get(message.guild.roles, name="Noob")
            await member.add_roles(role)
            await member.add_roles(role_level)
            channel = client.get_channel(439465475265658891)
            em = discord.Embed(title="User Registered", description="%s succesfully registered!" % (member.name), colour=0x55FF55)
            em.set_footer(text="We now have %s members!" % (len(member.guild.members)))
            await channel.send(embed=em)
            create_user(member)
        await message.delete()

    if message.content.upper().startswith("!PROMOTIONS"):
        if "Staff" in [role.name for role in message.author.roles]:
            levels = db_query("users.db", "SELECT message_weekly, user_id FROM users ORDER BY `message_weekly` DESC")
            leaderboard = ''
            for counter in range(0, 15):
                try:
                    user = discord.utils.get(message.guild.members, id=int(levels[counter][1]))
                    if user is None:
                        userid = "N/A"
                        level = levels[counter][0]
                    else:
                        userid = user.id
                        level = levels[counter][0]
                    leaderboard = leaderboard + "**#" + str(counter+1) + "** " + "<@"+ str(userid) +">" + ": **Messages: " + str(level) + "** \n"
                except IndexError:
                    pass

            em = discord.Embed(title="Possible Promotions:", description=leaderboard, colour=0xFFAA00) 
            await message.channel.send(embed=em)
        else:
            await message.channel.send("Error: No Permission {--5--}")

    if message.content.upper().startswith("!LOCK"):
        if "Staff" in [role.name for role in message.author.roles]:
            await message.delete()
            default = discord.utils.get(message.guild.roles, name="Registered")
            perms = default.permissions
            perms.send_messages = False
            try:
                time = int(message.content.split()[1]) * 60 #time in minutes (seconds -> minutes)
            except IndexError: #Saves us having to check the len() of the args, also means we don't have to make redundent code here 
                time = 0
            await default.edit(permissions=perms)
            if time == 0: #Basically if it = 0 then the lock is perm until someoone !unlock's it
                nEmbed = discord.Embed(title="Server Locked", description="The server has been locked by %s" % (message.author.mention), colour=0xFF5555)
            else:
                nEmbed = discord.Embed(title="Server Locked", description="The server has been locked by %s for **%s minutes**" % (message.author.mention, str(time/60)), colour=0xFF5555)
            nEmbed.set_footer(text="This bot is not capable of enforcing Discord Terms of Service but may submit statistical data to Trust & Safety using data collected by Guardian")
            logChannel = client.get_channel(447096454264389633)
            notice = await message.channel.send(embed=nEmbed)
            await logChannel.send(embed=nEmbed)
            if not time == 0:
                await asyncio.sleep(time)
                perms.send_messages = True
                await default.edit(permissions=perms)
                await notice.delete()

    if message.content.upper().startswith("!UNLOCK"):
        if "Staff" in [role.name for role in message.author.roles]:
            await message.delete()
            default = discord.utils.get(message.guild.roles, name="Registered")
            perms = default.permissions
            perms.send_messages = True
            await default.edit(permissions=perms)
            nEmbed = discord.Embed(title="Server Unlocked", description="The server has been unlocked by %s" % (message.author.mention), colour=0x55FF55)
            nEmbed.set_footer(text="This bot is not capable of enforcing Discord Terms of Service but may submit statistical data to Trust & Safety using data collected by Guardian")
            logChannel = client.get_channel(447096454264389633)
            notice = await message.channel.send(embed=nEmbed)
            await logChannel.send(embed=nEmbed)

    if message.content.upper().startswith("!KICK"):
        if "Staff" in [role.name for role in message.author.roles] or "Trusted User" in [role.name for role in message.author.roles]:
            args = message.content.split()
            await message.delete()
            if len(args) < 3:
                error = discord.Embed(title="Syntax Error", description="Usage: **!kick <user> <reason>**", colour=0xFF5555)
                await message.channel.send(embed=error)
                return
            memberMention = args[1]
            reason = " ".join(args[2:])
            member = discord.utils.get(message.guild.members, mention=memberMention)
            uNotify = discord.Embed(title="Kicked", description="You were kicked from The Labs by %s for **%s**" % (message.author.mention, reason), color=0xFFAA00)
            sNotify = discord.Embed(title="User Kicked", description="%s was kicked from The Labs by %s for **%s**" % (member.mention, message.author.mention, reason), color=0xFFAA00)
            uNotify.set_footer(text="This bot is not capable of enforcing Discord Terms of Service but may submit statistical data to Trust & Safety using data collected by Guardian")
            sNotify.set_footer(text="This bot is not capable of enforcing Discord Terms of Service but may submit statistical data to Trust & Safety using data collected by Guardian")
            try:
                await member.send(embed=uNotify)
            except:
                pass
            await member.kick(reason=reason + " [" + message.author.name + "]")
            logs = client.get_channel(447096454264389633)
            await logs.send(embed=sNotify)
            await message.channel.send(embed=sNotify)


    if message.content.upper().startswith("!BAN"):
        if "Staff" in [role.name for role in message.author.roles]:
            args = message.content.split()
            await message.delete()
            if len(args) < 3:
                error = discord.Embed(title="Syntax Error you fooking idiot", description="Usage: **!ban <user> <reason>**", colour=0xFF5555)
                await message.channel.send(embed=error)
                return
            memberMention = args[1]
            reason = " ".join(args[2:])
            member = discord.utils.get(message.guild.members, mention=memberMention)
            uNotify = discord.Embed(title="Banned", description="You were banned from The Labs by %s for **%s**" % (message.author.mention, reason), color=0xFF5555)
            sNotify = discord.Embed(title="User Banned", description="%s was banned from The Labs by %s for **%s**" % (member.mention, message.author.mention, reason), color=0xFF5555)
            uNotify.set_footer(text="This bot is not capable of enforcing Discord Terms of Service but may submit statistical data to Trust & Safety using data collected by Guardian")
            sNotify.set_footer(text="This bot is not capable of enforcing Discord Terms of Service but may submit statistical data to Trust & Safety using data collected by Guardian")
            try:
                await member.send(embed=uNotify)
            except:
                pass
            await member.ban(reason=reason + " [" + message.author.name + "]")
            logs = client.get_channel(447096454264389633)
            await logs.send(embed=sNotify)
            await message.channel.send(embed=sNotify)

    if message.content.upper().startswith("!REPORT"):  #Usage: !report <user_mention> | Reason | Evidence/MessageID
        args = message.content.split()
        report_args = message.content.split("|") #Reason actually isn't doing anything at the moment, but will do soon - PLACEHOLDER
        user_mention = args[1]
        user = discord.utils.get(message.guild.members, mention=user_mention)
        reason = report_args[1]
        evidence = report_args[2]
        try:
            int(evidence)
            if len(evidence.split()) == 1:
                isMessageId = True
            else:
                isMessageId = False
        except:
            isMessageId = False

        if isMessageId:
            messages = await message.channel.history(limit=250).flatten()
            reported_message = discord.utils.get(messages, id=int(evidence))
            if reported_message is None:
                #Message does not exist error output
                return
            message_content = reported_message.content

        #SQL SHIZ
        if not isMessageId:
            db_evidence = "[EVIDENCE]" + evidence
        else:
            db_evidence = '"' + message_content + '" by ' + str(reported_message.author)
        execute_query("reports.db", "INSERT INTO reports (offender_id, reporter_id, reason, evidence) VALUES (%s, %s, '%s', '%s')" % (str(user.id), str(message.author.id), reason, db_evidence))      
        rp_id = db_query("reports.db", "SELECT MAX(db_id) FROM reports")[0][0] 
        #FORM THE REPORT OUTPUT
        report = discord.Embed(title="User Report", description="The following report has been created:", colour=0xFFAA00)
        report.add_field(name="Offender", value="%s" % (user.mention), inline=False)
        report.add_field(name="Reporter", value="%s" % (message.author.mention), inline=False)
        report.add_field(name="Reason", value="%s" % (reason), inline=False)
        if isMessageId:
            report.add_field(name="Offensive Content", value="'%s' by %s" % (message_content, reported_message.author.mention), inline=False)
        else:
            report.add_field(name="Evidence", value="%s" % (evidence), inline=False)
        report.set_footer(text="Report ID: #0%s" % (str(rp_id)))

        report_msg = await message.channel.send(embed=report)
        reports_channel = client.get_channel(447415093592981548)
        await reports_channel.send(embed=report)
        await asyncio.sleep(15)
        await report_msg.delete()
        await message.delete()           

    if message.content.upper().startswith("!APPROVE"): #!approve ReportID | Reason
        if "Staff" in [role.name for role in message.author.roles] or "Trusted User" in [role.name for role in message.author.roles]:
            await message.delete()
            args = message.content.split()
            rp_args = message.content.split("|")
            approvals = db_query("reports.db", "SELECT approvals FROM reports WHERE db_id = %s" % (args[1]))[0][0] + 1
            status = db_query("reports.db", "SELECT status FROM reports WHERE db_id = %s" % (args[1]))[0][0]
            if not status.upper() == "PENDING":
                return False
            check = db_query("reports.db", "SELECT report_id FROM approvals WHERE user_id = %s AND report_id = %s" % (message.author.id, args[1]))  
            if not len(check) == 0:
                return False
            execute_query("reports.db", "UPDATE reports SET approvals = %s WHERE db_id = %s" % (str(approvals), args[1]))
            apEmbed = discord.Embed(title="Report Approval", description="Report #0%s was approved by %s" % (args[1], message.author.mention), colour=0x55FF55)
            apMsg = await client.get_channel(447415093592981548).send(embed=apEmbed)
            await message.channel.send("Report Approved")
            execute_query("reports.db", "INSERT INTO approvals (user_id, report_id) VALUES (%s, %s)" % (message.author.id, args[1]))
            if "Staff" in [role.name for role in message.author.roles] or approvals >= 5:
                execute_query("reports.db", "UPDATE reports SET status = 'Approved' WHERE db_id = %s" % (args[1]))
                cmd_channel = client.get_channel(439487832827101195)
                try:
                    user = discord.utils.get(message.guild.members, id=db_query("reports.db", "SELECT offender_id FROM reports WHERE db_id = %s" % (args[1]))[0][0])
                    reason = db_query("reports.db", "SELECT reason FROM reports WHERE db_id = %s" % (args[1]))[0][0]
                    rp_reason = "[REPORT #0" + args[1] + "] " + reason
                    await cmd_channel.send("!kick %s %s" % (user.mention, rp_reason))
                    apEmbed= discord.Embed(title="Report Approved", description="Report #0%s has been marked as accepted" % (args[1]), colour=0x55FF55)
                    apMsg = await client.get_channel(447415093592981548).send(embed=apEmbed)
                except:
                    pass

    if message.content.upper().startswith("!RPINFO"):
        await message.delete()
        args = message.content.split()
        report_info = db_query("reports.db", "SELECT offender_id, reporter_id, reason, evidence, status, approvals FROM reports WHERE db_id = %s" % args[1])
        offenderID = report_info[0][0]
        reporterID = report_info[0][1]
        reason = report_info[0][2]
        evidence = report_info[0][3]
        status = report_info[0][4]
        approvals = report_info[0][5]

        report = discord.Embed(title="Report #0%s" % (args[1]), description="Report Info:", colour=0xFFAA00)
        report.add_field(name="Offender", value="<@%s>" % (str(offenderID)), inline=False)
        report.add_field(name="Reporter", value="<@%s>" % (str(reporterID)), inline=False)
        report.add_field(name="Reason", value="%s" % (str(reason)), inline=False)
        report.add_field(name="Evidence", value="%s" % (str(evidence)), inline=False)
        report.add_field(name="Status", value="%s" % (str(status)), inline=False)
        report.add_field(name="Approvals", value="%s" % (str(approvals)), inline=False)
        report.set_footer(text="This bot is not capable of enforcing Discord Terms of Service but may submit statistical data to Trust & Safety using data collected by Guardian")
        output = await message.channel.send(embed=report)
        await asyncio.sleep(15)
        await output.delete()

    if message.content.upper().startswith("!CLOSE"):
        if "Staff" in [role.name for role in message.author.roles]:
            await message.delete()
            args = message.content.split()
            reason = " ".join(args[2:])
            execute_query("reports.db", "UPDATE reports SET status = 'Closed - %s' WHERE db_id = %s" % (reason, args[1]))
            apEmbed = discord.Embed(title="Report Closed", description="Report #0%s was closed by %s" % (args[1], message.author.mention), colour=0x55FF55)
            apMsg = await client.get_channel(447415093592981548).send(embed=apEmbed)
            
        
        
        
            
            
    if message.content.upper().startswith("!RESETWEEKLY"):
        if message.author.id == 432329360863920148:
            execute_query("users.db", "UPDATE users SET message_weekly = 0")

    if message.content.upper().startswith('!CREATE_USERS'):
        if message.author.id == 432329360863920148: 
            bot_message = await message.channel.send("Creating...")
            for user in message.guild.members:
                create_user(user)
            await message.channel.send("Done")

    if message.content.upper().startswith('!SUBMIT'):
        args = message.content.split()
        submit_flag = args[1]
        if submit_flag == flag:
            em = discord.Embed(title="Owned:", description="%s has owned the %s challenge!" % (message.author.name, challenge), colour=0xFFAA00)
            channel = client.get_channel(439465475265658891)
            await channel.send(embed=em)
        else:
            em = discord.Embed(title="Invalid Flag!", description="Oof! What a bummer! Try Harder! {---8-}", colour=0xFF5555)
            await message.channel.send(embed=em)
        await message.delete()
            

    if message.content.upper().startswith("!SETFLAG"):
        if message.author.id == 432329360863920148: #Should make this role based instead of user based
            args = message.content.split()
            flag = " ".join(args[1:])

    if message.content.upper().startswith("!SETCHAL"):
        if message.author.id == 432329360863920148: #ditto
            args = message.content.split()
            challenge = " ".join(args[1:])

'''THERE IS ANOTHER COMMAND HERE, THAT IS UNFINISHED, BUT ALSO GIVES MASSIVE HINTS TOWARDS THE ERRORS CHALLENGE AND THEREFORE IS BEING KEPT HIDDEN FOR NOW''' 

    if message.author.id in cooldowns:
        pass
    else:
        cooldowns.append(message.author.id)
        author = message.author
        current = db_query("users.db", "SELECT message_weekly FROM users WHERE user_id = '%s'" % (str(author.id)))
        if len(current) == 0:
            create_user(message.author)
            current = 0
        else:
            current = current[0][0]
        new = int(current) + 1
        execute_query("users.db", "UPDATE users SET message_weekly = %s WHERE user_id = '%s'" % (str(new), str(author.id)))
        await asyncio.sleep(60)
        cooldowns.remove(message.author.id)
        #There has to be an easier way of doing this, this is going to get really inefficient when the server starts racking up members. Probably the cause of the Memeory Leak as well. 

client.run("NTI1NjU3MTE5ODgyNjA4NjQw.D3QcVw.vFdC49Pf_1Jm3STt_rGU2m2vHNw") #SECRET
