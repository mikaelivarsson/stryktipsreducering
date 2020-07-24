#!/usr/bin/env python3

import urllib.parse
import requests
import urwid
import itertools
from tqdm import tqdm
from operator import eq
import time

maxlikaReduceradlista = []

def handleInput(key):
    if isinstance(key, str):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        if key in ('g', 'G'):
            setGrundrad()
        if key in ('s', 'S'):
            sparaRader()

def sparaRader():
    splittedInfo = infoText.get_text()[0].split()
    filename = "rader/" + type + '_' + splittedInfo[4] + '_' + str(len(maxlikaReduceradlista)) + "_rader_" + str(int(time.time())) + ".txt"
    with open(filename, 'w') as f:
        f.write(type+'\n')
        for rad in maxlikaReduceradlista:
            f.write('E')
            for tecken in rad[0]:
                f.write(',' + tecken)
            f.write('\n')

def getData(type="Stryktipset"):
    f = open("config.txt", 'r')
    key = f.read().replace('\n', '')
    f.close()
    api_url = "https://api.www.svenskaspel.se/external/draw/"
    url = api_url + type.lower() + "/draws?" + urllib.parse.urlencode({"accesskey": key})
    data = requests.get(url).json()
    return data

def getCoupon(data):
    rows = []
    homeTeams = []
    awayTeams = []
    odds = []
    sannolikhet = []
    streck = []
    spelbarhet = []
    oddsString = ""
    streckString = ""
    appendHeader(rows, "Match")
    appendHeader(homeTeams, "Hemmalag - ")
    appendHeader(awayTeams, "Bortalag")
    appendHeader(odds, "Odds")
    appendHeader(sannolikhet, "Sannolikhet")
    appendHeader(streck, "Streck")
    appendHeader(spelbarhet, "Spelbarhetskvot")
    for match in range(13):
        rows.append(str(match+1) + ':\n')
        if data["draws"] != []:
            homeTeams.append(data["draws"][0]["events"][match]["participants"][0]["name"] + ' - \n')
            awayTeams.append(data["draws"][0]["events"][match]["participants"][1]["name"] + '\n')
            oddsList = []
            streckList = []
            if data["draws"][0]["events"][match]["odds"] != None:
                oh = data["draws"][0]["events"][match]["odds"]["home"]
                od = data["draws"][0]["events"][match]["odds"]["draw"]
                oa = data["draws"][0]["events"][match]["odds"]["away"]
            else:
                oh = od = oa = "9,99"
            odds.append(oh + ' ' + od + ' ' + oa + '\n')
            oddsList.append(float(oh.replace(',','.')))
            oddsList.append(float(od.replace(',','.')))
            oddsList.append(float(oa.replace(',','.')))
            oddsString += str(oddsList.index(min(oddsList)))
            shh = int(0.5+100*(1/float(oh.replace(',','.'))) / (1/float(oh.replace(',','.')) + 1/float(od.replace(',','.')) + 1/float(oa.replace(',','.'))))
            shd = int(0.5+100*(1/float(od.replace(',','.'))) / (1/float(oh.replace(',','.')) + 1/float(od.replace(',','.')) + 1/float(oa.replace(',','.'))))
            sha = int(0.5+100*(1/float(oa.replace(',','.'))) / (1/float(oh.replace(',','.')) + 1/float(od.replace(',','.')) + 1/float(oa.replace(',','.'))))
            sannolikhet.append(str(shh) + ' ' + str(shd) + ' ' + str(sha) + '\n')
            sth =  data["draws"][0]["events"][match]["distribution"]["home"]
            std = data["draws"][0]["events"][match]["distribution"]["draw"]
            sta = data["draws"][0]["events"][match]["distribution"]["away"]
            streckList.append(int(sth))
            streckList.append(int(std))
            streckList.append(int(sta))
            streckString += str(streckList.index(max(streckList)))
            streck.append(sth + ' ' + std + ' ' + sta + '\n')
            sph = str("{:.2f}".format(shh/float(sth)))
            spd = str("{:.2f}".format(shd/float(std)))
            spa = str("{:.2f}".format(sha/float(sta)))
            appendText(spelbarhet, sph)
            spelbarhet.append(' ')
            appendText(spelbarhet, spd)
            spelbarhet.append(' ')
            appendText(spelbarhet, spa)
            spelbarhet.append('\n')
            infoText.set_text(data["draws"][0]["drawComment"] + " closes: " + data["draws"][0]["closeTime"][:10] + " " + data["draws"][0]["closeTime"][11:16] + " turnover: " + "{:,}".format(int(data["draws"][0]["turnover"][:-3])))
        else:
            homeTeams.append("Hemmalag - \n")
            awayTeams.append("Bortalag\n")
            odds.append("9,99 9,99 9,99\n")
            sannolikhet.append("33 33 33\n")
            streck.append("33 33 33\n")
            appendText(spelbarhet, "1.00")
            spelbarhet.append(' ')
            appendText(spelbarhet, "1.00")
            spelbarhet.append(' ')
            appendText(spelbarhet, "1.00")
            spelbarhet.append('\n')
            infoText.set_text('')
    oddsString = "Oddsfavoriter:   " + str([char for char in oddsString.replace('1', 'X').replace('0', '1')]).replace('\'','').replace('[','').replace(']','')
    streckString = "Streckfavoriter: " + str([char for char in streckString.replace('1', 'X').replace('0', '1')]).replace('\'','').replace('[','').replace(']','')
    return rows, homeTeams, awayTeams, odds, sannolikhet, streck, spelbarhet, oddsString, streckString

