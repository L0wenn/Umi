# THE PROJECT IS ABANDONED. IF YOU'RE GONNA USE THIS CODE, TAKE A NOTE THAT THE IT MIGHT NOT WORK DEPENDING ON DISCORD API CHANGES

# Mint
Mint is a Discord bot made out of pure curiosity about programming around 2-3 years ago. As a revived project, Mint is now ready to serve in providing moderation, fun and social features!

## Features:
* Moderation commands to keep your server nice and tidy
* Social (Leveling, Currency)
* Anime pictures and gifs (seriosly, try `neko` it's posts very cute nekos)
* Gelbooru
* Commands to spice up the server with memes
* And other stuff I'm lazy to list myself, so you better to [invite the bot](https://discord.com/oauth2/authorize?client_id=424862035063603202&scope=bot&permissions=2146958839) and see it for yourself!

## If you want to self host:
* Create python virtual environment (optional)
* Install requirements by using `pip3 install -r requirements.txt`
* Create `.env` file in bot's directory and put your bot's token(TOKEN) and Atlas MongoDB database url(MONGODB_URI) in it
* Run bot by `python main.py`

## Todo List for now:

- [x] Rewrite database.py and modules that use it (Moved to MongoDB)
- [x] Get a better hosting
- [x] Add more features to social.py
- [x] Make event handling process better
- [x] Make leveling related graphics
- [ ] Create a dashboard website for changing bot's settings easily (In Progress)
- [ ] Create a separate API for the bot (In Progress)
- [ ] Refactor the code (ugh)


