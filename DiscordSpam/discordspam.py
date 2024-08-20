import pyautogui
from PIL import ImageGrab
import pynput
import time
import typer
from typing_extensions import Annotated
from typing import List, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print
from enum import Enum
import random

keyboard = pynput.keyboard.Controller()

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

on = False

def on_release(key):
    global on

    if key == pynput.keyboard.Key.backspace:
        on = not on


class discordSpammer:
    def __init__(self, messages, rotation, amount, verbose):
        self.messages = messages
        self.rotation = (rotation and len(messages) > 1)
        self.amount = amount
        self.verbose = verbose

        self.sent = 0
    
    def getChillZoneMessage(self):
        x, y = pyautogui.position()
        try:
            image = ImageGrab.grab(bbox=(x-3, y-3, x-2, y-2)).load()
        except:
            return False
        
        color = image[0, 0]

        if 65 <= color[0] <= 90 and 75 <= color[1] <= 100 and 180 <= color[2] <= 245:
            return True
        
        return False

    def handleChillZone(self):
        if not self.getChillZoneMessage():
            return
        
        while True:
            if self.verbose:
                print("[bald]>[/bald] Chill zone detected")

            if not on:
                print("[bald]>[/bald] Exit by keypress")
                return
            
            keyboard.tap(pynput.keyboard.Key.enter)
            time.sleep(1)
            keyboard.tap(pynput.keyboard.Key.esc)
            time.sleep(0.3)
            keyboard.tap(pynput.keyboard.Key.enter)
            time.sleep(0.3)

            if not self.getChillZoneMessage():
                time.sleep(0.3)
                return

    def send(self):
        global on

        if self.verbose:
            print("[bald]>[/bald] Running burst...")

        # Initial burst
        i = 0
        while True:
            if self.rotation:
                message = random.choice(self.messages)
            else:
                if i + 1 > len(self.messages):
                    i = 0

                message = self.messages[i]

                i += 1

            keyboard.type(message)
            keyboard.tap(pynput.keyboard.Key.enter)

            time.sleep(0.05)

            self.sent += 1

            if self.amount != -1 and self.sent >= self.amount:
                if self.verbose:
                    print("[bald]>[/bald] Exit by amount reached")
                return

            if self.sent == 5:
                break

        if self.verbose:
            print("[bald]>[/bald] Burst complete. Running main loop...")

        while True:
            for message in self.messages:
                if self.rotation:
                    message = random.choice(self.messages)

                if not on:
                    if self.verbose:
                        print("[bald]>[/bald] Exit by keypress")
                    return
                
                if self.amount != -1 and self.sent >= self.amount:
                    if self.verbose:
                        print("[bald]>[/bald] Exit by amount reached")
                    return
                
                self.handleChillZone()

                keyboard.type(message)
                keyboard.tap(pynput.keyboard.Key.enter)
                time.sleep(0.3) # About right to keep up message buffer while not going too fast

                self.sent += 1

def setupHelper():
    print("[bold blue]Setup helper[/bold blue]\n")
    
    print("Enter messages to send, seperated by commas and no spaces. To send a message with a comma, put a backslash before it.")
    print("[italic]Eg: [message 1,message 2,message 3 part 1\\, and part 2[/italic]]")

    messages = input("Messages: ").split(",")
    
    for i in range(len(messages)):
        try:
            if "\\" in messages[i]:
                messages[i] = messages[i].replace("\\", ",") + messages[i+1]
                messages.pop(i+1)
        except IndexError:
            break

    if len(messages) != 1:
        rotation = input("\nRandomly rotate the order of the messages? [y/N]: ").lower() == "y"
    else:
        rotation = False

    print("\nEnter the number of messages to send. -1 for infinite.")
    amount = int(input("Amount: "))

    print("\n[bold blue]Setup complete[/bold blue]\n")

    return messages, amount, rotation

def main(messages: Annotated[Optional[List[str]], typer.Argument()] = None,
         amount: Annotated[int, typer.Option(help="Amount of messages to send. -1 for infinite")] = -1,
         rotation: Annotated[Optional[bool], typer.Option(help="Randomly rotate the order of the messages")] = False,
         verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False):
    global on

    print("\n[ [bold][blue]Discord[/blue] Spammer[/bold] ]\n")

    if messages is None:
        messages, amount, rotation = setupHelper()

    print("Press [bold]backspace[/bold] to begin, and again to stop.")
    print("While running, wait until the chill zone message pops up, placing your cursor in the bottom right corner of the [blue]enter[/blue] button and elaving it there for auto-detection.\n")

    listener = pynput.keyboard.Listener(on_release=on_release)
    listener.start()

    spammer = discordSpammer(messages, rotation, amount, verbose)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Waiting for [blue]backspace[/blue] to be pressed...", total=None)

        while not on:
            time.sleep(0.5)

    on = True

    timer = time.time()
    print(f"Starting at [[bold blue]{time.strftime('%H:%M:%S')}[/bold blue]]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=f"Spamming...", total=None)
        spammer.send()
    

    print("\nDone!")
    print(f"Sent [[bold blue]{spammer.sent}[/bold blue]] messages in [[bold blue]{round(time.time() - timer, 2)}[/bold blue]] seconds\n")
    exit()

if __name__ == "__main__":
    typer.run(main)