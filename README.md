# tapo-control-moonraker

Control TP-Link Tapo smart plugs (P100/P105/P110/P115) through Moonraker for automated 3D printer power management.

## Why this exists

Moonraker doesn't have native support for Tapo smart plugs, and setting up Home Assistant just for plug control feels like overkill. This project provides a lightweight solution using a simple HTTP server that bridges Moonraker's power control API with Tapo smart plugs, enabling:

- Remote printer power control through Mainsail/Fluidd
- Auto-shutdown after idle timeout
- Klipper service binding for safe power management

______________________________________________________________________

## How to run it:

Note: Everywhere you find YOUR_USERNAME you need to insert the name you log into your klipper device with (for example 'pi')

1. Clone the repo somewhere on your device running klipper, for example `/home/YOUR_USERNAME/tapo-control-moonraker/` \
   Note: If you choose a different path, you will need to adjust the path in the systemd service (step 5)

1. Rename the `.env.template` file to `.env` and insert your Tapo credentials \
   The `TAPO_IP_ADDRESS` can be found in the Tapo App: \
   Select your smart plug -> Settings -> Device Info -> IP Address \
   Note: You can change the `PORT` if 56427 is already in use (remember to update it in step 7)

1. Install the required packages from the `requirements.txt` in a virtual environment

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

1. Edit the `server.py` file to fit your smart plug (P100, P105, P110, P115)

   ```python
   device = (
       await client.p100(  # Change to fit your smart plug (p100, p105, p110, p115)
           ip_address=TAPO_IP_ADDRESS
       )
   )
   ```

1. Make the script autostart by creating a systemd service `sudo vim /etc/systemd/system/tapo-control.service` \
   You can use any editor you like, i just like vim :)

   ```ini
   [Unit]
   Description=Tapo HTTP server
   Wants=network.target
   After=network.target
   Before=moonraker.service

   [Service]
   User=YOUR_USERNAME
   Group=YOUR_USERNAME
   WorkingDirectory=/home/YOUR_USERNAME/tapo-control-moonraker
   Environment=PYTHONUNBUFFERED=1
   ExecStartPre=/bin/sleep 10
   ExecStart=/home/YOUR_USERNAME/tapo-control-moonraker/.venv/bin/python /home/YOUR_USERNAME/tapo-control-moonraker/main.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

1. Reload systemd and start+enable the service

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start tapo-control.service
   sudo systemctl enable tapo-control.service
   ```

   If something does not work you can check the status with `sudo systemctl status tapo-control.service` and logs with `journalctl -u tapo-control` 

1. Edit your `moonraker.conf` in Mainsail/Fluidd, add this at the end.\
   Note: `[power printer]` is a magic string that makes Mainsail display a more prominent [printer power](https://docs.mainsail.xyz/overview/quicktips/printer-power-switch) switch UI element, I'd recommend not changing it.

   ```ini
   [power printer]
   type: http
   on_url: http://localhost:56427/on
   off_url: http://localhost:56427/off
   status_url: http://localhost:56427/status
   response_template:
     {% set resp = http_request.last_response().json() %}
     {resp["status"]}
   bound_services: klipper
   ```

   Optional: You can add this below `[power printer]`

   ```ini
   off_when_shutdown: True
   locked_while_printing: False
   restart_klipper_when_powered: True
   on_when_job_queued: True
   ```

1. Optional Klipper auto power off, courtesy of [Arksine/moonraker#167 (comment)](https://github.com/Arksine/moonraker/issues/167#issuecomment-1094223802)\
   Add to `printer.cfg` or any Klipper config file:

   ```gcode
   [idle_timeout]
   timeout: 600
   gcode:
     MACHINE_IDLE_TIMEOUT

   # Turn on PSU
   [gcode_macro M80]
   gcode:
     # Moonraker action
     {action_call_remote_method('set_device_power',
                                device='printer',
                                state='on')}

   # Turn off PSU
   [gcode_macro M81]
   gcode:
     # Moonraker action
     {action_call_remote_method('set_device_power',
                                device='printer',
                                state='off')}

   [gcode_macro MACHINE_IDLE_TIMEOUT]
   gcode:
     M84
     TURN_OFF_HEATERS
     M81
   ```

## Acknowledgements

Inspired by [mainde](https://github.com/mainde)'s [klipper-moonraker-tapo](https://github.com/mainde/klipper-moonraker-tapo) project. Thanks for paving the way!
