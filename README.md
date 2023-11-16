# MLR Elections Bot
This bot was written to run any of the MLR elections that have an approve/disapprove ranking system. The bot only responds to DMs, storing the results to the given Google Sheet.

## User Commands
The bot operates on four commands: list, approve, disapprove, and ballot

### -list
Usage: `-list`
Sends the user a list of candidates, prefixed by letters in alphabetical order.

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
Sends the user their current ballot, reflecting the approve/disapprove for each candidate.

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