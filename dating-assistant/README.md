# dating-assistant

A local MCP server that turns Claude into a personal dating assistant: it stores
profiles, preferences, conversations and message drafts that **you** type or paste
in, and gives Claude structured context to reason over.

## What it deliberately does not do

This project never touches Hinge or any other dating service. It does not:

- automate, script or drive any dating app or its website
- scrape profiles, matches or messages
- call undocumented or reverse-engineered APIs
- automate login, swiping, liking, matching or messaging
- store credentials, passwords or session cookies
- inspect network traffic

Everything in the database got there because you pasted it in. Every draft is
text for you to copy and send yourself. If a future feature would need direct
interaction with a service, the right move is to check whether that service
offers an authorized API — not to work around its absence.

## Requirements

- Node.js **22.5 or newer** (uses the built-in `node:sqlite` module — no native build step)
- Claude Desktop or Claude Code

## Install

```bash
cd "dating-assistant"
npm install
npm run build
```

The database is created on first run at `data/assistant.db`. Override the
location with the `DATING_ASSISTANT_DB` environment variable.

## Connect to Claude Desktop

Add the server to your Claude Desktop config, using an **absolute path** to the
built `dist/index.js`:

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "dating-assistant": {
      "command": "node",
      "args": [
        "C:\\Users\\sriva\\Desktop\\Me\\hine automation\\dating-assistant\\dist\\index.js"
      ]
    }
  }
}
```

See `claude_desktop_config.example.json`. Restart Claude Desktop, then check the
tool list — you should see `add_profile`, `analyze_profile` and the rest.

The transport is **stdio only**. Do not put this behind ngrok, a Cloudflare
tunnel, a port forward, or any public HTTP endpoint.

## Connect to Claude Code

```bash
claude mcp add dating-assistant -- node "C:\Users\sriva\Desktop\Me\hine automation\dating-assistant\dist\index.js"
```

## Tools

| Tool | Purpose |
| --- | --- |
| `add_profile` | Store a profile you typed in (`name`, `age`, `occupation`, `location`, `bio`, `notes`) |
| `get_profile` | Fetch one stored profile by id |
| `list_profiles` | List stored profiles, newest first (`limit`) |
| `set_preference` | Save/update one of your preferences by `category` |
| `get_preferences` | Return all saved preferences |
| `analyze_profile` | Return structured raw material about a profile — it does not decide |
| `add_conversation` | Store conversation text you pasted in |
| `get_conversation` | Return the conversation entries for a profile |
| `draft_reply` | Return profile + preferences + conversation so Claude can write a draft |
| `save_draft` | Save a draft locally |
| `list_drafts` | List saved drafts, optionally per profile |

Preferences are keyed by category — setting the same category twice updates it.
Common categories: `communication style`, `interests`, `deal breakers`,
`conversation preferences`, `relationship goals`.

`analyze_profile` runs a plain text heuristic over the bio and notes. It returns
possible interests, conversation topics, questions to consider, preference
overlaps and explicit uncertainties. It produces no score and no recommendation
— Claude and you do the reasoning.

## Example Claude prompts

Setting up your preferences once:

```
Save my preferences: communication style is dry and playful, deal breakers are
smoking and not having any hobbies, relationship goals is something serious
within a year.
```

Adding a profile you are looking at:

```
Add this profile:
24
Software engineer
Likes hiking, coffee and photography.

Prompt: "My simple pleasures..."
"Finding a new coffee shop and spending three hours there."
```

Then:

```
Analyze profile 1 and tell me the strongest opener hook.
```

Claude might answer:

> The strongest conversation hook is the coffee-shop prompt.
>
> Possible opener: "You've got three hours in a new city and one coffee shop.
> What are you ordering?"

You type that into the app yourself.

Pasting a conversation and getting a reply drafted:

```
Here's the conversation with profile 1 so far, save it:
them: ok but a three hour coffee is a commitment
me: it's a lifestyle

Now draft me two replies that keep it playful and ask about their photography.
Save the one you like best.
```

Reviewing later:

```
List my profiles and show me the drafts I saved for profile 1.
```

## Tests

```bash
npm test
```

Covers database operations, tool schemas, invalid input, missing profile ids,
preference and draft persistence, the analysis heuristic, and an end-to-end
integration test over an in-memory MCP transport:

```
Claude client -> MCP -> add_profile -> SQLite -> get_profile -> Claude client
```

No test touches the network or any dating service.

## Layout

```
dating-assistant/
├── src/
│   ├── index.ts            stdio entrypoint
│   ├── server.ts           MCP server + tool registration
│   ├── tools/              profile, preferences, messages, analysis
│   ├── db/                 database.ts, schema.ts
│   └── types/              shared row types
└── data/                   SQLite file (gitignored)
```
