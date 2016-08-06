import discord
import asyncio
import os
import sys, traceback
import threading
import re

# Discord part

TOKEN = os.getenv('TOKEN') or 'my-discord-token'
EMAIL = os.getenv('EMAIL') or 'bot@dogood.com'
PASSWORD = os.getenv('PASSWORD') or 'secret'

client = discord.Client()
irc_client = None

gretellchannel = None

@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
@asyncio.coroutine
def on_message(message):
    nick = str(message.author).split('#')[0]
    if message.content[0] in ['!','.','=','&','?','^']:
        #yield from client.send_message(message.channel, '%s wants his !lg' % nick)
        #yield irc_client.message('##kramell', '%s used !lg in discord channel %s' % (nick, message.channel))
        # '!RELAY -n 1 -channel ' + (pm ? 'msg' : chan) + ' -nick ' + nick + ' -prefix ' + chan + ':' + ' ' + message
        forsequell = '!RELAY -n 1 -channel %s -nick %s -prefix discord:%s: %s' % ('c-a#'+message.channel.name, nick, message.channel.id, message.content)
        print(forsequell)
        yield irc_client.message('Sequell', forsequell)
    if message.content.startswith('@?'):
        global gretellchannel
        gretellchannel = message.channel
        yield irc_client.message('Gretell', message.content)
        
    if message.content.startswith('$dance'):
        tmp = yield from client.send_message(message.channel, ':D|-<')
        for i in range(2):
            yield from client.edit_message(tmp, ':D/-<')
            yield from client.edit_message(tmp, ':D|-<')
            yield from client.edit_message(tmp, r':D\-<')
            yield from client.edit_message(tmp, ':D|-<')

# IRC part
import pydle

ADMIN_NICKNAMES = [ 'Kramin', 'Kramin42']

clrstrip = re.compile("\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)

class MyClient(pydle.Client):
    """
    This is a simple bot that will tell you if you're an administrator or not.
    A real bot with administrative-like capabilities would probably be better off maintaining a cache
    that would be invalidated upon parting, quitting or changing nicknames.
    """

    def on_connect(self):
        super().on_connect()
        self.join('##kramell')

    @pydle.coroutine
    def is_admin(self, nickname):
        """
        Check whether or not a user has administrative rights for this bot.
        This is a blocking function: use a coroutine to call it.
        See pydle's documentation on blocking functionality for details.
        """
        admin = False

        # Check the WHOIS info to see if the source has identified with NickServ.
        # This is a blocking operation, so use yield.
        
        if nickname in ADMIN_NICKNAMES:
            info = yield self.whois(nickname)
            admin = info['identified']
        
        return admin

    @pydle.coroutine
    def on_message(self, target, source, message):
        try:
            print(message)
            super().on_message(target, source, message)
            
            message = clrstrip.sub('', message)
            
            if source=='Sequell':
            	msgarray = message.split(':')
            	serv = msgarray[0]
            	chanid = msgarray[1]
            	msg = ':'.join(msgarray[2:])
            	if re.search('\[\d\d?/\d\d?\]:', msg):
            	    s = re.split('(\[\d\d?/\d\d?\]:)', msg)
            	    msg = s[0] + s[1] + '```\n' + ''.join(s[2:]).strip() + '\n```' # put only the content of the ?? in a block
            	else:
            	    msg = '```\n' + msg + '\n```' # put in a code block to preserve formatting
            	if serv=='discord':
            		yield from client.send_message(client.get_channel(chanid), msg)
            
            if source=='Gretell':
                yield from client.send_message(gretellchannel, '```'+message+'```')

            # Tell a user if they are an administrator for this bot.
            if message.startswith('!adminstatus'):
                admin = yield self.is_admin(source)
                if admin:
                    self.message(target, '%s: You are an administrator.' % source)
                else:
                    self.message(target, '%s: You are not an administrator.' % source)
        except Exception:
            print("Exception irc thread:")
            traceback.print_exc(file=sys.stdout)



# run discord client in a thread
#client.run(TOKEN)
#client.login(EMAIL, PASSWORD)
def start_discord():
    print("Starting Discord thread...")
    discord_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(discord_loop)
    client.run(TOKEN)

discord_thread = threading.Thread(target=start_discord)
discord_thread.start()

# run irc client
def start_irc():
    print("Starting IRC thread...")
    global irc_client
    irc_client = MyClient('KramellDiscord')
    irc_client.connect('chat.freenode.net', tls=True)
    irc_client.handle_forever()

irc_thread = threading.Thread(target=start_irc)
irc_thread.start()

# website part starts here
# urls = (
#   '/', 'index'
# )

# app = web.application(urls, globals())

# render = web.template.render('templates/')

# class index:
#   def GET(self):
#       greeting = "Hello World"
#       return render.index(greeting = greeting)

# if __name__ == "__main__":
#   app.run()
