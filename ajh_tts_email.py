import imaplib
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path
import openai
import os
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Email credentials and server details from environment variables
IMAP_SERVER = os.getenv('AITOOLS_IMAP_SERVER', 'imap.ionos.com')
IMAP_PORT = int(os.getenv('AITOOLS_IMAP_PORT', 993))
SMTP_SERVER = os.getenv('AITOOLS_SMTP_SERVER', 'smtp.ionos.com')
SMTP_PORT = int(os.getenv('AITOOLS_SMTP_PORT', 587))
EMAIL_ACCOUNT = os.getenv('AITOOLS_EMAIL_ACCOUNT')
EMAIL_PASSWORD = os.getenv('AITOOLS_EMAIL_PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Log the loaded environment variables (except sensitive information)
logging.info(f"IMAP_SERVER: {IMAP_SERVER}")
logging.info(f"IMAP_PORT: {IMAP_PORT}")
logging.info(f"SMTP_SERVER: {SMTP_SERVER}")
logging.info(f"SMTP_PORT: {SMTP_PORT}")

# Ensure sensitive environment variables are set
if not EMAIL_ACCOUNT or not EMAIL_PASSWORD or not OPENAI_API_KEY:
    logging.error("Missing essential environment variables. Please check your environment settings.")
    exit(1)

def check_email():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select('inbox')

        result, data = mail.search(None, '(UNSEEN SUBJECT "TTS")')
        email_ids = data[0].split()
        
        if not email_ids:
            logging.info("No new emails found.")
            return

        for email_id in email_ids:
            result, data = mail.fetch(email_id, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            from_email = msg['From']
            subject = msg['Subject']
            email_body = extract_email_body(msg)
            
            if email_body:
                # Check if the content is safe using OpenAI's moderation endpoint
                if is_content_safe(email_body):
                    voice_model = extract_voice_model(subject)
                    transcribed_audio_path = transcribe_text_to_audio(email_body, voice_model)
                    if transcribed_audio_path:
                        send_email(from_email, subject, transcribed_audio_path)
                        # Mark email as read after successful processing
                        mail.store(email_id, '+FLAGS', '\\Seen')
                    else:
                        logging.error(f"Failed to transcribe and send email for {from_email}")
                else:
                    logging.warning(f"Email from {from_email} contained inappropriate content and was not processed.")

    except Exception as e:
        logging.error(f"Error checking email: {e}")
    finally:
        mail.logout()

def extract_email_body(msg):
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode('utf-8')
        else:
            return msg.get_payload(decode=True).decode('utf-8')
    except Exception as e:
        logging.error(f"Error extracting email body: {e}")
    return None

def extract_voice_model(subject):
    models = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
    for model in models:
        if model in subject.lower():
            return model
    return 'onyx'  # Default voice model

def is_content_safe(text):
    try:
        response = openai.Moderation.create(input=text)
        results = response["results"][0]
        if results["flagged"]:
            return False
        return True
    except Exception as e:
        logging.error(f"Error checking content safety: {e}")
        return False

def transcribe_text_to_audio(text, voice_model='onyx'):
    try:
        openai.api_key = OPENAI_API_KEY
        speech_file_path = Path(__file__).parent / "speech.mp3"

        response = openai.Audio.create(
            model="whisper-1",
            input=text,
            voice=voice_model
        )
        
        audio_data = response['data']
        
        with open(speech_file_path, 'wb') as audio_file:
            audio_file.write(audio_data)

        return speech_file_path
    except Exception as e:
        logging.error(f"Error transcribing text to audio: {e}")
        return None

def send_email(to_email, subject, audio_file_path):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ACCOUNT
        msg['To'] = to_email
        msg['Subject'] = subject

        # Adding the body text to the email
        body = "Thanks for using ai_tools@adrianhensler.com. Please find the transcribed audio file attached."
        msg.attach(MIMEText(body, 'plain'))

        # Adding the audio attachment
        with open(audio_file_path, 'rb') as audio_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(audio_file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename='transcribed_audio.mp3')
            msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ACCOUNT, to_email, msg.as_string())
            logging.info(f"Email sent to {to_email}")

    except Exception as e:
        logging.error(f"Error sending email: {e}")

if __name__ == "__main__":
    try:
        while True:
            check_email()
            time.sleep(60)  # Check for new emails every minute
    except KeyboardInterrupt:
        logging.info("Service interrupted by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
