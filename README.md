# MLR Elections Bot
This bot was written to run any of the MLR elections that have an approve/disapprove ranking system. The bot only responds to DMs, storing the results to the given Google Sheet.

## User Commands
The bot operates on several commands: list, abstain, approve, disapprove, ballot, and info

### -list
Usage: `-list`
Sends the user a list of candidates, prefixed by letters in alphabetical order.

### -abstain
Usage: `-abstain <list:str>`
- list: Any string of alphanumeric characters
Any matching characters in *list* to prefix letters in list/ballot are marked as "abstain" for the user.

### -approve
Usage: `-approve <list:str>`
- list: Any string of alphanumeric characters
Any matching characters in *list* to prefix letters in list/ballot are marked as "approve" for the user.

### -disapprove
Usage: `-disapprove <list:str>`
- list: Any string of alphanumeric characters
Any matching characters in *list* to prefix letters in list/ballot are marked as "disapprove" for the user.

### -ballot
Usage: `-ballot`
Sends the user their current ballot, reflecting the abstain/approve/disapprove for each candidate.

### -info
Usage: `-info`
If there is an active election, the bot sends the user information about the election: when it started, when it ends, and how many ballots have been cast.

## Controller Commands
The bot has several commands that a controller can use, verified by using the correct password.

### -start
Usage: `-start <password:str> <date:str>`
- password: A string of alphanumeric characters without any whitespace
- date: A string of alphanumeric characters to indicate a date
The bot will check that *password* is correct, then sets the start date by using *date* and attempting to parse that into a real date, setting the start time to noon Eastern on that day.

### -end
Usage: `-end <password:str>`
- password: A string of alphanumeric characters without any whitespace
The bot will check that *password* is correct, then immediately end the election.

## Administrator Commands
The bot has several commands that an administrator can use. Administrators are set in the `ADMIN_USER` variable.

### -servers
Usage: `-servers`
Shows a list of servers the bot is connected to.

### -leave_server
Usage: `-leave_server <name:str>`
- name: The name of a server the bot is connected to
The bot will leave the server given.

## Google Sheet
The bot needs a Google sheet with the following tabs and columns:

### `Votes` tab
Columns:
- A: Timestamp
- B: Discord Username
- C through ?: The name of a candidate, one name per column. This list is where the bot pulls the names each time.

### `Log` tab
Columns:
- A: Timestamp
- B: Discord Username
- C: Command
- D: Arguments
- E: Bot Reply

## Bot Dependencies
- Minimum Python version is 3.7 or higher
- The following libraries are required
  - datetime
  - discord
  - gspread
  - csv