def getColor(s):
    if float(s) < 1:
        return 'bad'
    elif float(s) > 1:
        return 'good'
    else:
        return 'neutral'

def appendHeader(l, s, style='header'):
    l.append((style, s))
    l.append('\n')

def appendText(l, s, color='neutral'):
    color = getColor(s)
    l.append((color, s))

def setType(typeButtons, state):
    if state:
        type = "Stryktipset"
        header.base_widget.set_text("TIPSREDUCERING - " + type)
    else:
        type = "Europatipset"
        header.base_widget.set_text("TIPSREDUCERING - " + type)
    setCoupon(type)

def setCoupon(type="Stryktipset"):
    rows, homeTeams, awayTeams, odds, sannolikhet, streck, spelbarhet, oddsString, streckString = getCoupon(getData(type))
    rowsText.set_text(rows)
    homeTeamsText.set_text(homeTeams)
    awayTeamsText.set_text(awayTeams)
    oddsText.set_text(odds)
    sannolikhetText.set_text(sannolikhet)
    streckText.set_text(streck)
    spelbarhetText.set_text(spelbarhet)
    oddsFavoriter.set_text(oddsString)
    streckFavoriter.set_text(streckString)

def setGrundrad():
    grundtext = "Grundrad: "
    if cb11.get_state():
        grundtext += '1'
    if cb1X.get_state():
        grundtext += 'X'
    if cb12.get_state():
        grundtext += '2'
    grundtext += ', '
    if cb21.get_state():
        grundtext += '1'
    if cb2X.get_state():
        grundtext += 'X'
    if cb22.get_state():
        grundtext += '2'
    grundtext += ', '
    if cb31.get_state():
        grundtext += '1'
    if cb3X.get_state():
        grundtext += 'X'
    if cb32.get_state():
        grundtext += '2'
    grundtext += ', '
    if cb41.get_state():
        grundtext += '1'
    if cb4X.get_state():
        grundtext += 'X'
    if cb42.get_state():
        grundtext += '2'
    grundtext += ', '
    if cb51.get_state():
        grundtext += '1'
    if cb5X.get_state():
        grundtext += 'X'
    if cb52.get_state():
        grundtext += '2'
    grundtext += ', '
    if cb61.get_state():
        grundtext += '1'
    if cb6X.get_state():
        grundtext += 'X'
    if cb62.get_state():
        grundtext += '2'
    grundtext += ', '
    if cb71.get_state():
        grundtext += '1'
    if cb7X.get_state():
        grundtext += 'X'
    if cb72.get_state():
        grundtext += '2'
    grundtext += ', '
    if cb81.get_state():
        grundtext += '1'
    if cb8X.get_state():
        grundtext += 'X'
    if cb82.get_state():
        grundtext += '2'
    grundtext += ', '
    if cb91.get_state():
        grundtext += '1'
    if cb9X.get_state():
        grundtext += 'X'
    if cb92.get_state():
        grundtext += '2'
    grundtext += ', '
    if cb101.get_state():
        grundtext += '1'
    if cb10X.get_state():
        grundtext += 'X'
    if cb102.get_state():
        grundtext += '2'
    grundtext += ', '
    if cb111.get_state():
        grundtext += '1'
    if cb11X.get_state():
        grundtext += 'X'
    if cb112.get_state():
        grundtext += '2'
    grundtext += ', '
    if cb121.get_state():
        grundtext += '1'
    if cb12X.get_state():
        grundtext += 'X'
    if cb122.get_state():
        grundtext += '2'
    grundtext += ', '
    if cb131.get_state():
        grundtext += '1'
    if cb13X.get_state():
        grundtext += 'X'
    if cb132.get_state():
        grundtext += '2'
    grundrad.set_text(grundtext)
    ar = grundtext[10:].replace(',', '').split()
    products = 1
    for a in ar:
        products *= len(a)
    antalrader.set_text("Antal rader, före reducering: " + str(products))

