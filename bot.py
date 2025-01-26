from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from transformers import pipeline
import torch
import logging 

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define the /start command (make it async)
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I am TX-7. How can I assist you today?")

# Load the API token securely
API_TOKEN = "8157175827:AAFTVSWuQYWMR7_bXAXr9rNkZfMsn2JImGM"
if not API_TOKEN:
    raise ValueError("API token is missing. Please set the TELEGRAM_API_TOKEN environment variable.")
logger.info(f"Using API token: {API_TOKEN[:5]}...")  # Log first 5 characters for verification

# Load the text-generation pipeline (using GPU)
pipe = pipeline(
     "text-generation",
    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    torch_dtype=torch.float16,
    device=0,  # Use GPU
    max_length=150,  # Limit the response length
    no_repeat_ngram_size=2,  # Avoid repeating phrases
    temperature=0.7  # Reduce randomness
)

# Generate responses
def generate_response(input_text):
    response = pipe(input_text, truncation=True, max_length=150, num_return_sequences=1)
    generated_text = response[0]["generated_text"]

    # Filter for relevancy
    if "sports" in input_text.lower() and "team" not in generated_text.lower():
        return "I'm sorry, I couldn't provide a relevant answer. Please try again."
    return generated_text

# Define the message handler (this should be async)
async def unknown_message(update: Update, context: CallbackContext):
    user_input = update.message.text
    logger.info(f"User input: {user_input}")

    # Generate the bot's response
    bot_response = generate_response(user_input)

    # Log and send the response
    logger.info(f"Bot Response: {bot_response}")
    await update.message.reply_text(bot_response.strip())  # Clean up whitespace

# Main function
def main():
    # Initialize the application with the API token
    application = Application.builder().token(API_TOKEN).build()

    # Add the /start command handler
    application.add_handler(CommandHandler("start", start))

    # Add the message handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    # Start the bot
    application.run_polling()
    logger.info("Bot is running...")

if __name__ == "__main__":
    main()
