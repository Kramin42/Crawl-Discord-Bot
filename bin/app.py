import discord
import asyncio
import time
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
cheichannel = None

def get_vanity_roles(message):
    bot_role = [r for r in message.server.me.roles if r.name=="Bot"]
    if len(bot_role)==0: return []
    else: bot_role = bot_role[0]
    return [r for r in message.server.roles if not r.is_everyone and r.permissions==message.server.default_role.permissions and r.position<bot_role.position]

@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    sys.stdout.flush()

@client.event
@asyncio.coroutine
def on_error(event, *args, **kwargs):
    print(event, args, kwargs)
    sys.stdout.flush()

@client.event
@asyncio.coroutine
def on_message(message):
    #print(message.content)
    if message.author == client.user: # don't reply to yourself
        if message.content[0] == '%': # special case, if it looks like a chei command, relay it
            print('relaying my own message to chei')
            global cheichannel
            cheichannel = message.channel
            yield irc_client.message('Cheibriados', message.content)
        return
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
    
    if message.content.startswith('%'):
        global cheichannel
        cheichannel = message.channel
        yield irc_client.message('Cheibriados', message.content)
    
    if message.content.startswith('$zxcdance'):
        tmp = yield from client.send_message(message.channel, '└[^_^]┐')
        for i in range(2):
            time.sleep(0.1)
            yield from client.edit_message(tmp, '┌[^_^]┘')
            time.sleep(0.1)
            yield from client.edit_message(tmp, '└[^_^]┐')
    
    if message.content.startswith('$dance'):
        tmp = yield from client.send_message(message.channel, ':D|-<')
        for i in range(1):
            time.sleep(0.1)
            yield from client.edit_message(tmp, ':D/-<')
            time.sleep(0.1)
            yield from client.edit_message(tmp, ':D|-<')
            time.sleep(0.1)
            yield from client.edit_message(tmp, ':D\\\\-<')
            time.sleep(0.1)
            yield from client.edit_message(tmp, ':D|-<')
    
    pieces = message.content.strip().split(' ')
    if pieces[0] == '$listroles' and message.server!=None:
        vanity_roles = get_vanity_roles(message)
        yield from client.send_message(message.channel, ', '.join(r.name for r in vanity_roles))
    
    if pieces[0] == '$addrole' and message.server!=None:
        vanity_roles = get_vanity_roles(message)
        new_role_name = ' '.join(pieces[1:])
        matches = [r for r in vanity_roles if r.name==new_role_name]
        if len(matches)>0:
            yield from client.add_roles(message.author, matches[0])
            yield from client.send_message(message.channel, 'Member %s has been given role %s' % (message.author.name, matches[0].name))
        else:
            yield from client.send_message(message.channel, 'Role does not exist: %s' % new_role_name)
    
    if pieces[0] == '$removerole' and message.server!=None:
        vanity_roles = get_vanity_roles(message)
        new_role_name = ' '.join(pieces[1:])
        matches = [r for r in vanity_roles if r.name==new_role_name]
        if len(matches)>0:
            role = matches[0]
            if role in message.author.roles:
                yield from client.remove_roles(message.author, role)
                yield from client.send_message(message.channel, 'Member %s has lost role %s' % (message.author.name, role.name))
            else:
                yield from client.send_message(message.channel, 'Member %s does not have role %s' % (message.author.name, role.name))
        else:
            yield from client.send_message(message.channel, 'Role does not exist: %s' % new_role_name)
    
    if pieces[0]=='$glasses':
        # ( •_•)    ( •_•)>⌐■-■    (⌐■_■)
        tmp = yield from client.send_message(message.channel, '( •_•)')
        time.sleep(1)
        yield from client.edit_message(tmp, '( •_•)>⌐■-■')
        time.sleep(1)
        yield from client.edit_message(tmp, '(⌐■_■)')
    
    if pieces[0]=='$deal':
        glasses ='    ⌐■-■    '
        glasson ='   (⌐■_■)   '
        dealwith='deal with it'
        lines = ['            ',\
                 '            ',\
                 '            ',\
                 '    (•_•)   ']
        tmp = yield from client.send_message(message.channel, '```%s```' % '\n'.join(lines))
        time.sleep(1)
        yield from client.edit_message(tmp, '```%s```' % '\n'.join([glasses]+lines[1:]))
        time.sleep(1)
        yield from client.edit_message(tmp, '```%s```' % '\n'.join(lines[:1]+[glasses]+lines[2:]))
        time.sleep(1)
        yield from client.edit_message(tmp, '```%s```' % '\n'.join(lines[:2]+[glasses]+lines[3:]))
        time.sleep(1)
        yield from client.edit_message(tmp, '```%s```' % '\n'.join(lines[:1]+[dealwith]+lines[2:3]+[glasson]))
    sys.stdout.flush()
    sys.stderr.flush()

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
            print(message.encode('utf-8'))
            super().on_message(target, source, message)
            
            message = clrstrip.sub('', message)
            
            if source=='Sequell':
            	msgarray = message.split(':')
            	serv = msgarray[0]
            	chanid = msgarray[1]
            	msg = ':'.join(msgarray[2:])
            	
            	url_regex = '(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)'
            	#msg_urls = re.findall(url_regex, msg)
            	msg_split = re.split(url_regex, msg)
            	
            	for mdchar in ['\\','*','_','~','`']:
            	    for i in range(0,len(msg_split),2):
            	        msg_split[i] = msg_split[i].replace(mdchar,'\\'+mdchar)
            	    #msg_wo_ulrs = msg_wo_ulrs.replace(mdchar,'\\'+mdchar)
            	
            	#msg = msg_wo_ulrs.format(*msg_urls)
            	msg = ''.join(msg_split)
            	
            	if msg[:3]=='/me':
            	    msg = '*'+msg[3:].strip()+'*'
            	#msg = msg.replace('/me','*'+client.user.name+'*')
            	
            	if re.search('\[\d\d?/\d\d?\]:', msg):
            	    s = re.split('(\[\d\d?/\d\d?\]:)', msg)
            	    #msg = s[0] + s[1] + '```\n' + ''.join(s[2:]).strip() + '\n```' # put only the content of the ?? in a block
            	    msg = s[0] + s[1] + '\n' + ''.join(s[2:]).strip()
            	else:
            	    #msg = '```\n' + msg + '\n```' # put in a code block to preserve formatting
            	    msg = msg
            	if serv=='discord':
            		yield from client.send_message(client.get_channel(chanid), msg)
            
            if source=='Gretell':
                yield from client.send_message(gretellchannel, '```'+message+'```')
            
            if source=='Cheibriados':
                yield from client.send_message(cheichannel, '```'+message+'```')

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
