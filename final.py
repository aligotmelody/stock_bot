

from telegram import Update 
from telegram.ext import  CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder
import yfinance as yf
import asyncio
import logging
from telegram.constants import ChatAction
import requests as rs
from langdetect import  detect
import string
from datetime import datetime, timedelta


news_api_key = ""
tele_token = ""


today = datetime.today().date()
yesterday = today - timedelta(days=1)
             
STOCK = ""


def contains_letters(word):

    for char in word:

        if  char.isalpha():

            return True  
        else:
            return False
def is_valid_ticker(ticker):
    stock = yf.Ticker(ticker)
    print(f"stock out : {stock}")
    if stock:
           return True
    else:
           return False


def news_layout(articles):  
                headlines = []
                descriptions = []
                sources = []
                urls = []
               
                for num in range(len(articles)) :
                        if articles[num]["url"] == None or articles[num]["title"] == None or articles[num]["description"] == None or articles[num]["source"] == None or "Suspicious Activity Detected" in articles[num]["description"] or detect(articles[num]["title"]) != "en" :
                                continue
                        else:
                                headlines.append(articles[num]["title"])
                                descriptions.append(articles[num]["description"])
                                urls.append(articles[num]["url"])
                                sources.append((articles[num]["source"]["name"]))

                return headlines, descriptions, urls, sources



class StockDetails():
        def __init__(self) :
                
                self.headlines = []
                self.descriptions = []
                self.sources = []
                self.urls = []


      
        def get_news(self, endpoint):
                
                try:    
                    response = rs.get(url=endpoint)
                    articles = response.json()["articles"]
                    Articles = articles[0]
                
                except ConnectionRefusedError as e :
                      return "404"
              
                except IndexError as e:
                      return "none to be shown"
                else:
                      print(f"####### here:  ")#articles
                      return articles
            

def curr_price(Stock):
        
        ticker = yf.Ticker(Stock)
        info = ticker.get_info()
        print(f"###INFO: {info}")
        if info:
               try:
                    price = info["currentPrice"]
                      
               except KeyError as e :
                      return "no current price keyword"
               else:
                      return price

stk = StockDetails()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    await update.message.reply_text('heeeey hot stuff,  how can I help you today?')
    await update.message.reply_text('press the help command to get started  ')



async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    lis = (
           "Just write down the Stock's ticker symbol\n"
           "In case you don't know what is a ticker symbol\n"
           "it's just an acronym for the stock's name\n"
           "Just look it up online if you don't know it "
           
           )
    await update.message.reply_text(f'{lis}')




async def Get_News(update: Update , STOCK: str):

    EndPoint = f"https://newsapi.org/v2/everything?q={STOCK}&from={yesterday}&to={today}&qInTitle='quantum computing Inc'&sortBy=relevancy&apiKey={news_api_key}"
    art = stk.get_news(endpoint=EndPoint)
    #print(art)
    if art == "none to be shown":
          await update.message.reply_text(f"seems like there aren't any fresh news regarding {STOCK} ")
    elif  "404" in art:
          await update.message.reply_text(f"the api won't have the stock symbol {STOCK} , seems like it's not registered for some reason ..")

    else:
          HeadLines, Descriptions, Urls, Sources = news_layout(art)
          print(f"headlines#####: {HeadLines}")

    #await update.effective_chat.send_action(ChatAction.TYPING)


    try:
        cur_price = curr_price(Stock=STOCK)
        print(f"####currentPrice: {cur_price}")
        if cur_price == "no current price keyword":
              cur_price = "can't find the current price for this stock"
        else:
              cur_price = "Unexpected error"
        if len(Descriptions) > 10:
                iteration = 10
        else:
            iteration = len(Descriptions)
        for num in range(iteration): 
                
                article_message = (
                    f"🔸 Article number : {num+1}\n"
                    f"----------------------------------------------------------\n"
                    f"💰💵 Stock's Current Price : {cur_price}\n"
                    f"----------------------------------------------------------\n"
                    f"💠 Source : {Sources[num]}\n"
                    f"----------------------------------------------------------\n"
                    f"💠 Headline : {HeadLines[num]}\n"
                    f"----------------------------------------------------------\n"
                    f"💠 Article Description : {Descriptions[num]} \n"
                    f"----------------------------------------------------------\n"
                    f"💠 url to the article : {Urls[num]} \n"
                )
                await update.effective_chat.send_action(ChatAction.TYPING)
                await update.message.reply_text(article_message)
                print(f"Sending article {num}: {article_message}")
                await asyncio.sleep(3)
                print("Finished sleeping .. ")
       
              
    except Exception as e:
        print(f"Error sending Article {num}\n Error: {e}")
    finally:
        logging.debug("Task completed or cancelled.")
       



async def sending_stock_news(update:Update , context:ContextTypes):

    user_message = update.message.text.upper().strip()
    if contains_letters(user_message):
        if not is_valid_ticker(user_message):
            await update.effective_chat.send_action(ChatAction.TYPING)
            await update.message.reply_text(f'{STOCK} is not a valid ticker symbol, make sure you double check it ...')
            user_message = update.message.text.upper().strip()
        STOCK = user_message
        if STOCK:
            
            task = context.application.create_task(Get_News(update, STOCK=STOCK))
            print("Task Started .... ")
            await update.effective_chat.send_action(ChatAction.TYPING)
            # while not task.done():
            #     await update.effective_chat.send_action(ChatAction.TYPING)
            #     try:
            #         await asyncio.wait_for(asyncio.shield(task), 6)  # Adjust timeout as needed
            #     except asyncio.TimeoutError:
            #         update.message.reply_text(f'Fetching the news ..... ')
        else:
            STOCK = None

    else:
          await update.message.reply_text(f'{user_message} is not a valid ticker symbol, make sure you double check it ...')
              
            
    # task = context.application.create_task(Get_News(update, STOCK=STOCK))
    # print("Task Started .... ")
    # while not task.done():
    #     await update.effective_chat.send_action(ChatAction.TYPING)
    #     try:
    #         await asyncio.wait_for(asyncio.shield(task), 6)  # Adjust timeout as needed
    #     except asyncio.TimeoutError:
    #           update.message.reply_text(f'Fetching the news ..... ')




Bot_app = ApplicationBuilder().token(tele_token).build()

Bot_app.add_handler(CommandHandler("start", start))
#Bot_app.add_handler(CommandHandler("new_stock", new_stock))
Bot_app.add_handler(CommandHandler("help", help))
Bot_app.add_handler(MessageHandler(filters.TEXT, sending_stock_news))


Bot_app.run_polling()
