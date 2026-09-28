# Safety, privacy and terms

## Terms of Service

Automating Hinge is against Hinge's Terms of Service. Using this project can get
your account restricted or banned. You use it at your own risk, on your own
account. The authors are not affiliated with Hinge or Match Group.

## What the tool will do

- Scroll the profile on screen and ask you before every like.
- Send a like, with or without a comment, only after you type `y`.
- Tap **Skip** only after you type `n`.
- Stop for the day at `--cap` likes (default 5).
- Stop, without tapping, whenever the screen is not what it expects.

## What the tool will not do

- Like or skip anyone without your answer for that profile.
- Run in the background, on a schedule, or without a person at the keyboard.
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
- The capture tool sends a screenshot of the profile to the model provider you
  choose (Anthropic or OpenAI). Their data policies apply to it.
- The SQLite database (`dating-assistant/data/assistant.db`) holds profile text
  and drafts. It is gitignored too.

## Reporting a problem

If the tool ever taps something it should not, stop it with Ctrl+C and open an
issue with the message it printed and, if you are comfortable sharing it, the
saved frame with any personal details cropped out.
