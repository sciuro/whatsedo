from willie import module
import time

# Variables
def setup(bot):
    """
    Setup all the variables
    """
    global players, game, settings, solution, locations
    
    players = []
    game = {}
    game['status'] = 0
    game['awnser'] = 0
    game['round'] = 0
    game['awnserok'] = []
    game['solved'] = []
    settings = {}
    settings['minplayers'] = int(bot.config.whatsedo.minplayers)
    settings['channel'] = bot.config.core.channels
    settings['wa_user'] = bot.config.whatsedo.whatsappuser
    settings['admin'] = bot.config.core.owner
    settings['walktime'] = int(bot.config.whatsedo.walktime)
    settings['playtime'] = int(bot.config.whatsedo.playtime)
    settings['gamequestion'] = bot.config.whatsedo.gamequestion
    solution = {
    'person':bot.config.whatsedo.person,
    'place':bot.config.whatsedo.place,
    'weapon':bot.config.whatsedo.weapon
    }
    locations = {
    1:['Vredenburg/uitgang Catharijne', 'Een camera kijkt hier uit op een bord wat meestal (niet hier) info over Utrecht staat. Wat is zijn ID nummer?', 'mu01326', 'Op het Neude werd iemand met gif vermoord, maar niet door Crofts'],
    2:['Zandbrug', 'Deze brug bevat een oude Duitse bunker. Echter in de 80 jarige oorlog was er hier ook een verzetsvrouw. In welk jaar gaf ze de opdracht kasteel Vredenburg te slopen?', '1577', 'Beatrix was in de stationshal, maar niet met het touw'],
    3:['Domplein', 'Jan van Nassau (broer van Willem van Oranje) was 1 van de oprichters van de Unie van Utrecht, het begin van het huidige Nederland. In welke zaal werd dit verdrag getekend?', 'kapittelzaal', 'Op het Domplein lag geen pistool'],
    4:['Sonnenborgh - Museum & Sterrenwacht', 'Deze sterrenwacht werd samen met het KNMI door wie opgericht? (twee woorden)', 'buys ballot', 'Van Krimpen was op het domplein, zonder touw.'],
    5:['Louis Hartlooper Complex (Tolsteegbrug)', 'Waarmee ondertekende de persoon die ook schreef: ANNO DOMINI MIXD', 'sdj95', 'Labre had dynamiet, echter niet op de mariaplaats.'],
    6:['Klein park achter Tivoli Oude Gracht', 'Er staat hier een oud pandhuis (bank van leningen). Wat was voor 1713 de functie van dit gebouw? (1 woord)', 'graanpakhuis', 'Op het vredenburg lag dynamiet. Masselman was op het Neude.']
    }


# Make the good guys better
@module.event('JOIN')
@module.rule(r'.*')
def autoop(bot, trigger):
    """
    If the user is the admin, he will be oped.
    """
    global settings
    
    nick = trigger.nick

    if nick == settings['admin']:
        channel = trigger.sender
        bot.write(['MODE', channel, "+o", nick])

@module.rule('gameintro')
def gameintro(bot, trigger):
    """
    Give an intro of the game and how to participate.
    """
    global game, settings

    channel = settings['channel']

    if game['status'] == 0 and settings['channel'] in bot.channels:
        bot.msg(channel, 'Welkom bij het spel LGedo. Meld je aan door in deze groeps WhatsApp te antwoorden met "speelmee". Je speelt dan met je team mee.')

@module.rule('<(.*)>\s\Dpeelmee')
def groupadd(bot, trigger):
    """
    Add a group to the players list. If there are enough (same as amount of locations)
    """
    global settings, players, locations

    channel = settings['channel']

    if game['status'] == 1:
        bot.msg(channel, 'Het spel is al begonnen. Je kunt niet meer mee doen.')
        return

    if len(players) == len(locations):
       bot.msg(channel, 'Er zijn genoeg groepjes. Jullie kunnen niet meer mee doen.')
       return

    newplayer =  trigger.group(1)
    
    if players.count(newplayer) == 0:
        players.append(newplayer)
        bot.msg(channel, 'Het groepje met als teamcaptain ' + newplayer + ' doet mee aan het spel!')

@module.rule('startspel')
def startcheck(bot, trigger):
    """
    Check the game requirements.
    """
    global settings, players

    nick = trigger.nick
    channel = settings['channel']

    if game['status'] == 1:
        bot.msg(channel, 'Het spel is al begonnen.')
        return

    if len(players) >= settings['minplayers']:
        startgame(bot)
    else:
        bot.msg(channel, 'Minimum aantal spelers nog niet bereikt. Dit moeten er minimaal ' + str(settings['minplayers']) + ' zijn.')

