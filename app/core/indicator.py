import winsound

async def beep():
    winsound.Beep(frequency=3000, duration=100)
