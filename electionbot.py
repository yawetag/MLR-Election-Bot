import csv
import datetime
import discord
import gspread
import json
import pytz
import time
from dateutil import parser
from discord.ext import commands
from discord.ext.commands import Bot
from gspread import Cell

##### DISCORD INFO ############################################################
TOKEN = "token here"
###############################################################################

##### GOOGLE INFORMATION ######################################################
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
GOOGLE_AUTH = 'auth JSON here'
GOOGLE_SHEET = "sheet reference here"

GOOGLE_TABS = {
    "votes" : "Votes",
    "log" : "Log",
}
###############################################################################

##### GLOBAL VARIABLES ########################################################
PASSWORD = "password here"
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
IGNORE_HEADERS = [
    "UNIX Timestamp",
    "Discord Snowflake",
    "MLR Player Name"
]

PLAYERS = {item['discordID']:item for item in json.load(open('players.json','r'))}
###############################################################################

##### DISCORD BOT SETUP #######################################################
intents = discord.Intents.default()
intents.guild_messages = False      # Make bot only reply to DMs.
intents.message_content = True
activity = discord.Activity(type=discord.ActivityType.watching, name="LOM Elections")
bot = Bot(command_prefix="-", intents=intents, activity=activity)
###############################################################################

##### FUNCTIONS ###############################################################
def start_func(ctx, pw, start_date):
    '''Starts the election if the password is correct.'''
    
    # Check password
    if pw != PASSWORD:  # If the password is incorrect, let the user know
        return f"{ctx.author.mention} : You provided an incorrect password."
    
    # If the password is correct, try turning the start_date string into an actual date
    try:
        d = parser.parse(start_date, fuzzy=True).date()
    except:
        return f"{ctx.author.mention} : You did not provide a date in your response."
    
    # Since we have a date, let's convert to Unix timestamp
    tz = pytz.timezone('America/New_York')
    d = tz.localize(datetime.datetime(d.year, d.month, d.day, 12, 0, 0))
    unix_date = int(d.timestamp())

    # Write time to start.csv
    with open(f'start.csv', 'w') as f:
        f.write(str(unix_date))

    return f"{ctx.author.mention} : You have started the election on <t:{unix_date}:f> in your timezone."

def end_func(ctx, pw):
    '''Ends the election if the password is correct.'''

    # Check password
    if pw != PASSWORD:  # If the password is incorrect, let the user know
        return f"{ctx.author.mention} : You provided an incorrect password."
    
    # If the password is correct, remove the value in start.csv
    with open(f'start.csv', 'w') as f:
        f.write(str(0))

    return f"{ctx.author.mention} : The election has ended immediately."

def ballot_get(ctx):
    '''Finds ballot for user.'''
    # Get all ballots
    all_ballots = ballot_get_all()

    # Get list of candidates
    candidates = all_ballots[0]

    # Check ballots for user's ballot based on Discord Username
    for b in all_ballots:
        if b[1] == str(ctx.author.id):
            return candidates, b
    
    return candidates, None

def ballot_get_all():
    '''Gets all ballots from the sheet.'''
    try:
        gc = gspread.service_account(filename=GOOGLE_AUTH)
        sht1 = gc.open_by_key(GOOGLE_SHEET)
        worksheet = sht1.worksheet(GOOGLE_TABS['votes'])
        return worksheet.get_all_values()
    except:
        print(f"{datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')} : Received error when pulling sheet.")
        return list()

