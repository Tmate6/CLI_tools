import pynput
import typer
from typing_extensions import Annotated
import time
from typing import Optional
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
import random

mouse = pynput.mouse.Controller()

on = False

def on_release(key):
    global on

    if key == pynput.keyboard.Key.backspace:
        on = not on

class Autoclicker:
    def __init__(self, cps, noise, duration, amount, rightClick):
        self.cps = cps
        self.noise = noise
        self.duration = duration
        self.amount = amount
        self.rightClick = rightClick

        self.clicks = 0
        self.startTime = 0
        self.endTime = 0

    def run(self):
        global on

        self.startTime = time.time()

        while on:
            currentTime = time.time()
            if self.duration is not None and currentTime - self.startTime >= self.duration:
                self.endTime = currentTime
                on = False
                break

            if self.amount is not None and self.clicks >= self.amount:
                on = False
                self.endTime = currentTime
                break

            if not self.rightClick:
                mouse.click(pynput.mouse.Button.left)
            else:
                mouse.click(pynput.mouse.Button.right)
                
            self.clicks += 1

            sleepTime = 1/self.cps - (currentTime - self.startTime - self.clicks/self.cps)

            if self.noise:
                time.sleep(max(0, sleepTime + (sleepTime * random.uniform(-1.1, 1.1))))
            else:
                time.sleep(max(0, sleepTime))

            #print(self.clicks / (time.time() - self.startTime), " ", abs(self.cps - (self.clicks / (time.time() - self.startTime))))

        self.endTime = currentTime

def setupHelper():
    print("\n[bold green]Setup helper[/bold green]")

    while True:
        try:
            print("\nEnter the cps to click.")
            cps = int(input("Cps: "))
            break

        except ValueError:
            print("\n[bold red]Invalid input[/bold red]")

    rightClick = input("\nRightclick? [y/N]: ").lower() == "y"

    noise = input("\nAdd noise? [y/N]: ").lower() == "y"

    while True:
        print("\nHave a limit? Enter a [green]number[/green] to set the max amount of clicks, a time (in the format [green]min:sec[/green] [white]/[/white] [green]hour:min:sec[/green]) or leave blank for infinite.")
        command = input("Limit: ")

        times = command.count(":")

        amount = None
        duration = None

        if command == "":
            break

        try:
            if times == 0:
                amount = int(command)
                break
            elif times == 1:
                duration = int(command.split(":")[0] * 60) + int(command.split(":")[1])
                break
            elif times == 2:
                duration = int(command.split(":")[0] * 3600) + int(command.split(":")[1] * 60) + int(command.split(":")[2])
                break
            else:
                print("\n[bold red]Invalid input[/bold red]")

        except ValueError:
            print("\n[bold red]Invalid input[/bold red]")

    print("\n[bold green]Setup complete[/bold green]\n")

    return cps, noise, duration, amount, rightClick

def main(cps: Annotated[Optional[int], typer.Argument()] = None,
         noise: Annotated[bool, typer.Option(help="Add noise to the cps")] = False,
         duration: Annotated[int, typer.Option(help="Time autoclicker should run for in seconds")] = None,
         amount: Annotated[int, typer.Option(help="Amount of times to click")] = None,
         rightclick: bool = None):
    
    print("\n[ [bold green]Autoclicker[/bold green] ]")

    if cps is None:
        cps, noise, duration, amount, rightclick = setupHelper()

    print("\nPress [bold]backspace[/bold] to begin, and again to stop.\n")

    keyboard = pynput.keyboard.Listener(on_release=on_release)
    keyboard.start()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Waiting for [green]backspace[/green] to be pressed...", total=None)

        while not on:
            time.sleep(0.5)

    print(f"Starting at [[bold green]{time.strftime('%H:%M:%S')}[/bold green]]")

    autoClicker = Autoclicker(cps, noise, duration, amount, rightclick)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=f"Clicking...", total=None)
        autoClicker.run()

    print("\nDone!")
    print(f"Clicked [[bold green]{round(autoClicker.clicks / (autoClicker.endTime - autoClicker.startTime), 2)}[/bold green]] cps. Thats [[bold green]{autoClicker.clicks}[/bold green]] times in [[bold green]{round(autoClicker.endTime - autoClicker.startTime, 2)}[/bold green]] seconds\n")

    exit()


if __name__ == "__main__":
    typer.run(main)