def handleReset(button):
    buttons = [
        cb11, cb1X, cb12,
        cb21, cb2X, cb22,
        cb31, cb3X, cb32,
        cb41, cb4X, cb42,
        cb51, cb5X, cb52,
        cb61, cb6X, cb62,
        cb71, cb7X, cb72,
        cb81, cb8X, cb82,
        cb91, cb9X, cb92,
        cb101, cb10X, cb102,
        cb111, cb11X, cb112,
        cb121, cb12X, cb122,
        cb131, cb13X, cb132,
    ]
    for button in buttons:
        button.set_state(False)
    setGrundrad()

def handleOddsButton(button):
    oF = ""
    for c in list(oddsFavoriter.get_text()[0]):
        if c in ('1', 'X', '2'):
            oF += c
    buttons = [
        cb11, cb1X, cb12,
        cb21, cb2X, cb22,
        cb31, cb3X, cb32,
        cb41, cb4X, cb42,
        cb51, cb5X, cb52,
        cb61, cb6X, cb62,
        cb71, cb7X, cb72,
        cb81, cb8X, cb82,
        cb91, cb9X, cb92,
        cb101, cb10X, cb102,
        cb111, cb11X, cb112,
        cb121, cb12X, cb122,
        cb131, cb13X, cb132,
    ]
    for i, value in enumerate(list(oF)):
        if value == '1':
            buttons[3*i].set_state(True)
        elif value == 'X':
            buttons[3*i+1].set_state(True)
        else:
            buttons[3*i+2].set_state(True)
    setGrundrad()

def handleStreckButton(button):
    oF = ""
    for c in list(streckFavoriter.get_text()[0]):
        if c in ('1', 'X', '2'):
            oF += c
    buttons = [
        cb11, cb1X, cb12,
        cb21, cb2X, cb22,
        cb31, cb3X, cb32,
        cb41, cb4X, cb42,
        cb51, cb5X, cb52,
        cb61, cb6X, cb62,
        cb71, cb7X, cb72,
        cb81, cb8X, cb82,
        cb91, cb9X, cb92,
        cb101, cb10X, cb102,
        cb111, cb11X, cb112,
        cb121, cb12X, cb122,
        cb131, cb13X, cb132,
    ]
    for i, value in enumerate(list(oF)):
        if value == '1':
            buttons[3*i].set_state(True)
        elif value == 'X':
            buttons[3*i+1].set_state(True)
        else:
            buttons[3*i+2].set_state(True)
    setGrundrad()

