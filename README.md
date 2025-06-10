# OneFastCatbot
A Discord bot for raspberry pi, line sensor, and cat treadmill (or other turning thing)

<img src="https://i.imgur.com/kcTfchY.jpeg" height="200" /><img src="https://i.imgur.com/ukVAWw0.jpeg" height="200" />

# BOM
 - Cat wheel. I used onefastcat.com
 - Raspberry Pi. I used 3B with WiFi
 - Line sensor. I used this TCRT5000 https://www.keyestudio.com/products/keyestudio-line-tracking-sensor-module-white-black-line-detector-for-arduino-uno-r3-mega-2560-r3
 - Contrast. I used masking tape.



# Hardware configuration
 - Wire sensor to GPIO. Pi pinout:
   - Pi Pin 1 to sensor pin "VCC" for 3.3v (or get 5V from Pi Pin 2 if your sensor needs it)
   - Pi Pin 6 to sensor pin "GND" for ground
   - Pi Pin 11 to sensor pin "OUT" for GPIO17
 - Power the computer
 - Network the computer
 - Position the sensor about 5mm from wheel (I put it under one of the support wheels using blu-tac, ymmv. Documented max is 20mm)
 - Add markers to wheel (stick tape bits on - I use a single 1" stripe)
 - If needed, adjust the sensor's sensitivity potentiometer so the LED is on when presented with white stripe and is off when presented with black stripe.
 - Secure computer - I ziptied it to the metal frame
 - Wire management - be sure nothing's at risk of dragging or getting into the wheels

<img src="https://i.imgur.com/PIrUsia.jpeg" height="200" alt="whole assembly"/><img src="https://i.imgur.com/jXxjZ7d.jpeg" height="200" alt="reflector and sensor" /><img src="https://i.imgur.com/9ckVk4G.jpeg" height="200" alt="sensor installed" /><img src="https://i.imgur.com/AhblzTS.jpeg" height="200" alt="pi wired" />

# Software configuration
 - Configure and connect TTY: https://www.raspberrypi.com/documentation/computers/remote-access.html
 - Set up a Discord "app" bot: https://discord.com/developers/docs/quick-start/getting-started
 - put the resulting .env file somewhere handy on the Pi, defining DISCORD_TOKEN= and CHANNEL_ID=
 - Download wheelbot.py to your Pi, same place as the .env file
 - Add your Bot, Channel, and wheel info to the .env file. Also adjust the GPIO pin if you used a different one than indicated above, run "pinout" in terminal to see the correlations
 - Add wheelbot.py as a service: https://tecadmin.net/setup-autorun-python-script-using-systemd/
 - Reboot your Pi to make sure it all comes online automatically
 - send "!start_wheel" in your channel and expect a response from your bot/app



## Notes
This configuration uses polling, not interrupt. As written, polling occurs every .00025s with a minimum pause of .00015s available. Interrupt might be better, but this is more precision than I need, with cats topping out around 13m/s. That's going to turn the 88mm wheel 160 times a second. With four reflectors, that's eight stripes and 1300 state switches per second, or one state switch every .00076s, so I think interrupt isn't really needed.

The inner dimension of the One Fast Cat wheel track is D=1070mm, the outer track dimension is D=1149mm, and the support wheels are D=88mm (mine are 110mm, much quieter).

stripes = Number of tape strips applied to support wheel, times two. I have one strip, two stripes (one black, one white). I average the values, so they need not be equal or evenly placed.

distance = track-inner-d / track-outer-d * ( (support-wheel-d * pi ) / stripes ) 

distance ratio = track-inner-d / track-outer-d

distance ratio = 107cm / 115cm

distance ratio = 0.930 (or inverted 1.075)

