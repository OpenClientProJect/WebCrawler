import asyncio

from FB_middle import main
if __name__ == "__main__":
    try:
        asyncio.run(main("272275"))
    except KeyboardInterrupt:
        print(111)