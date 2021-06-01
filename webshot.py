

from bs4 import BeautifulSoup
from main_startup.config_var import Config
from main_startup.core.decorators import friday_on_cmd
from main_startup.core.startup_helpers import run_cmd
from main_startup.helper_func.basic_helpers import edit_or_reply, get_text, humanbytes
from hashlib import md5
import aiofiles
import os
import aiohttp
import urllib
import validators

async def check_if_url_is_valid(url):
    valid = validators.url(url)
    if valid:
        return True
    return False

async def screen_shot_(url_s: str):
  """Use AioHttp For Faster Session."""
  async with aiohttp.ClientSession() as session:
      async with session.get('https://screenshotlayer.com') as resp:
          text_ = await resp.text()
  soup = BeautifulSoup(text_, features="html.parser")
  scl_secret = soup.findAll('input')[1]['value']
  print(scl_secret)
  key = md5((str(url_s) + scl_secret).encode()).hexdigest()
  url = f'https://screenshotlayer.com/php_helper_scripts/scl_api.php?secret_key={key}&url={url_s}'
  return url


async def download_img(url):
    """Download Images Using AioFiles."""
    file_path = None
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                file_path = f"Webshot_satya.png"
                f = await aiofiles.open(file_path, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return file_path

  
@friday_on_cmd(
    ["webshot", "ws"],
    cmd_help={
        "help": "Take A Screen Shot Of A Website.",
        "example": "{ch}webshot https://www.google.com/",
    }
)
async def fetch_webshoot(client, message):
    msg_ = await edit_or_reply(message, "<code>Please Wait i am capturing the Shot!</code>", parse_mode="html")
    url_ = get_text(message)
    if not url_:
        await msg_.edit("<code>Give Me Url To Fetch A Screen Shot.</code>", parse_mode="html")
        return
    if not await check_if_url_is_valid(url_):
        return await msg_.edit("<code>This is An Invalid Url.</code>", parse_mode="html")
    screen_shot_image = await screen_shot_(url_)
    img_ = await download_img(screen_shot_image)
    img_size = humanbytes(os.stat(img_).st_size)
    if not img_:
        return await msg_.edit("<code>Something Isn't Right. Did You Give Me Valid Url?</code>", parse_mode="html")
    capt_ = f"<b><u>WebShot Captured</b></u> \n<b>URL :</b> <code>{url_}</code> \n<b>SIZE :</b> <code>{img_size}</code> \n\n<b>Powered By FridayUB</b>"
    if message.reply_to_message:
        await client.send_document(
            message.chat.id,
            img_,
            caption=capt_,
            parse_mode="html",
            reply_to_message_id=message.reply_to_message.message_id,
        )
    else:
        await client.send_document(message.chat.id, img_, parse_mode="html", caption=capt_)
    if os.path.exists(img_):
        os.remove(img_)
    await msg_.delete()
    @friday_on_cmd.on(sudo_cmd(pattern="ss (.*)", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    if Config.CHROME_BIN is None:
        await edit_or_reply(event, "Need to install Google Chrome. Module Stopping.")
        return
    catevent = await edit_or_reply(event, "`Processing ...`")
    start = datetime.now()
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--test-type")
        chrome_options.add_argument("--headless")
        # https://stackoverflow.com/a/53073789/4723940
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = Config.CHROME_BIN
        await event.edit("`Starting Google Chrome BIN`")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        input_str = event.pattern_match.group(1)
        inputstr = input_str
        caturl = url(inputstr)
        if not caturl:
            inputstr = "http://" + input_str
            caturl = url(inputstr)
        if not caturl:
            await catevent.edit("`The given input is not supported url`")
            return
        driver.get(inputstr)
        await catevent.edit("`Calculating Page Dimensions`")
        height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);"
        )
        width = driver.execute_script(
            "return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);"
        )
        driver.set_window_size(width + 100, height + 100)
        # Add some pixels on top of the calculated dimensions
        # for good measure to make the scroll bars disappear
        im_png = driver.get_screenshot_as_png()
        # saves screenshot of entire page
        await catevent.edit("`Stoppping Chrome Bin`")
        driver.close()
        message_id = None
        if event.reply_to_msg_id:
            message_id = event.reply_to_msg_id
        end = datetime.now()
        ms = (end - start).seconds
        hmm = f"**url : **{input_str} \n**Time :** `{ms} seconds`"
        await catevent.delete()
        with io.BytesIO(im_png) as out_file:
            out_file.name = input_str + ".PNG"
            await event.client.send_file(
                event.chat_id,
                out_file,
                caption=hmm,
                force_document=True,
                reply_to=message_id,
                allow_cache=False,
                silent=True,
            )
    except Exception:
        await catevent.edit(f"`{traceback.format_exc()}`")