def handleSpelbarhetButton(button):
    sF = spelbarhetText.get_text()[0].replace('\n', ' ').split()[1:]
    buttons = [
        cb11, cb1X, cb12,
        cb21, cb2X, cb22,
        cb31, cb3X, cb32,
        cb41, cb4X, cb42,
        cb51, cb5X, cb52,
        cb61, cb6X, cb62,
        cb71, cb7X, cb72,
        cb81, cb8X, cb82,
        cb91, cb9X, cb92,
        cb101, cb10X, cb102,
        cb111, cb11X, cb112,
        cb121, cb12X, cb122,
        cb131, cb13X, cb132,
    ]
    for i, value in enumerate(sF):
        if float(value) >= float(spelbarhetEdit.get_edit_text()):
            buttons[i].set_state(True)

def countSimilar(a, b):
    return sum(map(eq, a, b))
"""
    similar = 0
    for x,y in zip(a,b):
        if x == y:
            similar += 1
    return similar
"""

def getUtdelning(s):
    streckList = streckText.get_text()[0][7:].split()
    probability = 1
    for i, value in enumerate(list(s)):
        if value == '1':
            probability *= 0.01*int(streckList[3*i])
        elif value == 'X':
            probability *= 0.01*int(streckList[3*i+1])
        else:
            probability *= 0.01*int(streckList[3*i+2])
    turnover = int((infoText.get_text()[0][infoText.get_text()[0].rfind(' ')+1:].replace(',', '')))
    antalPers = probability*turnover
    if antalPers > 1:
        return int(0.4*0.65*turnover/antalPers)
    else:
        return 10000000

def handleReduceraButton(button):
    reduceradlista = []
    radlista = grundrad.get_text()[0][10:].replace(',', '').split()
    odds = oddsFavoriter.get_text()[0][14:].replace(',', '').replace(' ', '')
    for c in itertools.product(*radlista):
        radstring = str(c).replace(',', '').replace(' ', '').replace("'", '').replace('(', '').replace(')', '')
        antalOdds = countSimilar(radstring, odds)
        if oddsMinEdit.value() <= antalOdds <= oddsMaxEdit.value():
            reduceradlista.append((radstring, getUtdelning(radstring)))
    reduceradlista.sort(key=lambda tup: tup[1])
    reduceradlista = [i for i in reduceradlista if i[1] > minUtdelningEdit.value()]
    global maxlikaReduceradlista
    maxlikaReduceradlista.clear()
    for i, rad in enumerate(reduceradlista):
        pb.set_completion(100*i/len(reduceradlista))
        loop.draw_screen()
        max = 0
        for hittills in maxlikaReduceradlista:
            antallika = countSimilar(rad[0], hittills[0])
            if antallika > max:
                max = antallika
            if max >= maxLikaEdit.value():
                break
        if max < maxLikaEdit.value():
            maxlikaReduceradlista.append(rad)
    pb.set_completion(100)
    if maxlikaReduceradlista != []:
        reduceraderader.set_text("Antal rader, efter reducering: " + str(len(maxlikaReduceradlista)) +
            '\n' + "Lägsta förväntade utdelning: " + str(maxlikaReduceradlista[0][1])
        )

palette = [
    ('header', 'default,bold', 'default'),
    ('good', 'black', 'light green'),
    ('bad', 'black', 'dark red'),
    ('neutral', 'black', 'yellow'),
    ('titlebar', 'black', 'white'),
    ('pbIncomplete', 'black', 'light gray'),
    ('pbComplete', 'black', 'dark gray')
]

type = "Stryktipset"
data = getData(type)

typeButtons = []
stryk = urwid.RadioButton(typeButtons, u"Stryktipset")
eu = urwid.RadioButton(typeButtons, u"Europatipset")
urwid.connect_signal(stryk, 'change', setType)

