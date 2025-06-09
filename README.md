# OneFastCatbot
A Discord bot for raspberry pi, line sensor, and cat treadmill (or other turning thing)

# BOM
 - Cat wheel. I used onefastcat.com
 - Raspberry Pi. I used 3B with WiFi
 - Line sensor. I used TCRT5000
 - Contrast. I used masking tape

# Hardware configuration
 - Wire sensor to GPIO. Pi pinout:
   - Pi Pin 1 to sensor pin "VCC" for 3.3v (get 5V from Pi Pin 2 if your sensor needs it)
   - Pi Pin 6 to sensor pin "GND" for ground
   - Pi Pin 11 to sensor pin "OUT" for GPIO17
 - Power the computer
 - Network the computer
 - Position the sensor about 5mm from wheel (I put it under one of the support wheels using blu-tac, ymmv. Documented max is 20mm)
 - Add markers to wheel (stick tape bits on - I use a single 1" stripe)
 - If needed, adjust the sensor's sensitivity potentiometer so the LED is on when presented with white stripe and is off when presented with black plastic.
 - Secure computer - I ziptied it to the metal frame
 - Wire management - be sure nothing's at risk of dragging or getting into the wheels

# Software configuration
 - Configure and connect TTY: https://www.raspberrypi.com/documentation/computers/remote-access.html
 - Set up a Discord "app" bot: https://discord.com/developers/docs/quick-start/getting-started
 - Download code to your Pi
 - Add python to rc.1 for autostart
 - Add your Bot, Channel, and wheel info to the python files. Also adjust the GPIO pin if you used a different one than indicated above, run "pinout" in terminal to see the correlations
 - Reboot the Pi
 - send "!start_wheel" in your channel and expect a response from your bot/app

## Notes
This configuration uses polling, not interrupt. Polling occurs every .0025s with a minimum of .0015s available.
The inner diameter of the One Fast Cat wheel is 336cm, the outer diameter is ##UNKNOWN##, and the stock support wheels are 88mm, so one rotation of a support wheel is a travel distance 
