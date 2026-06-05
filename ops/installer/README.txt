JoJo Bot - Desktop App
======================

WHAT THIS IS
------------
JoJo Bot is a self-contained desktop application. Everything it needs -
the Python runtime, the web UI, and the knowledge base - is bundled inside
the JojoBot\ folder. No Python, Node, browser, or internet connection is
required to run it.

FOLDER LAYOUT (do not rearrange)
--------------------------------
The knowledge base lives INSIDE the JojoBot\ folder, next to the .exe:

    JojoBot\
        JojoBot.exe        <- double-click this to launch
        _internal\         <- Python runtime + Qt libraries (do not move/delete)
        wiki\              <- the compiled knowledge base (Q&A memory)
        raw\               <- source documents (private; omitted in -SkipRaw builds)
        README.txt         <- this file

Keep wiki\ and raw\ inside the JojoBot\ folder. If you move JojoBot.exe,
move the whole folder.

HOW TO RUN
----------
Double-click JojoBot.exe. After a few seconds JoJo Bot opens in its own
application window (a native desktop window - there is NO separate browser
and NO console window). Use the tabs across the top: Chat, Wiki, Raw, Graph,
Ops, Settings.

To stop JoJo Bot: close the window.

FIRST RUN
---------
Antivirus software sometimes inspects a newly built .exe on first launch,
which can delay startup by 10-30 seconds. If the window does not appear,
wait a moment before retrying. To answer questions, open the Settings tab
and paste an Anthropic API key (Chat works without one in retrieval-only
mode; live answer synthesis needs the key).

WHERE ARE THE LOGS
------------------
%LOCALAPPDATA%\JojoBot\launcher.log
Open this file if the app fails to start; it records startup and any errors.

TROUBLESHOOTING
---------------
"Wiki tab shows 0 pages"
    The wiki\ folder must sit inside the JojoBot\ folder, next to JojoBot.exe.

"Raw tab is empty"
    The raw\ folder must sit inside the JojoBot\ folder. Builds made with
    -SkipRaw intentionally omit it; Chat and Wiki still work.

"The window never appears"
    Check %LOCALAPPDATA%\JojoBot\launcher.log. The launcher picks a free
    local port automatically (it prefers 8766), so a busy port is not fatal.
    Add an antivirus exception for JojoBot.exe if it is being blocked.

TO SHARE
--------
Zip the entire JojoBot\ folder and send it. The recipient unzips it and
double-clicks JojoBot.exe. Note: builds that include raw\ contain private
source documents - use a -SkipRaw build for wider distribution.
