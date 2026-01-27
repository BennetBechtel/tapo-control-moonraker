import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from tapo import ApiClient

load_dotenv()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


TAPO_USERNAME = require_env("TAPO_USERNAME")
TAPO_PASSWORD = require_env("TAPO_PASSWORD")
TAPO_IP_ADDRESS = require_env("TAPO_IP_ADDRESS")


app = FastAPI()
client = ApiClient(tapo_username=TAPO_USERNAME, tapo_password=TAPO_PASSWORD)
# device needs to be initialized every time else you get an Exception: Tapo(SessionTimeout)


@app.get("/status")
async def status():
    device = (
        await client.p100(  # Change to fit your smart plug (p100, p105, p110, p115)
            ip_address=TAPO_IP_ADDRESS
        )
    )
    if device is None:
        raise HTTPException(status_code=500, detail="Device not initialized")

    device_info = await device.get_device_info()
    device_info = device_info.to_dict()
    is_power_on = device_info.get("device_on")

    status = "on" if is_power_on else "off"
    return {"status": status}


@app.get("/on")
async def on():
    device = (
        await client.p100(  # Change to fit your smart plug (p100, p105, p110, p115)
            ip_address=TAPO_IP_ADDRESS
        )
    )
    if device is None:
        raise HTTPException(status_code=500, detail="Device not initialized")

    await device.on()
    return {"status": "on"}


@app.get("/off")
async def off():
    device = (
        await client.p100(  # Change to fit your smart plug (p100, p105, p110, p115)
            ip_address=TAPO_IP_ADDRESS
        )
    )
    if device is None:
        raise HTTPException(status_code=500, detail="Device not initialized")

    await device.off()
    return {"status": "off"}
