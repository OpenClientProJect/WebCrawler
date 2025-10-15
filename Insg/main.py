import asyncio
from Insg.scraper.task import main

if __name__ == "__main__":
    content0, content1, lines_hidden_line, lines_hidden_text = "000","纯","https://www.instagram.com/reel/DEutFdGTJod/?utm_source=ig_web_copy_link","https://www.instagram.com/like.japan/"
    asyncio.run(main(content0,content1,lines_hidden_line,lines_hidden_text))