# 🎓 HSBI Grade Notifier

Automated grade monitoring for the **Hochschule Bielefeld (HSBI)** LSF portal. Receive instant Telegram notifications whenever a new grade is posted.

## 📋 Table of Contents
1. [Features](#-features)
2. [Telegram Bot Setup](#-telegram-bot-setup)
3. [GitHub Configuration](#-github-configuration)
4. [How to Start & Test](#-how-to-start--test)
5. [Troubleshooting & Debugging](#-troubleshooting--debugging)

## ✨ Features
* **Automated Checks:** Runs every 30 minutes via GitHub Actions.
* **Detailed Notifications:** Sends a full list of exams and grades directly to your phone.
* **Session Stability:** Uses custom navigation to bypass portal "Java Exceptions".
* **Visual Debugging:** Automatically captures screenshots if a login fails.

## 🤖 Telegram Bot Setup
You need a private bot to act as your personal notifier.

1. **Create your Bot:**
   * Message **@BotFather** on Telegram.
   * Use the `/newbot` command and follow the steps.
   * **Save the API Token:** (e.g., `123456:ABC-DEF...`). This is your `TELEGRAM_TOKEN`.
2. **Get your Chat ID:**
   * Message **@userinfobot** on Telegram.
   * It will reply with your unique **Id**. This is your `TELEGRAM_CHAT_ID`.
3. **Activate the Bot:**
   * Search for your new bot's name on Telegram and press **Start**.

## ⚙️ GitHub Configuration
After forking this repository, follow these steps to link your account.

### 1. Repository Secrets
1. Go to **Settings** > **Secrets and variables** > **Actions**.
2. Add the following four **New repository secrets**:
   * `HSBI_USER`: Your university login name.
   * `HSBI_PASS`: Your university password.
   * `TELEGRAM_TOKEN`: The token from BotFather.
   * `TELEGRAM_CHAT_ID`: The ID from userinfobot.

### 2. Permissions
1. Go to **Settings** > **Actions** > **General**.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Click **Save**.

## 🚀 How to Start & Test
1. Click the **Actions** tab at the top of the repository.
2. Click **"I understand my workflows, go ahead and enable them"**.
3. Select **University Grade Checker** from the sidebar.
4. Click **Run workflow** > **Run workflow**.

## 🛠️ Troubleshooting & Debugging
If the automation fails (Red X in Actions):
1. Click on the **failed run**.
2. Go to the **Summary** page in the left sidebar.
3. Scroll to the bottom to find **Artifacts**.
4. Download **bot-view** to see `first_view.png` and `debug_error.png`. These images show exactly what the bot saw during the failure.
