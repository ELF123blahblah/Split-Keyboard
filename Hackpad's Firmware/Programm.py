#!/usr/bin/env python3
"""
SK6812 LED Matrix Controller with Switches and Rotary Encoders
Controls 9 LEDs with individual switches, brightness encoder, and volume encoder
"""

import time
import board
import neopixel
from gpiozero import Button, RotaryEncoder
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER

# LED Configuration
NUM_LEDS = 9
LED_PIN = board.D18  # GPIO18
pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS, brightness=0.5, auto_write=False, pixel_order=neopixel.GRB)

# Brightness and Volume
brightness = 0.5
volume = 50

# Rotary Encoder Pins (GPIO numbers)
BRIGHTNESS_ENC_A = 17
BRIGHTNESS_ENC_B = 27
VOLUME_ENC_A = 22
VOLUME_ENC_B = 23

# Switch Pins (GPIO numbers for 9 switches)
SWITCH_PINS = [5, 6, 13, 19, 26, 12, 16, 20, 21]

# Initialize Rotary Encoders
encoder_brightness = RotaryEncoder(BRIGHTNESS_ENC_A, BRIGHTNESS_ENC_B, max_steps=100)
encoder_volume = RotaryEncoder(VOLUME_ENC_A, VOLUME_ENC_B, max_steps=100)

# Initialize Switches
switches = [Button(pin, pull_up=True, bounce_time=0.05) for pin in SWITCH_PINS]

# LED States and Colors
led_states = [False] * NUM_LEDS
led_colors = [
    (255, 0, 0),      # Red
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
    (255, 255, 0),    # Yellow
    (0, 255, 255),    # Cyan
    (255, 0, 255),    # Magenta
    (255, 165, 0),    # Orange
    (128, 0, 128),    # Purple
    (255, 255, 255)   # White
]

# Initialize Windows Audio Control
try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    audio_volume = cast(interface, POINTER(IAudioEndpointVolume))
    audio_available = True
    print("Audio control initialized")
except Exception as e:
    print(f"Audio control not available: {e}")
    audio_available = False

def set_system_volume(vol):
    """Set system volume (0-100)"""
    if audio_available:
        try:
            # Convert 0-100 to 0.0-1.0
            volume_scalar = vol / 100.0
            audio_volume.SetMasterVolumeLevelScalar(volume_scalar, None)
        except Exception as e:
            print(f"Error setting volume: {e}")

def update_brightness(steps):
    """Update LED brightness based on encoder steps"""
    global brightness
    old_brightness = brightness
    brightness = max(0.0, min(1.0, brightness + steps * 0.02))
    
    if abs(brightness - old_brightness) > 0.01:
        pixels.brightness = brightness
        pixels.show()
        print(f"Brightness: {int(brightness * 100)}%")

def update_volume(steps):
    """Update system volume based on encoder steps"""
    global volume
    old_volume = volume
    volume = max(0, min(100, volume + steps * 2))
    
    if abs(volume - old_volume) > 1:
        set_system_volume(volume)
        print(f"Volume: {volume}%")

def toggle_led(index):
    """Toggle LED on/off"""
    led_states[index] = not led_states[index]
    
    if led_states[index]:
        pixels[index] = led_colors[index]
        print(f"LED {index + 1} ON - Color: {led_colors[index]}")
    else:
        pixels[index] = (0, 0, 0)
        print(f"LED {index + 1} OFF")
    
    pixels.show()

def setup_switch_handlers():
    """Set up button press handlers for all switches"""
    for i, switch in enumerate(switches):
        switch.when_pressed = lambda idx=i: toggle_led(idx)

def main():
    print("=" * 50)
    print("LED Matrix Controller Started")
    print("=" * 50)
    print("Brightness Encoder: Adjust LED brightness")
    print("Volume Encoder: Adjust system volume")
    print("Switches 1-9: Toggle individual LEDs")
    print("=" * 50)
    
    # Initialize all LEDs to off
    pixels.fill((0, 0, 0))
    pixels.show()
    
    # Set up switch handlers
    setup_switch_handlers()
    
    # Set initial volume
    set_system_volume(volume)
    
    # Store previous encoder values
    last_brightness_value = encoder_brightness.steps
    last_volume_value = encoder_volume.steps
    
    try:
        while True:
            # Check brightness encoder
            current_brightness = encoder_brightness.steps
            if current_brightness != last_brightness_value:
                delta = current_brightness - last_brightness_value
                update_brightness(delta)
                last_brightness_value = current_brightness
            
            # Check volume encoder
            current_volume = encoder_volume.steps
            if current_volume != last_volume_value:
                delta = current_volume - last_volume_value
                update_volume(delta)
                last_volume_value = current_volume
            
            time.sleep(0.01)  # Small delay to reduce CPU usage
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        pixels.fill((0, 0, 0))
        pixels.show()
        print("All LEDs turned off. Goodbye!")

if __name__ == "__main__":
    main()
    