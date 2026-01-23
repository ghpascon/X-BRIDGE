import asyncio


async def delayed_func(func, delay: float = 1.0):
	await asyncio.sleep(delay)
	func()

