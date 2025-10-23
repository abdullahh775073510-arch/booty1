import asyncio
import random
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from rapidfuzz import fuzz

# =======================
TOKEN = "8423452048:AAEJGLj2KKENX5NRxNRC6s_Hm4rUvzlU5KQ"
# =======================

import json

# تحميل الأسئلة من ملف JSON
with open("questions2.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

active_quiz = {}  # لتخزين بيانات المسابقة
scores = {}        # لتخزين النقاط


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user.first_name

    if chat_id in active_quiz:
        await update.message.reply_text("⚠️ هناك مسابقة تعمل حالياً!")
        return

    question = random.choice(questions)
    active_quiz[chat_id] = {
        "question": question,
        "owner": update.effective_user.id
    }

    await update.message.reply_text(
        f"🎯 بدءت مسابقة جديدة بواسطة {user}!\n\n"
        f"📜 السؤال:\n{question['q']}\n\n"
        f"💡 أرسل إجابتك في الرسائل أسفل 👇"
    )


async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in active_quiz:
        await update.message.reply_text("❌ لا توجد مسابقة حالياً.")
        return

    if active_quiz[chat_id]["owner"] != user_id:
        await update.message.reply_text("⚠️ فقط من بدأ المسابقة يمكنه الانتقال للسؤال التالي.")
        return

    question = random.choice(questions)
    active_quiz[chat_id]["question"] = question

    await update.message.reply_text(
        f"📜 السؤال الجديد:\n{question['q']}\n\n"
        f"💬 أرسل إجابتك 👇"
    )


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id not in active_quiz:
        return  # لا توجد مسابقة حالياً

    question = active_quiz[chat_id]["question"]
    correct_answer = question["a"].strip()
    user_answer = update.message.text.strip()

    # نقارن بين الإجابتين باستخدام التشابه
    similarity = fuzz.ratio(correct_answer, user_answer)

    if similarity >= 50:  # مقبولة
        scores[user.id] = scores.get(user.id, 0) + 1
        await update.message.reply_text(
            f"✅ أحسنت يا {user.first_name}!\n"
            f"إجابتك صحيحة ({correct_answer}) 🎉\n"
            f"لديك الآن {scores[user.id]} نقطة 🌟"
        )
    else:
        pass  # يطنش الإجابات الخاطئة


async def my_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    score = scores.get(user.id, 0)
    await update.message.reply_text(f"🏆 نقاطك الحالية: {score}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 أوامر البوت:\n"
        "/start - بدء مسابقة جديدة\n"
        "/next - السؤال التالي (فقط لمن بدأ المسابقة)\n"
        "/score - معرفة نقاطك\n"
    )


async def main():
    from nest_asyncio import apply
    apply()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_quiz))
    app.add_handler(CommandHandler("next", next_question))
    app.add_handler(CommandHandler("score", my_score))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    print("✅ البوت يعمل الآن...")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())