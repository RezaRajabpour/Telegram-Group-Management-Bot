# Telegram Group Management Bot

This script automates **group moderation in Telegram**.\
It checks messages for **banned words**, warns users, mutes them after 3
warnings, and can **lock/unlock the group** via commands.\
It's a lightweight and useful utility for group admins who want to keep
chats safe and organized.

## Installation

Make sure you have **Python 3.10+** installed.

### Create and activate a virtual environment

~~~
python -m venv venv
venv\Scripts\activate
~~~

### Install required libraries

``` bash
pip install python-telegram-bot
```

## Imported Libraries Description

-   **os** → File handling (checking existence, reading/writing).
-   **json** → Save & load warning data.
-   **datetime, timedelta** → Manage mute duration and warning expiry.
-   **telegram.ChatPermissions** → Control user permissions in groups.
-   **telegram.ext** → Manage message & command handlers
    (`MessageHandler`, `CommandHandler`).
-   **asyncio jobs (JobQueue)** → Automatically clear warnings after 24
    hours.

------------------------------------------------------------------------

## Key Elements & Functions in the Code

-   `BANNED_WORDS_FILE (a.txt)` → Text file containing banned words
    (UTF-8, one per line).
-   `WARNINGS_FILE (warning.json)` → Stores user warnings in JSON
    format.
-   `load_warnings()` / `save_warnings()` → Handle warning data
    persistence.
-   `check_message()` → Scans every message, issues warnings, and mutes
    after 3 violations.
-   `mute_user()` → Restricts a user from sending messages for 24 hours.
-   `clear_user_warnings()` → Clears user warnings automatically after
    24 hours.
-   `/lock` → Command to lock the group (disable sending messages).
-   `/unlock` → Command to unlock the group (enable sending messages).
-   `main()` → Initializes bot and starts polling.

------------------------------------------------------------------------

## How to Run

1.  Get a **bot token** from BotFather and replace it in the `TOKEN`
    variable.
2.  Create a file `a.txt` with your banned words (one word per line).
3.  Run the script:

``` bash
python a.py
```
## Example Files

**a.txt**

    badword1
    badword2
    badword3

**warning.json** (auto-generated)
## Notes

-   The bot **must be admin** in the group with permission to restrict
    members.
-   After **3 warnings**, the user is muted for **24 hours**.
-   Warnings are **auto-cleared after 24 hours** from the first
    violation.
-   `/lock` and `/unlock` commands can only be used by admins.
-   Keep your **TOKEN private** and never push it to public
    repositories.