def ballot_display(ctx, candidates, user_ballot, mention=True):
    '''Sends the user's current ballot.'''
    letter = 0

    if user_ballot is None: # If there's no ballot by the user, let them know.
        message = f"{ctx.author.mention} : You do not have a ballot submitted. Here is a list of candidates:"
    else:                   # If there is, give them information on when it was submitted.
        if mention:
            message = f"{ctx.author.mention} : Here is your ballot, last updated on <t:{user_ballot[0]}:f> in your timezone:"
        else:
            message = f"Here is your ballot, last updated on <t:{user_ballot[0]}:f> in your timezone:"
    
    for c in range(len(candidates)):        # Get list of candidates.
        if candidates[c] in IGNORE_HEADERS:     # If the column header is to be ignored, do so.
            continue
        else:                                   # If not, print the candidate and user's choice if they have one.
            message += f"\n     {LETTERS[letter]}. {candidates[c]}"
            if user_ballot is not None:
                message += f"  —  {user_ballot[c]}"
            letter += 1
    
    message += "\nType `-approve <letters>` or `-disapprove <letters>` to vote."

    return message

def dates_get():
    '''Sends the start and end dates of the election.'''

    # Get start time from file
    with open(f'start.csv', 'r') as f:
        start_time = int(f.read())
    
    if start_time == 0:
        return None, None
    else:
        return start_time, start_time+(9*24*60*60)
    
def info_func(ctx, ballot_count, start_date, end_date):
    '''Sends user information about the election.'''
    curr_time = int(time.time())    # Get current time in Unix timestamp

    if start_date is None:          # If the election has no start date
        return 0, f"{ctx.author.mention} : The election has either not started or has ended."
    
    if start_date > curr_time:      # If the election has not started
        return 0, f"{ctx.author.mention} : The election will begin <t:{start_date}:R>, on <t:{start_date}:F> in your timezone"
    
    if end_date <= curr_time:       # If the election has ended
        if ballot_count is None:
            return 0, f"{ctx.author.mention} : The election ended <t:{end_date}:R>, on <t:{end_date}:F> in your timezone."    
        return 0, f"{ctx.author.mention} : The election ended <t:{end_date}:R>, on <t:{end_date}:F> in your timezone. There were {ballot_count} ballots cast."

    # The election is active; give information
    message = f"{ctx.author.mention} : Here is some general information about the election:"
    message += f"\n* The election started <t:{start_date}:R>, on <t:{start_date}:F> in your timezone"
    message += f"\n* The election will end <t:{end_date}:R>, on <t:{end_date}:F> in your timezone"
    message += f"\n* There have been {ballot_count} ballots cast so far."
    
    return 1, message

def vote_func(ctx, type, list):
    '''Votes to approve or disapprove candidates.'''
    gc = gspread.service_account(filename=GOOGLE_AUTH)
    sht1 = gc.open_by_key(GOOGLE_SHEET)
    worksheet = sht1.worksheet(GOOGLE_TABS['votes'])

    if not list:    # If the user didn't provide a list, instruct them
        return f"{ctx.author.mention} : You sent the {type} command without a list. Type `-{type} <list>` to vote."
    
    # Get full list of ballots
    all_ballots = ballot_get_all()

    # Clean up candidate list (row 0)
    candidates = []
    for c in all_ballots[0]:
        if c in IGNORE_HEADERS:
            continue
        candidates.append(c)
    
    # Get user's MLR name
    player_name = get_player_name(ctx)

    cand_list = []
    letter_list = []
    letter = 0
    
    # Go through list of candidates and check letter against list given by user
    for c in candidates:
        if LETTERS[letter] in list.upper():
            letter_list.append(LETTERS[letter])
            cand_list.append(c)
        letter += 1
    
    # Check if the user has voting row already
    vote_row = None
    vote_ballot = None
    for b in range(len(all_ballots)):
        if all_ballots[b][1] == str(ctx.author.id):
            vote_row = b+1
            vote_ballot = all_ballots[b]
            break

    # If user has a vote row, edit it, and update it
    if vote_row:
        # Edit row
        update_vote = []
        update_vote.append(Cell(vote_row, 1, int(time.time())))
        vote_ballot[0] = int(time.time())
        for i in range(len(candidates)):
            if candidates[i] in cand_list:
                update_vote.append(Cell(vote_row, i+4, type))
                vote_ballot[i+3] = type

        # Update row
        worksheet.update_cells(update_vote)
    
    # If user does not have a vote row, append it to the bottom
    else:
        # Edit row
        append_vote = [int(time.time()), str(ctx.author.id), player_name]
        for i in range(len(candidates)):
            if candidates[i] in cand_list:
                append_vote.append(type)
            else:
                append_vote.append("disapprove")        # We assume disapprove if not approved

        # Post row
        vote_ballot = append_vote
        worksheet.append_row(append_vote, table_range="A1:L1")
    
    # Generate the message
    if len(cand_list) > 0:     # If there are any candidates, display the list
        message = f"{ctx.author.mention} : You **{type.upper()}** the following: {', '.join(cand_list)}\n"
        message += ballot_display(ctx, all_ballots[0], vote_ballot, False)
    else:                      # If not, let the user know
        message = f"{ctx.author.mention} : You sent the {type} command without correct letters. Type `-{type} <list>` to vote."
    
    return message

