import aiofiles
import asyncio
import os
with open("example.txt","w") as f:
    f.write("0123456789")

async def main():
    async with aiofiles.open("example.txt", mode="rb") as f:
        content = await f.read()
        print(content.decode('utf-8'))

    async with aiofiles.open("example.txt", mode="rb") as f:
        await f.seek(3)
        # await f.seek(3+2)
        content = await f.read(2)
        print(content.decode('utf-8'))



asyncio.run(main())


if os.path.exists("example.txt"):
    
    os.remove("example.txt")