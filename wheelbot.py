import discord
import os
from discord.ext import tasks, commands
import RPi.GPIO as GPIO
import time
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
Channel_ID = os.getenv('CHANNEL_ID')
intents = discord.Intents.all()
GPIO_PIN = 17
monitoring = False
support_wheel = 110 # wheel diameter in millimeters, stock wheel is 88
stripes = 2
distance_per_flip = 1070 / 1149 * ( ( support_wheel * 3.14 ) / stripes ) # in mm: track-inner-d / track-outer-d * ( (support-wheel * pi ) / stripes ) 

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN)

# Initialize Discord bot
bot = commands.Bot(command_prefix='!', intents = intents)

session_end_wait_time = 5 # seconds to wait stationary before considering the run session "over"
session_end_min_dist = 0.5 # meters: how far does the run need to be to publish/record it?
last_state = GPIO.input(GPIO_PIN)
timestamp_list = []

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@tasks.loop(seconds=0.00025)  # Adjust delay as needed for sensor resolution, minimum delay is .00015 seconds (150us).
async def monitor_gpio():
    global distance, last_change_time, monitoring, last_state, start_time
    if GPIO.input(GPIO_PIN) != last_state and monitoring: # run happening?
        timestamp_list.append(time.time())
        last_state = GPIO.input(GPIO_PIN)

    elif not timestamp_list: # run not happening
        time.sleep(.2)

    elif monitoring and timestamp_list and (time.time() - timestamp_list[-1]) > session_end_wait_time: # after running ends
        distance = len(timestamp_list) * distance_per_flip
        if distance > session_end_min_dist:
            elapsed_time = timestamp_list[-1] - timestamp_list[0]
            calc_span = 4
            top_speed = 0
            avg_speed = (distance / elapsed_time)  # m/s
            dist_ft = distance * 3.28084
            kph = avg_speed * 3.6 # kilometer per hour
            mph = kph / 1.60934 # miles per hour
#            kts = avg_speed * 1.943844
            pace_mi = 60 / mph # minutes per mile
            pace_km = pace_mi * 0.621371
#            pace_nm = pace_mi / 0.86897
#            furlong = distance / 201.168 # why steeb?

            for i in range(1, (len(timestamp_list)-calc_span)): 
                time_diff = timestamp_list[i + calc_span] - timestamp_list[i]
                speed = (calc_span*distance_per_flip)/time_diff
                if speed > top_speed and speed < (avg_speed * 5):
                   top_speed = speed
            #print to console:
            print(f'{distance:.1f}m | {elapsed_time:.1f}s | avg {avg_speed:.2f}m/s | top {top_speed:.2f}m/s')
                        # wheel movement result output to discord:
            await bot.get_channel(Channel_ID).send(f'Cat ran {distance:.1f}m ({dist_ft:.1f}\') in {elapsed_time:.1f}s at {kph:.2f}kph ({mph:.2f}MPH), top speed {top_speed*3.6:.2f}kph, avg pace: {pace_km:.0f}min/km ({pace_mi:.0f}min/SM).') 
        timestamp_list.clear()
        print("Elif done, zeroed out")

@bot.command()
async def start_wheel(ctx):
    global monitoring
    monitoring = True
    monitor_gpio.start()
    print(f'Monitoring wheel for channel {Channel_ID}')
    await ctx.send('Monitoring cat wheel. Use !stop_wheel to halt.') # startup discord response

@bot.command()
async def stop_wheel(ctx):
    global monitoring
    monitoring = False
    monitor_gpio.stop()
    await ctx.send('Wheel monitor halted, use !start_wheel to resume.') # pause discord activity

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
#        await ctx.send("Invalid command")
        print("Invalid command ignored in discord channel")

    current_state = GPIO.input(GPIO_PIN)
bot.run(TOKEN)
