# OneFastCatbot
A Discord bot for raspberry pi, line sensor, and cat treadmill (or other turning thing)

# BOM
 - Cat wheel. I used onefastcat.com
 - Computer with connectivity. I used a Raspberry Pi 3B with WiFi
 - Line sensor. I used TCRT5000
 - Contrast. I used masking tape

# Hardware configuration
 - Wire sensor to GPIO. Pi pinout:
   - Pi Pin 1 to sensor pin "VCC" for 3.3v
   - Pi Pin 6 to sensor pin "GND" for ground
   - Pi Pin 11 to sensor pin "OUT" for GPIO17
 - Power computer
 - Network computer
 - Position the sensor about 5mm from wheel (I put it under one of the support wheels using blu-tac, ymmv)
 - Add markers to wheel (stick tape bits on - I use a single 1" stripe)
 - Secure computer - I ziptied it to the metal frame
 - Wire management - be sure nothing's at risk of dragging or getting into the wheels

# Software configuration
 - Configure and connect TTY: https://www.raspberrypi.com/documentation/computers/remote-access.html
 - Set up a Discord "app" bot: https://discord.com/developers/docs/quick-start/getting-started
 - Download code to your Pi
 - Add python to rc.1 for autostart
 - Add your Bot, Channel, and wheel info to the python files. Also adjust the GPIO pin if you used a different one than indicated above, run "pinout" in terminal to see the correlations
 - Reboot the Pi
