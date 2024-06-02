# Email to Audio Transcription Script

## Introduction
This Python script automates the process of converting email text to audio files using OpenAI's transcription services. The script:
- Retrieves and processes unread emails with a specific subject.
- Uses OpenAI's API to transcribe the email content to audio.
- Sends the transcribed audio file back to the sender.

## Prerequisites
Before using this script, ensure you have the following:
- Python, tested on 3.12
- An OpenAI API key
- An email address you can monitor

## Installation

### Clone the Repository:
```bash
git clone https://github.com/adrianhensler/ajh_ai_tools.git
cd ajh_ai_tools
```

### Install Dependencies:
Create a virtual environment (optional but recommended):
```bash
python3 -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
```
Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables
Set the following environment variables in a `.env` file for the script to function correctly:

- `AITOOLS_IMAP_SERVER`: Your IMAP server (e.g., imap.example.com)
- `AITOOLS_IMAP_PORT`: Your IMAP server port (e.g., 993)
- `AITOOLS_SMTP_SERVER`: Your SMTP server (e.g., smtp.example.com)
- `AITOOLS_SMTP_PORT`: Your SMTP server port (e.g., 587)
- `AITOOLS_EMAIL_ACCOUNT`: Your email account
- `AITOOLS_EMAIL_PASSWORD`: Your email account password
- `OPENAI_API_KEY`: Your OpenAI API key
- `FORCE_MODERATION`: Force content moderation (true/false)
- `DISABLE_MODERATION`: Disable content moderation (true/false)

Example configuration in a `.env` file:
```env
AITOOLS_IMAP_SERVER=imap.example.com
AITOOLS_IMAP_PORT=993
AITOOLS_SMTP_SERVER=smtp.example.com
AITOOLS_SMTP_PORT=587
AITOOLS_EMAIL_ACCOUNT=your-email@example.com
AITOOLS_EMAIL_PASSWORD=yourpassword
OPENAI_API_KEY=your-openai-api-key
FORCE_MODERATION=true
DISABLE_MODERATION=false
```

## Usage
Run the Script:
```bash
python3 ajh_tts_email.py
```

### Email Subject Format
The script looks for emails with the subject "TTS". You can specify the voice model in the subject (e.g., "TTS: onyx"). Available models are:
- alloy
- echo
- fable
- onyx (default)
- nova
- shimmer

### Running in a Loop
To run the script in a loop (checking for new emails every minute), use the `--loop` flag:
```bash
python3 ajh_tts_email.py --loop
```
### Character limit
A character limit is set at 2000 characters via "MAX_CHARACTER_COUNT = 2000  # Set your desired limit" in the code. Adjust as required.

### Setting up as a Cron Job
To run the script as a cron job every 5 minutes, add the following line to your crontab file (`crontab -e`):
```bash
*/5 * * * * /path/to/your/virtualenv/bin/python /path/to/ajh_tts_email.py >> /path/to/logfile.log 2>&1
```

### Log Messages
Log messages are configured to be printed to the console. You can redirect them to a file by modifying the logging configuration in the script.

## Security Considerations
- **Handling Sensitive Information:** Ensure that your environment variables, especially those containing passwords and API keys, are kept secure and not hard-coded in the script.
- **Best Practices:** Use environment variable management tools like dotenv for secure and convenient handling.

## Troubleshooting

Please note that the core functionality has been tested fairly well. That is running with and without --loop, changing voices with the "TTS: fable" format in the email subject line,
sending the text to the moderation endpoint, then sending the audio back to the sender.

Moderation variables and logic has not been fully tested. These options should be considered untested examples to be used and tested at your own risk.

I've added another document that may assist if you wish to run this as a cron job.

### Common Issues
- **Missing Environment Variables:** Ensure all required environment variables are set.
- **Connection Errors:** Verify your email server details and internet connection.
- **Processing Failures:** Check logs for any errors related to the OpenAI API or email processing.

### Log Messages
Check the log output for detailed error messages and follow the recommendations.

## Future Development Ideas
- **Enhanced Error Handling:** Improve robustness with more granular error handling.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.
