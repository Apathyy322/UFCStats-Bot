# UFC info bot by Apathyy322 ( with explanation )

import requests
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
import asyncio
from datetime import datetime
import os
import time
load_dotenv()

url = os.getenv("url")
api = os.getenv("api")
resp = requests.get(url)
bot = Bot(token=api)
dp = Dispatcher()

@dp.message(Command("start"))
async def startio(message: Message): 
    text1 = """<b>👋 Hi, I am UFC Stats bot and I can provide you UFC fighters stats! 🤖</b>"""
    await message.reply(text1, parse_mode=ParseMode.HTML) # parse mode basically sends our message and 
                                                          #  looking for special symbols like <b> </b> 
                                                          # here and adapt message's looks to those symbols

@dp.message(Command("help"))
async def help(message: Message):
    usr = message.from_user # this group of 3 lines ( fname lname included ) is getting all names from telegram 
    fname = usr.first_name or "User"
    lname = usr.last_name or ""

    full_name = f"{fname} {lname}" if lname else fname # making both names 1 variable 
    response_text = f"Hi, <b>{full_name}</b>\nHere are the commands of this bot:\n <code>/find (name of the fighter)</code>\nExample: <code>/find Nariman Abbasov</code> or <code>/find Islam Makhachev</code>"
    await message.reply(response_text, parse_mode=ParseMode.HTML) #using our name to prompt user with his name

@dp.message(Command("find"))
async def find_fighter(message: Message):
    user_input = message.text[len('/find '):].strip() #making a variable called user_input ater /find (stringing fighter's name)

    if not user_input:
        await message.reply("<b>Please provide a fighter's name.</b>", parse_mode=ParseMode.HTML)
        return #if here is nothing after find it sends the message above

    if resp.status_code == 200:
        all_fighters = resp.json()
        bm = await message.reply("<i>Gathering information....</i>", parse_mode=ParseMode.HTML)
        time.sleep(1)
        await bm.delete()
        #if our respone is sucessfull it says that it is gathering infortmation and then deletes its own 
        # message in 1 second to clear the chat

        if not isinstance(all_fighters, list):
            print("Unexpected data format.")
            await message.reply("<b>Unexpected data format.</b>", parse_mode=ParseMode.HTML)
            # this referce to api errors
            return

        def calculate_age(birthdate_str):
            birthdate_format = "%Y-%m-%dT%H:%M:%S"
            birthdate = datetime.strptime(birthdate_str, birthdate_format)
            today = datetime.today()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            return age
        # after getting our json from api this function counts the age of fighter in real time (time now - date of birth)

        search_parts = user_input.split()
        search_first_name = search_parts[0] if len(search_parts) > 0 else ''
        search_last_name = search_parts[1] if len(search_parts) > 1 else ''

        found = False
        for fighter in all_fighters:
            if fighter is None:
                print("Encountered None entry in fighters list")
                continue

            if isinstance(fighter, dict):
                first_name = str(fighter.get('FirstName', ''))
                last_name = str(fighter.get('LastName', ''))
                birthdate_str = fighter.get('BirthDate', '')

                age = calculate_age(birthdate_str) if birthdate_str else 'Unknown'

                if (search_first_name in first_name and search_last_name in last_name) or \
                   (user_input in f"{first_name} {last_name}"):
                    text2 = f"""
<b>📛Nickname:</b> {fighter.get('Nickname', 'N/A')}
<b>⚖Weightclass:</b> {fighter.get('WeightClass', 'N/A')}
<b>⏰Age:</b> {age}
<b>☝Height:</b> {fighter.get('Height', 0) * 2.54} cm <b>or</b> {fighter.get('Height', 0)} inches
<b>🏋️‍♀️Weight:</b> {fighter.get('Weight', 0) * 0.45359237:.1f} kg <b>or</b> {fighter.get('Weight', 0)} lbs

<b>🥇Wins:</b> {fighter.get('Wins', 0)}
<b>😢Losses:</b> {fighter.get('Losses', 0)}
<b>😐Draws:</b> {fighter.get('Draws', 0)}

<b>🥊Knockouts:</b> {fighter.get('TechnicalKnockouts', 0)}
<b>😴Knockout losses:</b> {fighter.get('TechnicalKnockoutLosses', 0)}
<b>🏆Title Wins:</b> {fighter.get('TitleWins', 0)}
<b>😭Title Losses:</b> {fighter.get('TitleLosses', 0)}
<b>🤐Title Draws:</b> {fighter.get('TitleDraws', 0)}
""" # huge text that will be sent to our client. Look at use of parsemode again
                    bm2 = await message.reply("<b>[+] Fighter Found!✅</b>\n\n<i>Sending Data!</i>", parse_mode=ParseMode.HTML)
                    time.sleep(2) # just to make it look official lol
                    await bm2.delete()
                    await message.reply(text2, parse_mode=ParseMode.HTML)
                    found = True

        if not found:
            await message.reply("<b>No fighter found with that name.</b>", parse_mode=ParseMode.HTML) # if no found with that name is found in that json it sends this
    else:
        print(f"Error: {resp.status_code}")
        await message.reply("<b>Error fetching data from the API.</b>", parse_mode=ParseMode.HTML)

async def main():
    await dp.start_polling(bot) # dispatcher.start_polling where bot is defined on line 18

if __name__ == "__main__":
    asyncio.run(main())
#making asyncio run our command if no errors