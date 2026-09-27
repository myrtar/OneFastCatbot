import os
import time
import threading

import discord
from discord.ext import tasks, commands
from gpiozero import DigitalInputDevice
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Put your channel ID in .env as CHANNEL_ID=1234567890, or replace the
# fallback 0 below with it directly.
CHANNEL_ID = int(os.getenv('CHANNEL_ID') or 0)
if not TOKEN or not CHANNEL_ID:
    raise SystemExit('DISCORD_TOKEN and CHANNEL_ID must be set (check the .env file)')

GPIO_PIN = 17
runner_name = 'Meowrie Curie'

support_wheel = 88      # support wheel diameter in mm (stock is 88)
tape_strips = 1         # pieces of tape on the support wheel
track_ratio = 1070 / 1149   # track inner-d / outer-d

# We count ONE edge per tape strip (rising only), so each count is exactly
# 1/tape_strips of a revolution, regardless of stripe width or sensor polarity.
distance_per_count = track_ratio * (support_wheel * 3.14159265 / tape_strips) / 1000  # m

# Anything faster than this is physically impossible for a cat, so two edges
# closer together than the resulting interval are sensor chatter, not tape.
max_plausible_speed = 15.0  # m/s
min_count_interval = distance_per_count / max_plausible_speed  # s

top_speed_revs = 2          # top speed is measured over this many whole revolutions
session_end_wait_time = 5   # s of no movement before a run is considered over
session_end_min_dist = 0.5  # m; shorter runs are not reported

monitoring = True
_lock = threading.Lock()
timestamps = []
_last_count_time = 0.0


def on_edge():
    """Runs in gpiozero's edge-event thread, independent of the Discord event loop."""
    global _last_count_time
    if not monitoring:
        return
    now = time.monotonic()  # immune to NTP clock steps, unlike time.time()
    if now - _last_count_time < min_count_interval:
        return  # debounce
    _last_count_time = now
    with _lock:
        timestamps.append(now)


def summarize(ts):
    intervals = len(ts) - 1  # N edges bound N-1 measured intervals
    if intervals < 1:
        return None
    distance = intervals * distance_per_count
    if distance < session_end_min_dist:
        return None
    elapsed = ts[-1] - ts[0]
    speed = distance / elapsed  # m/s

    span = top_speed_revs * tape_strips  # always a whole number of revolutions
    top_speed = speed
    for i in range(len(ts) - span):
        window_speed = span * distance_per_count / (ts[i + span] - ts[i])
        top_speed = max(top_speed, window_speed)

    dist_ft = distance * 3.28084
    kph = speed * 3.6
    mph = kph / 1.60934
    pace_mi = 60 / mph
    pace_km = 60 / kph

    print(f'{distance:.1f}m | {elapsed:.1f}s | avg {speed:.2f}m/s | top {top_speed:.2f}m/s')
    return (f'{runner_name} ran {distance:.1f}m ({dist_ft:.1f}\') in {elapsed:.1f}s '
            f'at {kph:.2f}kph ({mph:.2f}MPH), top speed {top_speed * 3.6:.2f}kph, '
            f'avg pace: {pace_km:.0f}min/km ({pace_mi:.0f}min/SM).')


# The sensor module drives its OUT pin itself, so no internal pull resistor.
# gpiozero ships with Raspberry Pi OS and uses kernel edge events (lgpio),
# which work on Bookworm, unlike RPi.GPIO's add_event_detect.
sensor = DigitalInputDevice(GPIO_PIN, pull_up=None, active_state=True)
sensor.when_activated = on_edge  # one count per rising edge

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@tasks.loop(seconds=0.5)
async def check_session():
    with _lock:
        if not timestamps or time.monotonic() - timestamps[-1] < session_end_wait_time:
            return
        ts = timestamps.copy()
        timestamps.clear()
    message = summarize(ts)
    if message:
        await bot.get_channel(CHANNEL_ID).send(message)
    else:
        print('Run too short, discarded')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id}) and monitoring = {monitoring}')


@bot.command()
async def start_wheel(ctx):
    global monitoring
    monitoring = True
    if not check_session.is_running():
        check_session.start()
    await ctx.send('Monitoring cat wheel. Use !stop_wheel to halt.')


@bot.command()
async def stop_wheel(ctx):
    global monitoring
    monitoring = False
    check_session.stop()
    with _lock:
        timestamps.clear()
    await ctx.send('Wheel monitor halted, use !start_wheel to resume.')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        print('Invalid command ignored in discord channel')


try:
    bot.run(TOKEN)
finally:
    sensor.close()
