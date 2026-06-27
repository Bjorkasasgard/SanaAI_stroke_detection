"""
bot.py — Telegram Bot untuk Sana AI Stroke Screening (API Client Version)
Bilingual: Indonesia 🇮🇩 & English 🇬🇧
Menggunakan python-telegram-bot v21+
"""

import os
import logging
from pathlib import Path
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
load_dotenv(Path(__file__).parent / ".env")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_URL = "https://xvasthunter-sana-backend.hf.space/api/predict"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("sana-bot")


# ---------------------------------------------------------------------------
# Translations
# ---------------------------------------------------------------------------
STRINGS = {
    "id": {
        "welcome": (
            "👋 *Selamat datang di Sana AI Bot!*\n\n"
            "Saya akan membantu Anda melakukan *screening risiko stroke* berbasis AI.\n\n"
            "Jawab beberapa pertanyaan singkat dan saya akan menganalisis risiko Anda.\n\n"
            "⚠️ _Hasil ini bersifat indikatif dan BUKAN diagnosis medis._\n\n"
            "Pilih model AI yang ingin digunakan:"
        ),
        "model_selected": "✅ Model dipilih: *{name}*\n\nMari isi data kesehatan Anda.\n\n*Pertanyaan 1/10*\nApa jenis kelamin Anda?",
        "q_gender":      "*Pertanyaan 1/10*\nApa jenis kelamin Anda?",
        "q_age":         "*Pertanyaan 2/10*\nBerapa usia Anda?\n\nKetik angka usia Anda (contoh: `45`)",
        "q_hypertension":"*Pertanyaan 3/10*\nApakah Anda memiliki *hipertensi* (tekanan darah tinggi)?",
        "q_heart":       "*Pertanyaan 4/10*\nApakah Anda memiliki *penyakit jantung*?",
        "q_married":     "*Pertanyaan 5/10*\nApakah Anda sudah/pernah menikah?",
        "q_work":        "*Pertanyaan 6/10*\nApa jenis pekerjaan Anda?",
        "q_residence":   "*Pertanyaan 7/10*\nDi mana Anda tinggal?",
        "q_glucose":     "*Pertanyaan 8/10*\nBerapa rata-rata kadar glukosa darah Anda (mg/dL)?\n\nKetik angkanya (contoh: `90.5`)\n_Normal: 70–140 mg/dL_",
        "q_bmi":         "*Pertanyaan 9/10*\nBerapa nilai BMI (Indeks Massa Tubuh) Anda?\n\nKetik angkanya (contoh: `24.5`)\n_Normal: 18.5–24.9_",
        "q_smoking":     "*Pertanyaan 10/10*\nBagaimana status merokok Anda?",
        "analyzing":     "⏳ Sedang menganalisis data Anda...",
        "error":         "❌ Terjadi kesalahan saat menghubungi server AI. Silakan coba lagi nanti.",
        "cancelled":     "❎ Analisis dibatalkan. Ketik /start untuk memulai kembali.",
        "invalid_age":   "⚠️ Masukkan angka usia yang valid (0–120). Coba lagi:",
        "invalid_glucose":"⚠️ Masukkan angka glukosa yang valid (40–500 mg/dL). Coba lagi:",
        "invalid_bmi":   "⚠️ Masukkan nilai BMI yang valid (10–100). Coba lagi:",
        "btn_male":      "👨 Laki-laki",
        "btn_female":    "👩 Perempuan",
        "btn_yes":       "✅ Ya",
        "btn_no":        "❌ Tidak",
        "btn_married":   "💍 Sudah Menikah",
        "btn_single":    "🚫 Belum/Tidak",
        "btn_govt":      "🏛️ Pegawai Pemerintah",
        "btn_private":   "🏢 Swasta",
        "btn_self":      "💼 Wiraswasta",
        "btn_children":  "👶 Anak-anak",
        "btn_never_work":"🚫 Tidak Bekerja",
        "btn_rural":     "🌾 Pedesaan",
        "btn_urban":     "🏙️ Perkotaan",
        "btn_smokes":    "🚬 Sedang Merokok",
        "btn_former":    "🔚 Mantan Perokok",
        "btn_never_smk": "🚭 Tidak Pernah Merokok",
        "btn_unknown":   "❓ Tidak Diketahui",
        "btn_restart":   "🔄 Analisis Ulang",
        "result_header":  "🏥 *HASIL ANALISIS SANA AI*",
        "result_prob":    "📊 *Probabilitas Stroke:*",
        "result_risk":    "⚡ *Tingkat Risiko:*",
        "result_model":   "🤖 *Model:*",
        "result_data":    "📋 *Data yang Diinput:*",
        "result_label_gender":    "Jenis Kelamin",
        "result_label_age":       "Usia",
        "result_label_hype":      "Hipertensi",
        "result_label_heart":     "Penyakit Jantung",
        "result_label_smoking":   "Status Merokok",
        "result_label_glucose":   "Glukosa",
        "result_label_bmi":       "BMI",
        "yes":           "Ya",
        "no":            "Tidak",
        "years":         "tahun",
        "result_rec":    "💡 *Rekomendasi:*",
        "model_lr":      "Logistic Regression ⭐",
        "model_dt":      "Decision Tree 🌳",
        "model_knn":     "K-Nearest Neighbors 👥",
    },
    "en": {
        "welcome": (
            "👋 *Welcome to Sana AI Bot!*\n\n"
            "I will help you perform an AI-based *stroke risk screening*.\n\n"
            "Answer a few quick questions and I'll analyze your risk.\n\n"
            "⚠️ _This result is indicative and NOT a medical diagnosis._\n\n"
            "Choose an AI model to use:"
        ),
        "model_selected": "✅ Model selected: *{name}*\n\nLet's fill in your health data.\n\n*Question 1/10*\nWhat is your gender?",
        "q_gender":      "*Question 1/10*\nWhat is your gender?",
        "q_age":         "*Question 2/10*\nHow old are you?\n\nType your age (e.g. `45`)",
        "q_hypertension":"*Question 3/10*\nDo you have *hypertension* (high blood pressure)?",
        "q_heart":       "*Question 4/10*\nDo you have any *heart disease*?",
        "q_married":     "*Question 5/10*\nHave you ever been married?",
        "q_work":        "*Question 6/10*\nWhat is your type of work?",
        "q_residence":   "*Question 7/10*\nWhere do you live?",
        "q_glucose":     "*Question 8/10*\nWhat is your average blood glucose level (mg/dL)?\n\nType the value (e.g. `90.5`)\n_Normal: 70–140 mg/dL_",
        "q_bmi":         "*Question 9/10*\nWhat is your BMI (Body Mass Index)?\n\nType the value (e.g. `24.5`)\n_Normal: 18.5–24.9_",
        "q_smoking":     "*Question 10/10*\nWhat is your smoking status?",
        "analyzing":     "⏳ Analyzing your data...",
        "error":         "❌ An error occurred connecting to the AI server. Please try again later.",
        "cancelled":     "❎ Analysis cancelled. Type /start to begin again.",
        "invalid_age":   "⚠️ Enter a valid age (0–120). Try again:",
        "invalid_glucose":"⚠️ Enter a valid glucose value (40–500 mg/dL). Try again:",
        "invalid_bmi":   "⚠️ Enter a valid BMI value (10–100). Try again:",
        "btn_male":      "👨 Male",
        "btn_female":    "👩 Female",
        "btn_yes":       "✅ Yes",
        "btn_no":        "❌ No",
        "btn_married":   "💍 Married",
        "btn_single":    "🚫 Never Married",
        "btn_govt":      "🏛️ Government Job",
        "btn_private":   "🏢 Private Sector",
        "btn_self":      "💼 Self-employed",
        "btn_children":  "👶 Children",
        "btn_never_work":"🚫 Never Worked",
        "btn_rural":     "🌾 Rural",
        "btn_urban":     "🏙️ Urban",
        "btn_smokes":    "🚬 Currently Smoking",
        "btn_former":    "🔚 Formerly Smoked",
        "btn_never_smk": "🚭 Never Smoked",
        "btn_unknown":   "❓ Unknown",
        "btn_restart":   "🔄 Analyze Again",
        "result_header":  "🏥 *SANA AI ANALYSIS RESULT*",
        "result_prob":    "📊 *Stroke Probability:*",
        "result_risk":    "⚡ *Risk Level:*",
        "result_model":   "🤖 *Model:*",
        "result_data":    "📋 *Input Data:*",
        "result_label_gender":    "Gender",
        "result_label_age":       "Age",
        "result_label_hype":      "Hypertension",
        "result_label_heart":     "Heart Disease",
        "result_label_smoking":   "Smoking Status",
        "result_label_glucose":   "Glucose",
        "result_label_bmi":       "BMI",
        "yes":           "Yes",
        "no":            "No",
        "years":         "years old",
        "result_rec":    "💡 *Recommendations:*",
        "model_lr":      "Logistic Regression ⭐",
        "model_dt":      "Decision Tree 🌳",
        "model_knn":     "K-Nearest Neighbors 👥",
    },
}

