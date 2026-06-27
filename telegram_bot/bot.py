"""
Sana AI - Telegram Bot (Fitur Opsional)
Bot screening risiko stroke yang terhubung dengan backend Sana AI.

Cara penggunaan:
1. Buat bot baru di Telegram via @BotFather
2. Salin token ke file .env (lihat .env.example)
3. Pastikan backend Sana AI sudah berjalan
4. Jalankan: python bot.py
"""

import os
import logging
import httpx
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Conversation states
(
    MODEL_SELECT,
    GENDER,
    AGE,
    HYPERTENSION,
    HEART_DISEASE,
    EVER_MARRIED,
    WORK_TYPE,
    RESIDENCE_TYPE,
    AVG_GLUCOSE,
    BMI,
    SMOKING_STATUS,
    CONFIRM,
) = range(12)

# Emoji constants
EMOJI_WAVE = "👋"
EMOJI_HEART = "💚"
EMOJI_CHECK = "✅"
EMOJI_WARNING = "⚠️"
EMOJI_CHART = "📊"
EMOJI_DOCTOR = "🩺"
EMOJI_THINK = "🤔"
EMOJI_LEAF = "🌿"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler untuk perintah /start."""
    user = update.effective_user
    context.user_data.clear()

    welcome_text = (
        f"Halo {user.first_name}! {EMOJI_WAVE}\n\n"
        f"{EMOJI_LEAF} Selamat datang di *Sana* — Screening Kesehatan Cerdas.\n\n"
        "Sana akan membantu Anda melakukan screening awal risiko stroke "
        "berdasarkan beberapa informasi kesehatan.\n\n"
        f"{EMOJI_WARNING} *Penting:* Hasil screening ini bukan diagnosis medis. "
        "Selalu konsultasikan dengan dokter profesional.\n\n"
        "Ketik /screening untuk memulai, atau /help untuk bantuan."
    )

    await update.message.reply_text(welcome_text, parse_mode="Markdown")
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk perintah /help."""
    help_text = (
        f"{EMOJI_LEAF} *Panduan Sana Bot*\n\n"
        "Perintah yang tersedia:\n"
        "/start — Mulai bot\n"
        "/screening — Mulai screening risiko stroke\n"
        "/batal — Batalkan screening yang sedang berjalan\n"
        "/help — Tampilkan bantuan ini\n\n"
        "Sana akan memandu Anda mengisi data kesehatan secara bertahap, "
        "kemudian memberikan hasil analisis risiko stroke.\n\n"
        f"{EMOJI_DOCTOR} Screening ini menggunakan model Machine Learning "
        "yang dilatih berdasarkan data WHO."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def start_screening(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Memulai proses screening — pilih model."""
    context.user_data.clear()
    context.user_data["model"] = "logistic_regression"  # Default

    keyboard = [
        [InlineKeyboardButton("✅ Logistic Regression (Direkomendasikan)", callback_data="logistic_regression")],
        [InlineKeyboardButton("🌳 Decision Tree (Akurasi Tinggi)", callback_data="decision_tree")],
        [InlineKeyboardButton("📐 K-Nearest Neighbors (Seimbang)", callback_data="knn")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        f"{EMOJI_CHART} *Pilih Model Analisis*\n\n"
        "• *Logistic Regression* — Paling sensitif mendeteksi stroke (Direkomendasikan)\n"
        "• *Decision Tree* — Akurasi keseluruhan tinggi\n"
        "• *KNN* — Pendekatan seimbang\n\n"
        "Kami merekomendasikan Logistic Regression untuk screening awal."
    )

    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return MODEL_SELECT


async def model_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback saat model dipilih."""
    query = update.callback_query
    await query.answer()

    model_names = {
        "logistic_regression": "Logistic Regression",
        "decision_tree": "Decision Tree",
        "knn": "K-Nearest Neighbors",
    }

    context.user_data["model"] = query.data
    model_name = model_names.get(query.data, query.data)

    await query.edit_message_text(
        f"{EMOJI_CHECK} Model dipilih: *{model_name}*\n\n"
        "Mari kita mulai! 😊\n\n"
        "Pertanyaan 1 dari 10:\n"
        "*Apa jenis kelamin Anda?*",
        parse_mode="Markdown",
    )

    keyboard = [["Laki-laki", "Perempuan"]]
    await query.message.reply_text(
        "Silakan pilih:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input gender."""
    text = update.message.text
    gender_map = {"Laki-laki": "Male", "Perempuan": "Female"}

    if text not in gender_map:
        await update.message.reply_text("Mohon pilih 'Laki-laki' atau 'Perempuan'.")
        return GENDER

    context.user_data["gender"] = gender_map[text]

    await update.message.reply_text(
        "Pertanyaan 2 dari 10:\n"
        "*Berapa usia Anda?* (dalam tahun)\n\n"
        "Contoh: 45",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )
    return AGE


async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input usia."""
    try:
        age_val = float(update.message.text)
        if age_val < 0 or age_val > 120:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Mohon masukkan usia yang valid (0-120). Contoh: 45")
        return AGE

    context.user_data["age"] = age_val

    keyboard = [["Ya", "Tidak"]]
    await update.message.reply_text(
        "Pertanyaan 3 dari 10:\n"
        "*Apakah Anda memiliki hipertensi (tekanan darah tinggi)?*",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode="Markdown",
    )
    return HYPERTENSION


async def hypertension(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input hipertensi."""
    text = update.message.text
    if text not in ["Ya", "Tidak"]:
        await update.message.reply_text("Mohon pilih 'Ya' atau 'Tidak'.")
        return HYPERTENSION

    context.user_data["hypertension"] = 1 if text == "Ya" else 0

    keyboard = [["Ya", "Tidak"]]
    await update.message.reply_text(
        "Pertanyaan 4 dari 10:\n"
        "*Apakah Anda memiliki riwayat penyakit jantung?*",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode="Markdown",
    )
    return HEART_DISEASE


async def heart_disease(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input penyakit jantung."""
    text = update.message.text
    if text not in ["Ya", "Tidak"]:
        await update.message.reply_text("Mohon pilih 'Ya' atau 'Tidak'.")
        return HEART_DISEASE

    context.user_data["heart_disease"] = 1 if text == "Ya" else 0

    keyboard = [["Ya", "Tidak"]]
    await update.message.reply_text(
        "Pertanyaan 5 dari 10:\n"
        "*Apakah Anda pernah menikah?*",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode="Markdown",
    )
    return EVER_MARRIED


async def ever_married(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input status pernikahan."""
    text = update.message.text
    if text not in ["Ya", "Tidak"]:
        await update.message.reply_text("Mohon pilih 'Ya' atau 'Tidak'.")
        return EVER_MARRIED

    context.user_data["ever_married"] = "Yes" if text == "Ya" else "No"

    keyboard = [["Karyawan Swasta", "Wiraswasta"], ["Pegawai Negeri", "Belum Bekerja"], ["Anak-anak"]]
    await update.message.reply_text(
        "Pertanyaan 6 dari 10:\n"
        "*Apa jenis pekerjaan Anda?*",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode="Markdown",
    )
    return WORK_TYPE


async def work_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input jenis pekerjaan."""
    work_map = {
        "Karyawan Swasta": "Private",
        "Wiraswasta": "Self-employed",
        "Pegawai Negeri": "Govt_job",
        "Belum Bekerja": "Never_worked",
        "Anak-anak": "children",
    }

    text = update.message.text
    if text not in work_map:
        await update.message.reply_text("Mohon pilih salah satu opsi pekerjaan yang tersedia.")
        return WORK_TYPE

    context.user_data["work_type"] = work_map[text]

    keyboard = [["Perkotaan", "Pedesaan"]]
    await update.message.reply_text(
        "Pertanyaan 7 dari 10:\n"
        "*Di mana tipe tempat tinggal Anda?*",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode="Markdown",
    )
    return RESIDENCE_TYPE


async def residence_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input tipe tempat tinggal."""
    residence_map = {"Perkotaan": "Urban", "Pedesaan": "Rural"}

    text = update.message.text
    if text not in residence_map:
        await update.message.reply_text("Mohon pilih 'Perkotaan' atau 'Pedesaan'.")
        return RESIDENCE_TYPE

    context.user_data["residence_type"] = residence_map[text]

    await update.message.reply_text(
        "Pertanyaan 8 dari 10:\n"
        "*Berapa rata-rata kadar glukosa darah Anda?* (mg/dL)\n\n"
        "💡 Normal saat puasa: 70-100 mg/dL\n"
        "Contoh: 85.5",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )
    return AVG_GLUCOSE


async def avg_glucose(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input kadar glukosa."""
    try:
        glucose_val = float(update.message.text)
        if glucose_val < 0 or glucose_val > 500:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Mohon masukkan angka yang valid (0-500). Contoh: 85.5")
        return AVG_GLUCOSE

    context.user_data["avg_glucose_level"] = glucose_val

    await update.message.reply_text(
        "Pertanyaan 9 dari 10:\n"
        "*Berapa Indeks Massa Tubuh (BMI) Anda?*\n\n"
        "💡 Normal: 18.5-24.9\n"
        "Rumus: Berat (kg) / Tinggi (m)²\n"
        "Contoh: 23.5",
        parse_mode="Markdown",
    )
    return BMI


async def bmi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input BMI."""
    try:
        bmi_val = float(update.message.text)
        if bmi_val < 5 or bmi_val > 100:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Mohon masukkan BMI yang valid (5-100). Contoh: 23.5")
        return BMI

    context.user_data["bmi"] = bmi_val

    keyboard = [
        ["Tidak Pernah Merokok", "Pernah Merokok"],
        ["Masih Merokok", "Tidak Diketahui"],
    ]
    await update.message.reply_text(
        "Pertanyaan 10 dari 10 (terakhir! 🎉):\n"
        "*Bagaimana status merokok Anda?*",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode="Markdown",
    )
    return SMOKING_STATUS


async def smoking_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input status merokok dan menampilkan konfirmasi."""
    smoking_map = {
        "Pernah Merokok": "formerly smoked",
        "Tidak Pernah Merokok": "never smoked",
        "Masih Merokok": "smokes",
        "Tidak Diketahui": "Unknown",
    }

    text = update.message.text
    if text not in smoking_map:
        await update.message.reply_text("Mohon pilih salah satu opsi yang tersedia.")
        return SMOKING_STATUS

    context.user_data["smoking_status"] = smoking_map[text]

    # Show confirmation summary
    data = context.user_data
    model_names = {
        "logistic_regression": "Logistic Regression",
        "decision_tree": "Decision Tree",
        "knn": "K-Nearest Neighbors",
    }
    gender_display = "Laki-laki" if data["gender"] == "Male" else "Perempuan"

    summary = (
        f"{EMOJI_CHECK} *Ringkasan Data Anda:*\n\n"
        f"🤖 Model: {model_names.get(data['model'], data['model'])}\n"
        f"👤 Gender: {gender_display}\n"
        f"🎂 Usia: {data['age']} tahun\n"
        f"💊 Hipertensi: {'Ya' if data['hypertension'] else 'Tidak'}\n"
        f"❤️ Penyakit Jantung: {'Ya' if data['heart_disease'] else 'Tidak'}\n"
        f"💍 Pernah Menikah: {'Ya' if data['ever_married'] == 'Yes' else 'Tidak'}\n"
        f"💼 Pekerjaan: {text}\n"
        f"🏠 Tempat Tinggal: {update.message.text}\n"
        f"🩸 Glukosa: {data['avg_glucose_level']} mg/dL\n"
        f"⚖️ BMI: {data['bmi']}\n"
        f"🚬 Merokok: {text}\n\n"
        "Apakah data di atas sudah benar?"
    )

    keyboard = [["✅ Ya, Analisis!", "❌ Batal"]]
    await update.message.reply_text(
        summary,
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode="Markdown",
    )
    return CONFIRM


async def confirm_and_predict(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Konfirmasi dan kirim ke API untuk prediksi."""
    text = update.message.text

    if "Batal" in text:
        await update.message.reply_text(
            "Screening dibatalkan. Ketik /screening untuk memulai kembali.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    await update.message.reply_text(
        f"{EMOJI_THINK} Sedang menganalisis data Anda...",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Prepare API request
    data = context.user_data
    payload = {
        "model": data.get("model", "logistic_regression"),
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

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{API_BASE_URL}/api/predict", json=payload)
            response.raise_for_status()
            result = response.json()

        # Format result
        risk_emoji = {"Rendah": "🟢", "Sedang": "🟡", "Tinggi": "🔴"}
        risk_level = result.get("risk_level", "Tidak diketahui")
        probability = result.get("probability", 0) * 100
        model_used = result.get("model_used", "Unknown")

        result_text = (
            f"{EMOJI_CHART} *Hasil Screening Sana*\n\n"
            f"{risk_emoji.get(risk_level, '⚪')} *Tingkat Risiko: {risk_level}*\n"
            f"📈 Probabilitas: *{probability:.1f}%*\n"
            f"🤖 Model: {model_used}\n\n"
        )

        # Contributing factors
        factors = result.get("contributing_factors", [])
        if factors:
            result_text += "*Faktor yang Mempengaruhi:*\n"
            impact_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            for factor in factors[:5]:
                emoji = impact_emoji.get(factor.get("impact", "low"), "⚪")
                result_text += f"  {emoji} {factor.get('factor', '')}: {factor.get('value', '')}\n"
            result_text += "\n"

        # Recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            result_text += "*Saran untuk Anda:*\n"
            for rec in recommendations[:4]:
                result_text += f"  ✅ {rec}\n"
            result_text += "\n"

        # Disclaimer
        result_text += (
            f"\n{EMOJI_WARNING} *Disclaimer:*\n"
            "Hasil ini hanya bersifat screening awal dan BUKAN diagnosis medis. "
            "Selalu konsultasikan dengan dokter atau tenaga medis profesional "
            "untuk evaluasi lebih lanjut.\n\n"
            "Ketik /screening untuk screening ulang."
        )

        await update.message.reply_text(result_text, parse_mode="Markdown")

    except httpx.ConnectError:
        await update.message.reply_text(
            "❌ Tidak dapat terhubung ke server Sana. "
            "Pastikan backend API sedang berjalan.\n\n"
            "Ketik /screening untuk mencoba lagi."
        )
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        await update.message.reply_text(
            "❌ Terjadi kesalahan saat menganalisis data. "
            "Silakan coba lagi nanti.\n\n"
            "Ketik /screening untuk mencoba lagi."
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Membatalkan screening."""
    await update.message.reply_text(
        "Screening dibatalkan. Ketik /screening kapan saja untuk memulai kembali. 😊",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def main() -> None:
    """Entry point utama bot."""
    if not TELEGRAM_TOKEN:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN tidak ditemukan!")
        print("Silakan salin .env.example menjadi .env dan isi token bot Anda.")
        print("Dapatkan token dari @BotFather di Telegram.")
        return

    # Build application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Conversation handler untuk screening
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("screening", start_screening)],
        states={
            MODEL_SELECT: [CallbackQueryHandler(model_selected)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            HYPERTENSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, hypertension)],
            HEART_DISEASE: [MessageHandler(filters.TEXT & ~filters.COMMAND, heart_disease)],
            EVER_MARRIED: [MessageHandler(filters.TEXT & ~filters.COMMAND, ever_married)],
            WORK_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, work_type)],
            RESIDENCE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, residence_type)],
            AVG_GLUCOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, avg_glucose)],
            BMI: [MessageHandler(filters.TEXT & ~filters.COMMAND, bmi)],
            SMOKING_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, smoking_status)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_and_predict)],
        },
        fallbacks=[CommandHandler("batal", cancel)],
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)

    # Run bot
    print(f"{EMOJI_LEAF} Sana Telegram Bot sedang berjalan...")
    print("Tekan Ctrl+C untuk menghentikan.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
