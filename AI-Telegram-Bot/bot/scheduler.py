import schedule
import time
from bot.main import app

def send_daily_message():
    app.bot.send_message(chat_id="YOUR_CHAT_ID", text="Reminder: Join today's event!")

schedule.every().day.at("09:00").do(send_daily_message)

while True:
    schedule.run_pending()
    time.sleep(1)
