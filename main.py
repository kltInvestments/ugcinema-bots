import asyncio, tempfile, os
from telethon import events, Button
from common.config import settings
from common.telegram_utils import make_client
from common import db
from workers.video_worker import overlay_style_A

FREE_UP = settings.FREE_UPLOADER_ID
PAID_UP = settings.PAID_UPLOADER_ID
TRUSTED = set(settings.TRUSTED_UPLOADER_IDS + [FREE_UP, PAID_UP])
FREE_CHANNEL = settings.FREE_CHANNEL_USERNAME
PAID_GROUP_ID = settings.PAID_GROUP_ID

PENDING = {}  # user_id -> {thumb, video, title, cta, free, cat, confirm_dup}
CATEGORIES = ["Action","Comedy","Romance","Horror","Series","Kids","Local Uganda Movies","Trending Now"]
CTA_DEFAULT = "Unlock full HD movies & early releases! Tap below to join Premium 👇"

def is_free_uploader(uid: int) -> bool: return uid == FREE_UP
def is_paid_uploader(uid: int) -> bool: return uid == PAID_UP

async def main():
    client = make_client("uploader_bot")
    await client.start(bot_token=settings.UPLOADER_BOT_TOKEN)
    await db.init_pool(settings.DATABASE_URL)

    async def ask_category(event, free_flow: bool):
        rows, row = [], []
        for i, name in enumerate(CATEGORIES, 1):
            row.append(Button.inline(name, data=f"cat:{name}".encode()))
            if i % 2 == 0: rows.append(row); row = []
        if row: rows.append(row)
        await event.reply(("Choose category (FREE)" if free_flow else "Choose category (PAID)") + ":", buttons=rows)

    @client.on(events.NewMessage)
    async def on_message(event):
        sender = await event.get_sender()
        if not sender or sender.id not in TRUSTED: return

        rec = PENDING.get(sender.id, {"thumb": None, "video": None, "title": None, "cta": None, "free": is_free_uploader(sender.id), "confirm_dup": False})
        msg = event.message

        if msg.photo and not rec["thumb"]:
            rec["thumb"] = msg; PENDING[sender.id] = rec
            await event.reply("✅ Thumbnail saved. Now send the **video**."); return

        if (msg.video or msg.document) and not rec["video"]:
            rec["video"] = msg; PENDING[sender.id] = rec
            await event.reply("✅ Video received. Send the **Title** text."); return

        if msg.raw_text and not rec["title"]:
            rec["title"] = msg.raw_text.strip(); PENDING[sender.id] = rec
            if rec["free"]:
                await event.reply("✅ Title saved. Send **CTA description** for FREE channel (or type 'default').")
            else:
                await ask_category(event, free_flow=False)
            return

        if rec["free"] and msg.raw_text and rec["title"] and not rec["cta"]:
            cta = msg.raw_text.strip()
            rec["cta"] = CTA_DEFAULT if cta.lower()=="default" else cta
            PENDING[sender.id] = rec
            await ask_category(event, free_flow=True); return

    @client.on(events.CallbackQuery(pattern=b"cat:"))
    async def on_category(event):
        sender = await event.get_sender()
        rec = PENDING.get(sender.id)
        if not rec or not rec["video"] or not rec["title"]:
            await event.answer("Missing video/title.", alert=True); return

        cat = event.data.decode().split(":",1)[1]
        rec["cat"] = cat
        PENDING[sender.id] = rec

        # Anti-duplicate check
        if await db.title_exists(rec["title"]) and not rec.get("confirm_dup"):
            yes = Button.inline("Post anyway", data=b"dup:yes")
            no = Button.inline("Cancel", data=b"dup:no")
            return await event.edit(f"⚠️ Duplicate title detected: **{rec['title']}**. Post anyway?", buttons=[[yes, no]])

        await event.edit(f"Category set: **{cat}**. Processing & posting...")
        await process_and_post(event, rec)

    @client.on(events.CallbackQuery(pattern=b"dup:"))
    async def on_dup_choice(event):
        sender = await event.get_sender()
        rec = PENDING.get(sender.id)
        if not rec: return await event.answer("No pending upload.", alert=True)
        choice = event.data.decode().split(":",1)[1]
        if choice == "no":
            PENDING.pop(sender.id, None)
            return await event.edit("❌ Upload cancelled.")
        rec["confirm_dup"] = True
        PENDING[sender.id] = rec
        await event.edit("Duplicate acknowledged. Processing...")
        await process_and_post(event, rec)

    async def process_and_post(event, rec):
        free_flow = rec["free"]
        cat = rec.get("cat","Uncategorized")
        with tempfile.TemporaryDirectory() as td:
            vid_path = os.path.join(td, "input.mp4")
            out_path = os.path.join(td, "output.mp4")
            thumb_path = os.path.join(td, "thumb.jpg") if rec["thumb"] else None
            await event.client.download_media(rec["video"], file=vid_path)
            if rec["thumb"]: await event.client.download_media(rec["thumb"], file=thumb_path)
            title = rec["title"]
            cta_desc = rec["cta"] if free_flow else None
            try:
                overlay_style_A(vid_path, out_path, title=title, cta=cta_desc, preset=settings.FFMPEG_PRESET)
            except Exception as e:
                return await event.respond(f"❌ Processing failed: {e}")

            if free_flow:
                caption = f"{title}\n\n{cta_desc}"
                buttons = [[Button.inline(f"Join Premium — UGX {settings.SUB_PRICE_UGX}", data=b"premium")]]
                target = FREE_CHANNEL
            else:
                caption = f"{title}"
                buttons = None
                target = PAID_GROUP_ID

            await event.client.send_file(target, file=out_path, caption=caption, buttons=buttons, thumb=thumb_path if thumb_path else None)

        try:
            await db.record_upload((await event.get_sender()).id, rec["title"], cat, "free" if free_flow else "paid")
        except Exception:
            pass

        await event.respond("✅ Posted.")
        PENDING.pop((await event.get_sender()).id, None)

    print("Uploader bot ready (anti-dup + CTA default).")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
