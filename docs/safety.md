# Safety, privacy and terms

## Terms of Service

Automating Hinge is against Hinge's Terms of Service. Using this project can get
your account restricted or banned. You use it at your own risk, on your own
account. The authors are not affiliated with Hinge or Match Group.

## What the tool will do

- In ask mode (the default): scroll each profile and wait for your `y`, `n` or
  `q`. It likes only after `y`, and lets you keep, rewrite or drop the comment.
- In auto mode (`--auto`, or **Auto** in the web page): like every profile it
  scans, without asking, until the cap. Use it only when you are fine with every
  profile Hinge shows you getting a like and the comment the tool picks.
- Stop for the day at `--cap` likes (default 5) in both modes.
- Stop, without tapping, whenever the screen is not what it expects.

## What the tool will not do

- Run in the background or on a schedule. A run lasts until the cap, `q`,
  **Stop** or Ctrl+C.
- Send messages in chats.
- Tap Rose, Boost, HingeX, subscription or any purchase control. When the
  "Send a Rose instead?" sheet appears, it taps **Send Like anyway**.
- Change your profile, settings or account.
- Bypass Hinge's screen protection. Screenshots come from the emulator window
  on your own screen.

Hinge's like button may be labelled "Send Priority Like". On the account used to
build this tool that cost nothing. Check yours: if sending a like would spend
anything, stop and do not use `run`.

## Other people's data

Each sent like saves the frames of that person's profile and a short record under
`people/`. That is personal data about someone who did not agree to it.

- `people/` is in `.gitignore`. Never commit it, share it or upload it.
- Delete folders you no longer need.
- Vision comments (`--model`) and the capture hotkey send a screenshot of the
  profile to the model provider you choose (Anthropic, OpenAI, or Anthropic
  through the `claude` CLI). Their data policies apply to it.
- The SQLite database (`dating-assistant/data/assistant.db`) holds profile text
  and drafts. It is gitignored too.

## Reporting a problem

If the tool ever taps something it should not, stop it with Ctrl+C and open an
issue with the message it printed and, if you are comfortable sharing it, the
saved frame with any personal details cropped out.
