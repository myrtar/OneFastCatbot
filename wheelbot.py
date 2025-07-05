import discord
import os
from discord.ext import tasks, commands
import RPi.GPIO as GPIO
import time
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
GPIO_PIN = 17
monitoring = True
Channel_ID = #must be defined for your own channel
runner_name = 'Meowrie Curie'
support_wheel = 88 # wheel diameter in millimeters, stock wheel is 88
stripes = 2 #number of color changes (or, number of tape pieces times two)

distance_per_flip = 1070 / 1149 * ( ( support_wheel * 3.14 ) / stripes ) / 1000 # in m: track-inner-d / track-outer-d * ( (support-wheel * pi ) / stripes ) 

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN)

# Initialize Discord bot
bot = commands.Bot(command_prefix='!', intents = intents)

session_end_wait_time = 5 # seconds to wait stationary before considering the run session "over"
session_end_min_dist = 0.5 # how far does the run need to be to publish/record it?
last_state = GPIO.input(GPIO_PIN)
timestamp_list = []

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id}) and monitoring = {monitoring}')

@tasks.loop(seconds=0.00050)  # Adjust delay as needed for sensor resolution, floor is .00015
async def monitor_gpio():
    global distance, last_change_time, monitoring, last_state, start_time
    if GPIO.input(GPIO_PIN) != last_state and monitoring: # run happening?
        timestamp_list.append(time.time())
        last_state = GPIO.input(GPIO_PIN)
        print(f'Go time!')
    elif not timestamp_list: # run is not happening
        time.sleep(.2)

    elif monitoring and timestamp_list and (time.time() - timestamp_list[-1]) > session_end_wait_time: # after running ends
        distance = len(timestamp_list) * distance_per_flip
        if distance > session_end_min_dist:
            elapsed_time = timestamp_list[-1] - timestamp_list[0]
            calc_span = 4
            top_speed = 0
            speed = (distance / elapsed_time)  # m/s
            dist_ft = distance * 3.28084
            kph = speed * 3.6 # kilometer per hour
            mph = kph / 1.60934 # miles per hour
            kts = speed * 1.943844
            pace_mi = 60 / mph # minutes per mile
            pace_km = pace_mi * 0.621371
            pace_nm = pace_mi / 0.86897
            furlong = distance / 201.168 # y tho

            for i in range(1, (len(timestamp_list)-calc_span)):
                time_diff = timestamp_list[i + calc_span] - timestamp_list[i]
                speed = (calc_span*distance_per_flip)/time_diff
                if speed > top_speed:
                    top_speed = speed

            print(f'{distance:.1f}m | {elapsed_time:.1f}s | {speed:.2f}m/s')
            await bot.get_channel(Channel_ID).send(f'{runner_name} ran {distance:.1f}m ({dist_ft:.1f}\') in {elapsed_time:.1f}s at {kph:.2f}kph ({mph:.2f}MPH), top speed {top_speed*3.6:.2f}kph, avg pace: {pace_km:.0f}min/km ({pace_mi:.0f}min/SM).')
        timestamp_list.clear()
        print("Elif done, zeroed out")

@bot.command()
async def start_wheel(ctx):
    global monitoring
    monitoring = True
    monitor_gpio.start()
                               
    await ctx.send('Monitoring cat wheel. Use !stop_wheel to halt.')

@bot.command()
async def stop_wheel(ctx):
    global monitoring
    monitoring = False
    monitor_gpio.stop()
    await ctx.send('Wheel monitor halted, use !start_wheel to resume.')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
#        await ctx.send("Invalid command")
        print("Invalid command ignored in discord channel")

    current_state = GPIO.input(GPIO_PIN)
bot.run(TOKEN)
