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
    while len(random_words) < 6:
        random_word = random.choice(words)
        if random_word not in random_words:
            random_words.append(random_word)
    rhyme_words = []
    for word in random_words:
        rhymes = loop.run_until_complete(get_rhyme(page, word))
        if len(rhymes) == 0:
            rhymes = ['-']
        rhyme_words.append(random.choice(rhymes[:10] if len(rhymes) > 10 else rhymes))
    label1['text'] = ' '.join(random_words[:3])
    label2['text'] = ' '.join(rhyme_words[:3])
    label3['text'] = ' '.join(random_words[3:])
    label4['text'] = ' '.join(rhyme_words[3:])
    root.after(10 * 1000, generate_words)


def before_start():
    global seconds
    label2['text'] = ''
    label3['text'] = ''
    label4['text'] = ''
    label1.config(fg='#00FF00')
    if seconds > 0:
        label1['text'] = str(seconds)
    else:
        label1['text'] = 'FIGHT!!!'
        label4['text'] = 'Подгружаю рифмы..'
        label1.config(fg='#FF0000')
        root.after(1000, generate_words)
        return
    seconds -= 1
    root.after(1000, before_start)


def load_words() -> list:
    with open('top.txt', 'r', encoding='UTF-8') as f:
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
label1 = Label(root, text='RAP', font=('Comic Sans MS', 46), fg='#FF0000')
label2 = Label(root, text='ГЕНЕРАТОР', font=('Comic Sans MS', 46), fg='#FF0000')
label3 = Label(root, text='III', font=('Comic Sans MS', 46), fg='#0000FF')
label4 = Label(root, text='2021', font=('Comic Sans MS', 46), fg='#0000FF')
label1.pack(fill=BOTH, expand=1)
label2.pack(fill=BOTH, expand=1)
label3.pack(fill=BOTH, expand=1)
label4.pack(fill=BOTH, expand=1)
root.after(2000, before_start)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