def get_player_name(ctx):
    try:
        player_name = PLAYERS[ctx.author.id]['playerName']
    except:
        player_name = "--- UNKNOWN ---"
    
    return player_name

def log_interaction(ctx, command, arguments, bot_reply, log_type):
    '''Logs interactions to the Google Sheet and/or CSV file (for duplication)'''
    
    log_data = [int(time.time()), str(ctx.author.id), command, arguments, bot_reply.replace('\n', '\\n')]

    # Log to Google Sheet if log_type is sheet, which is only for approve/disapprove interactions
    if log_type == "sheet":
        try:
            gc = gspread.service_account(filename=GOOGLE_AUTH)
            sht1 = gc.open_by_key(GOOGLE_SHEET)
            worksheet = sht1.worksheet(GOOGLE_TABS['log'])
            worksheet.append_row(log_data, table_range="A1:E1")
        except Exception as error:
            print(f"{datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')} : Received error when pulling sheet.")

    # Log to local CSV on all interactions
    with open(f'election_log.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(log_data)
###############################################################################

##### COMMANDS ################################################################

### -start <pw> <date>
###     Starts the election process
@bot.command(hidden=True, brief="Start the election", description="-start <password> <date>\nStarts the election at noon of the given date.")
@commands.cooldown(1, 30, commands.BucketType.default)
async def start(ctx, pw:str="", *, start_date:str=""):
    await ctx.message.add_reaction('👍')                            # Let user know we received the request
    message = start_func(ctx, pw, start_date)                       # Start the election
    log_interaction(ctx, "start", start_date, message, "sheet")     # Log interaction to both files
    await ctx.author.send(message)

### -end <pw>
###     Ends the election process
@bot.command(hidden=True, brief="End the election", description="-end <password> <date>\nEnds the election immediately.")
@commands.cooldown(1, 30, commands.BucketType.default)
async def end(ctx, pw:str=""):
    await ctx.message.add_reaction('👍')                    # Let user know we received the request
    message = end_func(ctx, pw)                             # End the election
    log_interaction(ctx, "end", "", message, "sheet")       # Log interaction to both files
    await ctx.author.send(message)

### -info
###     Gives information about the election
@bot.command(brief="Get election information", description="-info\nGives basic information about the election.")
@commands.cooldown(1, 5, commands.BucketType.user)
async def info(ctx):
    await ctx.message.add_reaction('👍')                                    # Let user know we received the request
    all_ballots = len(ballot_get_all()) - 1                                 # Get count of all ballots (remove the header in the count)
    start_date, end_date = dates_get()                                      # Get start and end dates of the election
    status, message = info_func(ctx, all_ballots, start_date, end_date)     # Get the election information
    log_interaction(ctx, "info", "", message, "csv")                        # Log interaction to CSV file
    await ctx.author.send(message)

### -ballot
###     Sends user their current ballot
@bot.command(brief="View your ballot", description="-ballot\nDisplays your current ballot. If you have no ballot, displays the candidates.")
@commands.cooldown(1, 5, commands.BucketType.user)
async def ballot(ctx):
    await ctx.message.add_reaction('👍')                    # Let user know we received the request
    candidates, user_ballot = ballot_get(ctx)               # Find user's ballot
    message = ballot_display(ctx, candidates, user_ballot)  # Get text to display user's ballot
    log_interaction(ctx, "ballot", "", message, "csv")      # Log interaction to the CSV file
    await ctx.author.send(message)

### -approve <list>
###     Sets vote to "Approve" for the listed candidates
@bot.command(brief="Mark candidate(s) as Approved", description="-approve <approve_list>\nApprove a list of candidates.\nThis list can include any number of letters. (ex: -approve xyz)")
@commands.cooldown(1, 5, commands.BucketType.user)
async def approve(ctx, *, approve_list:str=commands.parameter(default=None, description="List of letters from ballot of candidates to approve.")):
    await ctx.message.add_reaction('👍')                                # Let user know we received the request
    start_date, end_date = dates_get()                                  # Get start and end dates of the election
    status, message = info_func(ctx, None, start_date, end_date)        # Get status of election
    if status == 1:
        message = vote_func(ctx, "approve", approve_list)               # Since election is active, log vote
    log_interaction(ctx, "approve", approve_list, message, "sheet")     # Log the interaction to the sheet
    await ctx.author.send(message)

### -disapprove <list>
###     Sets vote to "Disapprove" for the listed candidates
@bot.command(brief="Mark candidate(s) as Disapproved", description="-disapprove <disapprove_list>\nDisapprove a list of candidates.\nThis list can include any number of letters. (ex: -disapprove xyz)")
@commands.cooldown(1, 5, commands.BucketType.user)
async def disapprove(ctx, *, disapprove_list:str=commands.parameter(default=None, description="List of letters from ballot of candidates to disapprove.")):
    await ctx.message.add_reaction('👍')                                        # Let user know we received the request
    start_date, end_date = dates_get()                                          # Get start and end dates of the election
    status, message = info_func(ctx, None, start_date, end_date)                # Get status of election
    if status == 1:
        message = vote_func(ctx, "disapprove", disapprove_list)                 # Since election is active, log vote
    log_interaction(ctx, "disapprove", disapprove_list, message, "sheet")       # Log the interaction to the sheet
    await ctx.author.send(message)
###############################################################################

##### BOT EVENTS ##############################################################
# When bot boots up, show list of guilds it has joined.
@bot.event
async def on_ready():
    print(f"Logged on as {bot.user.name}")
    print(f"{bot.user} is connected to the following guilds:")
    for guild in bot.guilds:
        print(f"   {guild.name} (id: {guild.id})")
        await bot.tree.sync(guild=discord.Object(id=guild.id))
    
    # Get start time from file
    with open(f'start.csv', 'r') as f:
        start_time = int(f.read())
        if start_time > 0:
            end_time = start_time+(9*24*60*60)
    curr_time = int(time.time())    # Get current time in Unix timestamp

    if start_time == 0:
        print(f"Election is not active.")
    elif start_time > curr_time:
        print(f"The election will run {datetime.datetime.fromtimestamp(start_time)}  —  {datetime.datetime.fromtimestamp(end_time)}")
    elif end_time <= curr_time:
        print(f"The election ended {datetime.datetime.fromtimestamp(end_time)}")
    else:
        print(f"The election is active: {datetime.datetime.fromtimestamp(start_time)}  —  {datetime.datetime.fromtimestamp(end_time)}")

# When bot joins a new guild, let me know.
@bot.event
async def on_guild_join(guild):
    print(f'Bot has been added to: {guild.name} (id: {guild.id})')

# Since the commands are on a cooldown, let's send an error to the user when they trip it.
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.author.send(f"This command is on cooldown for {int(error.retry_after)} second(s).")
    else:
        print(f"An error occurred: {str(error)}")

# Run the bot
bot.run(TOKEN)
###############################################################################