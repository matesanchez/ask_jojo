# JoJo Bot - User Guide

JoJo Bot is Nurix's internal knowledge assistant. It reads a curated, continuously
maintained wiki built from the company's documents and answers questions against it,
with every answer traceable back to a source document. This guide explains how to use
the app day to day.

## Starting the app

Double-click `JojoBot.exe` inside the `JojoBot\` folder. JoJo Bot opens in its own
desktop window after a few seconds (there is no console window and no separate browser
tab). To stop it, close the window.

The first time you use it, open the **Settings** tab and paste an Anthropic API key.
Without a key, JoJo Bot still retrieves and shows you the relevant wiki content; with a
key, it also writes a synthesized answer on top of that content.

## The tabs

**Chat** - Ask questions in natural language. JoJo Bot routes the question, retrieves
the relevant wiki pages, and (with an API key configured) writes an answer that cites
the pages it used. Badges on each answer show how the question was routed and what
output format was chosen. You can adjust answer depth, and use "File this" to save a
useful answer back into the wiki's `outputs/` area. For relational questions ("how does
X connect to Y"), a "Show in graph" link reveals the connection visually.

**Wiki** - Browse the compiled knowledge base. The left pane is a tree of pages; the
center renders the selected page (including charts, slide decks, and tables for
rich-output pages); the right pane shows the page's metadata and backlinks. Wikilinks
are clickable, so you can navigate between related topics. This is the "product" - the
synthesized understanding JoJo Bot answers from.

**Raw** - Inspect the original source documents behind the wiki. It is a three-pane view:
a source tree grouped by connector (SharePoint, OneDrive, public drive), a preview of the
selected document, and a metadata panel (title, source location, access level, hash,
fetched time). This is the audit surface - if you want to confirm where a wiki claim came
from, you trace it here. Raw documents are immutable: once ingested they never change, so
a citation always points to exactly what the wiki was written against.

**Graph** - A visual map of how topics in the wiki connect. It includes an interactive
3D "brain" view of the knowledge graph and a conventional node-link diagram. Use it to
explore relationships - which programs, targets, methods, and papers reference each other.

**Ops** - The operational dashboard: total wiki pages and last-update time, connector
health, whether an API key is configured, the background job queue, recent jobs, and
lint history (the automated checks that keep the wiki healthy). Use it to trigger an
absorb or sync and to see system status at a glance.

**Settings** - Runtime configuration without touching any files: your Anthropic API key,
the model tier, Microsoft Graph authentication (device-code or pasted token) for
SharePoint/OneDrive sync, connector folder paths, and the lint cadence. Changes are saved
to a per-user encrypted config; you do not need to restart for most of them.

## How answers stay trustworthy

Every wiki page cites the immutable source documents it was written from, by file path
and content hash. When JoJo Bot answers a question, it draws from those pages and points
back to them, so you can always verify a claim by following it to the Raw tab. If JoJo Bot
cannot find a source for something, it is designed to say so rather than guess.

## Tips

- If the **Wiki tab shows 0 pages** or the **Raw tab is empty**, the `wiki\` / `raw\`
  folders are missing from inside the `JojoBot\` folder - make sure you kept the whole
  folder together when copying or moving it.
- The knowledge base grows over time. New pages added by overnight maintenance runs appear
  in the `wiki\` folder and show up the next time you open the app - no reinstall needed.
- Logs live at `%LOCALAPPDATA%\JojoBot\launcher.log` if you ever need to report a problem.

## Getting help

For installation or building, see `BUILD-AND-INSTALL.md`. For how the knowledge base is
structured and maintained, see `ask_jojo_wiki/SCHEMA.md`.
