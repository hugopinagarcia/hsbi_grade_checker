#🎓 HSBI Grade Notifier

Automated grade monitoring for the Hochschule Bielefeld (HSBI) LSF portal. Receive instant Telegram notifications whenever a new grade is posted.
📋 Table of Contents

    Features

    Telegram Bot Setup

    GitHub Configuration

    How to Start & Test

    Troubleshooting & Debugging

✨ Features

    Automated Checks: Runs every 30 minutes via GitHub Actions.

    Detailed Notifications: Sends a full list of exams and grades directly to your phone.

    Session Stability: Uses custom navigation to bypass portal "Java Exceptions".

    Visual Debugging: Automatically captures screenshots if a login fails.

🤖 Telegram Bot Setup

You need a private bot to act as your personal notifier.

    Create your Bot:

        Message @BotFather on Telegram.

        Use the /newbot command and follow the steps.

        Save the API Token: (e.g., 123456:ABC-DEF...). This is your TELEGRAM_TOKEN.

    Get your Chat ID:

        Message @userinfobot on Telegram.

        It will reply with your unique Id. This is your TELEGRAM_CHAT_ID.

    Activate the Bot:

        Search for your new bot's name on Telegram and press Start.

⚙️ GitHub Configuration

After forking this repository, follow these steps to link your account.
1. Repository Secrets

    Go to Settings > Secrets and variables > Actions.

    Add the following four New repository secrets:

        HSBI_USER: Your university login name.

        HSBI_PASS: Your university password.

        TELEGRAM_TOKEN: The token from BotFather.

        TELEGRAM_CHAT_ID: The ID from userinfobot.

2. Permissions

    Go to Settings > Actions > General.

    Under Workflow permissions, select Read and write permissions.

    Click Save.

🚀 How to Start & Test

    Click the Actions tab at the top of the repository.

    Click "I understand my workflows, go ahead and enable them".

    Select University Grade Checker from the sidebar.

    Click Run workflow > Run workflow.

🛠️ Troubleshooting & Debugging

If the automation fails (Red X in Actions):

    Click on the failed run.

    Go to the Summary page in the left sidebar.

    Scroll to the bottom to find Artifacts.

    Download bot-view to see first_view.png and debug_error.png. These images show exactly what the bot saw during the failure.