cb11 = urwid.CheckBox(u"1")
cb1X = urwid.CheckBox(u"X")
cb12 = urwid.CheckBox(u"2")
cb21 = urwid.CheckBox(u"1")
cb2X = urwid.CheckBox(u"X")
cb22 = urwid.CheckBox(u"2")
cb31 = urwid.CheckBox(u"1")
cb3X = urwid.CheckBox(u"X")
cb32 = urwid.CheckBox(u"2")
cb41 = urwid.CheckBox(u"1")
cb4X = urwid.CheckBox(u"X")
cb42 = urwid.CheckBox(u"2")
cb51 = urwid.CheckBox(u"1")
cb5X = urwid.CheckBox(u"X")
cb52 = urwid.CheckBox(u"2")
cb61 = urwid.CheckBox(u"1")
cb6X = urwid.CheckBox(u"X")
cb62 = urwid.CheckBox(u"2")
cb71 = urwid.CheckBox(u"1")
cb7X = urwid.CheckBox(u"X")
cb72 = urwid.CheckBox(u"2")
cb81 = urwid.CheckBox(u"1")
cb8X = urwid.CheckBox(u"X")
cb82 = urwid.CheckBox(u"2")
cb91 = urwid.CheckBox(u"1")
cb9X = urwid.CheckBox(u"X")
cb92 = urwid.CheckBox(u"2")
cb101 = urwid.CheckBox(u"1")
cb10X = urwid.CheckBox(u"X")
cb102 = urwid.CheckBox(u"2")
cb111 = urwid.CheckBox(u"1")
cb11X = urwid.CheckBox(u"X")
cb112 = urwid.CheckBox(u"2")
cb121 = urwid.CheckBox(u"1")
cb12X = urwid.CheckBox(u"X")
cb122 = urwid.CheckBox(u"2")
cb131 = urwid.CheckBox(u"1")
cb13X = urwid.CheckBox(u"X")
cb132 = urwid.CheckBox(u"2")

infoText = urwid.Text('')
grundrad = urwid.Text('')
antalrader = urwid.Text('')
reduceraderader = urwid.Text('')

setGrundrad()
oddsFavoriter = urwid.Text('')
streckFavoriter = urwid.Text('')

resetButton = urwid.Button(u"Reset")
reset = urwid.connect_signal(resetButton, 'click', handleReset)
oddsButton = urwid.Button(u"Set Oddsfavoriter")
oddsButtonSignal = urwid.connect_signal(oddsButton, 'click', handleOddsButton)
streckButton = urwid.Button(u"Set Streckfavoriter")
streckButtonSignal = urwid.connect_signal(streckButton, 'click', handleStreckButton)

spelbarhetEdit = urwid.Edit(u"Lägsta spelbarhet: ", "1.00")
spelbarhetButton = urwid.Button(u"Set Spelbarhet")
SpelbarhetButtonSignal = urwid.connect_signal(spelbarhetButton, 'click', handleSpelbarhetButton)

oddsMaxEdit = urwid.IntEdit("Max oddsfavoriter: ", 9)
oddsMinEdit = urwid.IntEdit("Min oddsfavoriter: ", 1)
minUtdelningEdit = urwid.IntEdit("Min utdelning: ", 1000000)
maxLikaEdit = urwid.IntEdit("Max lika: ", 11)
reduceraButton = urwid.Button(u"Reducera")
reduceraButtonSignal = urwid.connect_signal(reduceraButton, 'click', handleReduceraButton)
pb = urwid.ProgressBar('pbIncomplete', 'pbComplete')