def s(ctx: ContextTypes.DEFAULT_TYPE, key: str, **kwargs) -> str:
    lang = ctx.user_data.get("lang", "id")
    text = STRINGS[lang].get(key, STRINGS["id"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text


# ---------------------------------------------------------------------------
# Conversation States
# ---------------------------------------------------------------------------
(
    CHOOSE_LANG,
    CHOOSE_MODEL,
    ASK_GENDER,
    ASK_AGE,
    ASK_HYPERTENSION,
    ASK_HEART,
    ASK_MARRIED,
    ASK_WORK,
    ASK_RESIDENCE,
    ASK_GLUCOSE,
    ASK_BMI,
    ASK_SMOKING,
) = range(12)


def kb(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(t, callback_data=v) for t, v in row] for row in rows])


# ---------------------------------------------------------------------------
# Prediction Logic via API
# ---------------------------------------------------------------------------
def run_prediction_api(data: dict) -> dict:
    lang = data.get("lang", "id")
    payload = {
        "model": data["model"],
        "gender": data["gender"],
        "age": data["age"],
        "hypertension": data["hypertension"],
        "heart_disease": data["heart_disease"],
        "ever_married": data["ever_married"],
        "work_type": data["work_type"],
        "residence_type": data["residence_type"],
        "avg_glucose_level": data["avg_glucose_level"],
        "bmi": data["bmi"],
        "smoking_status": data["smoking_status"],
    }
    r = requests.post(f"{API_URL}?lang={lang}", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data.clear()
    lang_kb = kb([("🇮🇩 Bahasa Indonesia", "lang_id")], [("🇬🇧 English", "lang_en")])
    msg = "🌐 *Pilih bahasa / Choose language:*"
    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=lang_kb)
    elif update.callback_query:
        await update.callback_query.message.reply_text(msg, parse_mode="Markdown", reply_markup=lang_kb)
    return CHOOSE_LANG


