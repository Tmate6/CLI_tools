# Discord Spammer

Uses pynput to spam send specified messages on Discord. Detects and avoids rate limits by recognising the pop-up.

### Arguments

messages: Messages to send, seperated by a comma (use \, to include command in message) (string)
amount: Amount of messages to send (int)
rotation: Randomly rotate the order of the messages (bool)
verbose: Verbose mode (bool)