typeFill = urwid.Filler(
    urwid.Pile([
        stryk,
        eu,
        urwid.Divider(),
        infoText,
        urwid.Divider(),
        urwid.Padding(urwid.GridFlow(
            [urwid.Text(u"1: "), cb11, cb1X, cb12],
            5, 3, 1, 'left'
            )
        ),
        urwid.Padding(urwid.GridFlow(
            [urwid.Text(u"2: "), cb21, cb2X, cb22],
            5, 3, 1, 'left'
            )
        ),
        urwid.Padding(urwid.GridFlow(
            [urwid.Text(u"3: "), cb31, cb3X, cb32],
            5, 3, 1, 'left'
            )
        ),
        urwid.Padding(urwid.GridFlow(
            [urwid.Text(u"4: "), cb41, cb4X, cb42],
            5, 3, 1, 'left'
            )
        ),
        urwid.Padding(urwid.GridFlow(
            [urwid.Text(u"5: "), cb51, cb5X, cb52],
            5, 3, 1, 'left'
            )
        ),
        urwid.Padding(urwid.GridFlow(
            [urwid.Text(u"6: "), cb61, cb6X, cb62],
            5, 3, 1, 'left'
            )
        ),
        urwid.Padding(urwid.GridFlow(
            [urwid.Text(u"7: "), cb71, cb7X, cb72],
            5, 3, 1, 'left'
            )
        ),
        urwid.Padding(urwid.GridFlow(
            [urwid.Text(u"8: "), cb81, cb8X, cb82],
            5, 3, 1, 'left'
            )
        ),
        urwid.Padding(urwid.GridFlow(
            [urwid.Text(u"9: "), cb91, cb9X, cb92],
            5, 3, 1, 'left'
            )
        ),
        urwid.Padding(urwid.GridFlow(
            [urwid.Text(u"10: "), cb101, cb10X, cb102],
            5, 3, 1, 'left'
            )
        ),
        urwid.Padding(urwid.GridFlow(
            [urwid.Text(u"11: "), cb111, cb11X, cb112],
            5, 3, 1, 'left'
            )
        ),
        urwid.Padding(urwid.GridFlow(
            [urwid.Text(u"12: "), cb121, cb12X, cb122],
            5, 3, 1, 'left'
            )
        ),
        urwid.Padding(urwid.GridFlow(
            [urwid.Text(u"13: "), cb131, cb13X, cb132],
            5, 3, 1, 'left'
            )
        ),
        urwid.Divider(),
        grundrad,
        urwid.Divider(),
        oddsFavoriter,
        streckFavoriter,
        urwid.Divider(),
        urwid.Padding(urwid.GridFlow(
            [resetButton, oddsButton, streckButton], 24, 3, 1, 'left'
        )),
        urwid.Padding(urwid.GridFlow(
            [spelbarhetEdit, spelbarhetButton], 24, 3, 1, 'left'
        )),
        urwid.Divider(),
        antalrader,
        urwid.Divider(),
        urwid.Padding(urwid.GridFlow(
            [oddsMinEdit, oddsMaxEdit, minUtdelningEdit, maxLikaEdit, reduceraButton, pb], 24, 3, 1, 'left'
        )),
        urwid.Divider(),
        reduceraderader
    ]),
    valign='top', top=0, bottom=1)

headerText = urwid.Text(u"TIPSREDUCERING", align='center')
header = urwid.AttrMap(headerText, 'titlebar')
footerText = urwid.Text(u"G: Uppdatera grundrad | S: Spara rader till fil | Q: QUIT", align='center')
footer = urwid.AttrMap(footerText, 'titlebar')

rows = []
homeTeams = []
awayTeams = []
odds = []
sannolikhet = []
streck = []
spelbarhet = []
rows, homeTeams, awayTeams, odds, sannolikhet, streck, spelbarhet, odds_t, streck_t = getCoupon(data)
rowsText = urwid.Text(rows, 'right')
homeTeamsText = urwid.Text(homeTeams, 'right')
awayTeamsText = urwid.Text(awayTeams)
oddsText = urwid.Text(odds)
sannolikhetText = urwid.Text(sannolikhet)
streckText = urwid.Text(streck)
spelbarhetText = urwid.Text(spelbarhet)
oddsFavoriter.set_text(odds_t)
streckFavoriter.set_text(streck_t)

coupon = urwid.Columns([
    rowsText,
    homeTeamsText,
    awayTeamsText,
    oddsText,
    sannolikhetText,
    streckText,
    spelbarhetText,
])

innerFrame = urwid.Frame(body=typeFill, footer=coupon)
layout = urwid.Frame(body=innerFrame, footer=footer)

loop = urwid.MainLoop(layout, palette, unhandled_input=handleInput)
#loop = urwid.MainLoop(innerFrame, palette, unhandled_input=exit)
loop.run()
