JoJo Bot — Deployment Layout
=============================

To run JoJo Bot, place the JojoBot/ folder and the ask_jojo_wiki/ folder
side-by-side in the same parent directory:

    MyFolder\
    ├── JojoBot\          ← the folder you unzip
    │   ├── JojoBot.exe
    │   └── _internal\    ← do not delete or move
    └── ask_jojo_wiki\    ← your wiki content directory

Then double-click JojoBot.exe inside the JojoBot\ folder.

A console window will appear while JoJo Bot loads (keep it open — closing it
stops the app).  Your default browser will open automatically to
http://127.0.0.1:8766 once the server is ready.

To stop JoJo Bot: press Ctrl+C in the console window, or close it.

Clicking JojoBot.exe a second time while it is already running will just
open a new browser tab — it will NOT start a second server.


Troubleshooting
---------------

"Wiki shows 0 pages"
  → The ask_jojo_wiki\ folder must be a sibling of JojoBot\ (see layout above).
    If you moved the JojoBot\ folder, also move ask_jojo_wiki\ next to it.

"Port 8766 already in use" error
  → Another process is using that port.  Close the existing JoJo Bot window
    (or the other process) and try again.

"Server did not respond in 30s"
  → Check the console window for error messages.  Antivirus software sometimes
    blocks new executables on first launch — add an exception for JojoBot.exe.
