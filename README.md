## v3 Rewrite in progress
# Katoku v2 formally known as SSCBot
A Discord bot which does things.

Specifically for the TpF community with the global server being the focus.

# Functions
- Log when messages are deleted, members join/leave/change-nick, etc.
- React to things.
- Provide info about members and guilds.
- Provide links to the TpF wikis.
- Create mod previews for the Steam Workshop, and Nexusmods. tpf|net is WIP.
These previews can also be automagically sent to the global server from the regional server.
- Provide random facts.
- And a bunch more.

# Localisation
As of v2.7, it has localisation of most functions.
I ask any who can translate to please help out by providing a translation.
The GNU gettext standard is used.
So for new translations, grab the base.pot file and open it in PoEdit.
Create new translation and pick a language that's recognised by Discord/Nextcord to create a new base.po file.
https://docs.nextcord.dev/en/stable/api.html#nextcord.Locale

If wishing to update an existing translation.
Grab the base.po file from the locale folder and open it with PoEdit.
Please take note of the comments.

Once finished, please either send the .po file directly to me or via a pull request.
 
Please note that a complete translation is not required but any missing strings will be substituted with English.
 
 # Notes
I don't test on on Windows, so YMMV.

Currently the working directory must be the bot's folder (where bot.py is).

# Contributors
## Code
- APasz (Creator)
## Locale
- APasz (English obviously)
