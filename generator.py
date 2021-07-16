import asyncio
import random
from tkinter import *
import requests
from bs4 import BeautifulSoup
import urllib.parse
from pyppeteer import launch


async def init_browser_page():
        browser = await launch({'headless': True})
        page = await browser.newPage()
        await page.setRequestInterception(True)
        page.on('request', lambda req: asyncio.ensure_future(intercept_blocker(req)))
        return browser, page


async def get_rhyme(page, word) -> list:
    await page.goto(f'https://rifme.net/r/{word}/0')
    content = await page.evaluate('document.body.innerHTML', force_expr=True)
    soup = BeautifulSoup(content, 'html.parser')
    words_tags = soup.select('.riLi')
    rhyme_words = [tag.text for tag in words_tags]
    return rhyme_words


async def close_browser(browser):
    await browser.close()


def on_closing():
    loop.run_until_complete(close_browser(browser))
    root.destroy()


async def intercept_blocker(request):
    if request.resourceType in ['stylesheet', 'image', 'font', 'script']:
        await request.abort()
    else:
        await request.continue_()


def generate_words():
    # themes_ = [random.choice(words) for _ in range(3)]
    random_words = []
    while len(random_words) < 2:
        random_word = random.choice(words)
        if random_word not in random_words:
            random_words.append(random_word)
    rhyme_words = loop.run_until_complete(get_rhyme(page, random_words[-1]))
    random_words.append(random.choice(rhyme_words[:10] if len(rhyme_words) > 10 else rhyme_words))
    label['text'] = ', '.join(random_words)
    root.after(5000, generate_words)


def before_start():
    global seconds
    label.config(fg='#00FF00')
    if seconds > 0:
        label['text'] = str(seconds)
    else:
        label['text'] = 'FIGHT!!!'
        label.config(fg='#FF0000')
        root.after(1000, generate_words)
        return
    seconds -= 1
    root.after(1000, before_start)


def load_words() -> list:
    with open('top-yandex.txt', 'r', encoding='UTF-8') as f:
        theme_text = f.read()
    words = theme_text.split('\n')
    words = list(filter(lambda x: len(x) <= 10, words))
    return words


words = load_words()
seconds = 3
root = Tk()
loop = asyncio.get_event_loop()
browser, page = loop.run_until_complete(init_browser_page())
root.geometry('1600x900')
label = Label(root, text='RAP ГЕНЕРАТОР III', font=('Comic Sans MS', 46), fg='#FF0000')
label.pack(fill=BOTH, expand=1)
root.after(2000, before_start)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