@module.rule('<(.*)>\s\Dntwoord\s(.*)')
def awnser(bot, trigger):
    """
    Let the players give an awnser to the questions given in the game.
    """
    global settings, players, game, locations

    player =  trigger.group(1)
    awnser =  trigger.group(2)
    channel = settings['channel']

    if game['status'] == 0:
        bot.msg(settings['wa_user'], player + ': Het spel is nog niet begonnen. Je kunt geen antwoorden insturen.')
        return 

    if game['awnser'] == 0:
        bot.msg(settings['wa_user'], player + ': Je kunt op dit moment geen antwoorden insturen.')
        return 

    if players.count(player) == 0:
        bot.msg(settings['wa_user'], player + ': Je speelt niet mee.')
        return

    if game['awnserok'].count(player) == 1:
        return

    loccounter = players.index(player) + game['round']
    if loccounter > len(locations):
        loccounter = loccounter - len(locations)
    
    if awnser == locations[loccounter][2]:
        game['awnserok'].append(player)
        bot.msg(settings['wa_user'], player + ': Goed')
        bot.msg(settings['wa_user'], player + ': Aanwijzing ' + str(game['round']) + ': ' + locations[loccounter][3])
        bot.msg(channel, 'De groep van ' + player + ' heeft een goed antwoord gegeven.')
    else:
        bot.msg(settings['wa_user'], player + ': Fout')

@module.rule('<(.*)>\s\Dplossing\s(.*)\s(.*)\s(.*)')
def gamesolution(bot, trigger):
    """
    Let the players give the solution to the main question of the game.
    """
    global settings, players, game, locations, solution

    player =  trigger.group(1)
    person =  trigger.group(2)
    place = trigger.group(3)
    weapon = trigger.group(4)
    channel = settings['channel']

    if game['status'] == 0:
        bot.msg(settings['wa_user'], player + ': Het spel is nog niet begonnen. Je kunt geen oplossing insturen.')
        return

    if players.count(player) == 0:
        bot.msg(settings['wa_user'], player + ': Je speelt niet mee.')
        return

    if game['solved'].count(player) == 1:
        return

    if person == solution['person'] and place == solution['place'] and weapon == solution['weapon']:
        game['solved'].append(player)
        bot.msg(settings['wa_user'], player + ': Dat is het goede antwoord!')
        bot.msg(channel, 'De groep van ' + player + ' heeft de complete zaak opgelost. Als ze er nog niet zijn, zijn ze nu onderweg naar het eindpunt.')
    else:
        bot.msg(settings['wa_user'], player + ': Dat is niet goed.')
        bot.msg(channel, 'De groep van ' + player + ' heeft de verkeerde oplossing gegeven. ' + person + ' , ' + place + ' , ' + weapon + ' is niet het goede antwoord.' )

# Not user-callable functions
def startgame(bot):
    """
    Start the game itself.
    """
    global settings, players, game

    channel = settings['channel']
    game['status'] = '1'

    bot.msg(channel, 'We beginnen het spel! Er spelen ' + str(len(players)) + ' groepjes mee.')

    for player in players:
        bot.msg(settings['wa_user'], player + ': In deze persoonlijke chat krijg je de opdrachten voor je groep. Geef ook alleen maar antwoord in deze chat en niet in de groepswhatsapp. De groepswhatsapp kan iedereen lezen. Mocht je de oplossing van het spel weten, dan stuur je het volgende bericht: "oplossing <naam> <plaats> <wapen>" Daarna ga je naar de moordplek toe.')

    bot.msg(channel, settings['gamequestion'])

    for count in locations:
        round(bot)

    bot.msg(channel, 'Dit waren alle aanwijzingen. Hiermee zullen jullie het moeten doen.')

def stopgame(bot, trigger):
    """
    Ends the game and reset all the variables.
    """
    global settings, players, game

    nick = trigger.nick
    channel = settings['channel']

    if game['status'] == 0:
        bot.msg(channel, 'Het spel was nog niet begonnen.')
        return

    bot.msg(channel, 'Het spel is gestopt en gereset.')

    players = []
    game['status'] = 0
    game['round'] = 0
    game['awnserok'] = []
    game['solved'] = []

def round(bot):
    """
    Play one round.
    """
    global settings, players, game, locations

    game['round'] = game['round'] + 1
    channel = settings['channel']

    bot.msg(channel, 'Ronde: ' + str(game['round']))

    counter = 1
    for player in players:
        loccounter = counter + game['round'] - 1
        if loccounter > len(locations):
            loccounter = loccounter - len(locations)

        bot.msg(settings['wa_user'], player + ': De lokatie waar jullie naar toe moeten is: ' + locations[loccounter][0] + '. Hiervoor hebben jullie ' + str(settings['walktime']) + ' minuten de tijd. Over ' + str(settings['walktime']) + ' minuten hoor je weer van mij.')
        counter = counter + 1

    time.sleep(settings['walktime'] * 60)

    game['awnser'] = 1

    counter = 1
    for player in players:
        loccounter = counter + game['round'] - 1
        if loccounter > len(locations):
            loccounter = loccounter - len(locations)

        bot.msg(settings['wa_user'], player + ': Stuur het antwoord als volgt: "antwoord <jullie antwoord>". Jullie hebben ' + str(settings['playtime']) + ' minuten de tijd voor het antwoord.')
        bot.msg(settings['wa_user'], player + ': Vraag ' + str(game['round']) + ': ' + locations[loccounter][1])
        counter = counter + 1

    time.sleep(settings['playtime'] * 60)

    for player in players:
        bot.msg(settings['wa_user'], player + ': Einde van ronde: ' + str(game['round']) + '. Antwoorden kunnen niet meer ingestuurd worden.')

    game['awnser'] = 0
    game['awnserok'] = []