async def choose_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    ctx.user_data["lang"] = "id" if q.data == "lang_id" else "en"
    model_kb = kb(
        [(s(ctx, "model_lr"), "logistic_regression")],
        [(s(ctx, "model_dt"), "decision_tree")],
        [(s(ctx, "model_knn"), "knn")],
    )
    await q.edit_message_text(s(ctx, "welcome"), parse_mode="Markdown", reply_markup=model_kb)
    return CHOOSE_MODEL


async def choose_model(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    ctx.user_data["model"] = q.data
    model_names = {"logistic_regression": s(ctx, "model_lr"), "decision_tree": s(ctx, "model_dt"), "knn": s(ctx, "model_knn")}
    await q.edit_message_text(
        s(ctx, "model_selected", name=model_names[q.data]),
        parse_mode="Markdown",
        reply_markup=kb([(s(ctx, "btn_male"), "Male"), (s(ctx, "btn_female"), "Female")]),
    )
    return ASK_GENDER


async def ask_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    ctx.user_data["gender"] = q.data
    await q.edit_message_text(s(ctx, "q_age"), parse_mode="Markdown")
    return ASK_AGE


async def ask_age(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        age = float(update.message.text.strip())
        if age < 0 or age > 120: raise ValueError
        ctx.user_data["age"] = age
        await update.message.reply_text(s(ctx, "q_hypertension"), parse_mode="Markdown", reply_markup=kb([(s(ctx, "btn_yes"), "1"), (s(ctx, "btn_no"), "0")]))
        return ASK_HYPERTENSION
    except ValueError:
        await update.message.reply_text(s(ctx, "invalid_age"))
        return ASK_AGE


async def ask_hypertension(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    ctx.user_data["hypertension"] = int(q.data)
    await q.edit_message_text(s(ctx, "q_heart"), parse_mode="Markdown", reply_markup=kb([(s(ctx, "btn_yes"), "1"), (s(ctx, "btn_no"), "0")]))
    return ASK_HEART


async def ask_heart(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    ctx.user_data["heart_disease"] = int(q.data)
    await q.edit_message_text(s(ctx, "q_married"), parse_mode="Markdown", reply_markup=kb([(s(ctx, "btn_married"), "Yes"), (s(ctx, "btn_single"), "No")]))
    return ASK_MARRIED


async def ask_married(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    ctx.user_data["ever_married"] = q.data
    await q.edit_message_text(s(ctx, "q_work"), parse_mode="Markdown", reply_markup=kb(
        [(s(ctx, "btn_govt"), "Govt_job"), (s(ctx, "btn_private"), "Private")],
        [(s(ctx, "btn_self"), "Self-employed"), (s(ctx, "btn_children"), "children")],
        [(s(ctx, "btn_never_work"), "Never_worked")],
    ))
    return ASK_WORK


async def ask_work(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    ctx.user_data["work_type"] = q.data
    await q.edit_message_text(s(ctx, "q_residence"), parse_mode="Markdown", reply_markup=kb([(s(ctx, "btn_rural"), "Rural"), (s(ctx, "btn_urban"), "Urban")]))
    return ASK_RESIDENCE


async def ask_residence(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    ctx.user_data["residence_type"] = q.data
    await q.edit_message_text(s(ctx, "q_glucose"), parse_mode="Markdown")
    return ASK_GLUCOSE


async def ask_glucose(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        val = float(update.message.text.strip())
        if val < 40 or val > 500: raise ValueError
        ctx.user_data["avg_glucose_level"] = val
        await update.message.reply_text(s(ctx, "q_bmi"), parse_mode="Markdown")
        return ASK_BMI
    except ValueError:
        await update.message.reply_text(s(ctx, "invalid_glucose"))
        return ASK_GLUCOSE


async def ask_bmi(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        val = float(update.message.text.strip())
        if val < 10 or val > 100: raise ValueError
        ctx.user_data["bmi"] = val
        await update.message.reply_text(s(ctx, "q_smoking"), parse_mode="Markdown", reply_markup=kb(
            [(s(ctx, "btn_smokes"), "smokes"), (s(ctx, "btn_former"), "formerly smoked")],
            [(s(ctx, "btn_never_smk"), "never smoked"), (s(ctx, "btn_unknown"), "Unknown")],
        ))
        return ASK_SMOKING
    except ValueError:
        await update.message.reply_text(s(ctx, "invalid_bmi"))
        return ASK_BMI


async def ask_smoking(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    ctx.user_data["smoking_status"] = q.data

    await q.edit_message_text(s(ctx, "analyzing"), parse_mode="Markdown")

    try:
        res = run_prediction_api(ctx.user_data)
        
        prob_pct = res["probability"] * 100
        filled = int(prob_pct / 10)
        bar = "█" * filled + "░" * (10 - filled)

        d = ctx.user_data
        yes_str = s(ctx, "yes")
        no_str = s(ctx, "no")

        msg = (
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{s(ctx, 'result_header')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{s(ctx, 'result_prob')} `{prob_pct:.1f}%`\n"
            f"`[{bar}] {prob_pct:.1f}%`\n\n"
            f"{s(ctx, 'result_risk')} *{res['risk_level']} {res['risk_color']}*\n"
            f"{s(ctx, 'result_model')} {res['model_used'].replace('_', ' ').title()}\n\n"
            f"{s(ctx, 'result_data')}\n"
            f"• {s(ctx, 'result_label_gender')}: {d['gender']}\n"
            f"• {s(ctx, 'result_label_age')}: {d['age']:.0f} {s(ctx, 'years')}\n"
            f"• {s(ctx, 'result_label_hype')}: {yes_str if d['hypertension'] else no_str}\n"
            f"• {s(ctx, 'result_label_heart')}: {yes_str if d['heart_disease'] else no_str}\n"
            f"• {s(ctx, 'result_label_smoking')}: {d['smoking_status']}\n"
            f"• {s(ctx, 'result_label_glucose')}: {d['avg_glucose_level']:.1f} mg/dL\n"
            f"• {s(ctx, 'result_label_bmi')}: {d['bmi']:.1f}\n\n"
            f"{s(ctx, 'result_rec')}\n"
        )
        for rec in res["recommendations"]:
            msg += f"• {rec}\n"

        restart_kb = InlineKeyboardMarkup([[InlineKeyboardButton(s(ctx, "btn_restart"), callback_data="restart")]])
        await q.message.reply_text(msg, parse_mode="Markdown", reply_markup=restart_kb)

    except Exception as e:
        logger.error("API error: %s", e)
        retry_kb = InlineKeyboardMarkup([[InlineKeyboardButton(s(ctx, "btn_restart"), callback_data="restart")]])
        await q.message.reply_text(s(ctx, "error"), parse_mode="Markdown", reply_markup=retry_kb)

    return ConversationHandler.END


async def restart_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    return await start(update, ctx)


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(s(ctx, "cancelled"), parse_mode="Markdown")
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in .env!")
        return

    application = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(restart_callback, pattern="^restart$"),
        ],
        states={
            CHOOSE_LANG:     [CallbackQueryHandler(choose_lang, pattern="^lang_(id|en)$")],
            CHOOSE_MODEL:    [CallbackQueryHandler(choose_model, pattern="^(logistic_regression|decision_tree|knn)$")],
            ASK_GENDER:      [CallbackQueryHandler(ask_gender, pattern="^(Male|Female)$")],
            ASK_AGE:         [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
            ASK_HYPERTENSION:[CallbackQueryHandler(ask_hypertension, pattern="^[01]$")],
            ASK_HEART:       [CallbackQueryHandler(ask_heart, pattern="^[01]$")],
            ASK_MARRIED:     [CallbackQueryHandler(ask_married, pattern="^(Yes|No)$")],
            ASK_WORK:        [CallbackQueryHandler(ask_work, pattern="^(Govt_job|Private|Self-employed|children|Never_worked)$")],
            ASK_RESIDENCE:   [CallbackQueryHandler(ask_residence, pattern="^(Rural|Urban)$")],
            ASK_GLUCOSE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_glucose)],
            ASK_BMI:         [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_bmi)],
            ASK_SMOKING:     [CallbackQueryHandler(ask_smoking, pattern="^(smokes|formerly smoked|never smoked|Unknown)$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    application.add_handler(conv)

    logger.info("🚀 Sana AI API Bot is running locally... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    import time
    while True:
        try:
            main()
        except Exception as e:
            logger.error(f"Bot crashed with error: {e}")
            logger.info("Restarting bot in 10 seconds...")
            time.sleep(10)
