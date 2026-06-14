# Configuring the email relay to send through Gmail

SigBah sends mail through a single transport function (`_send` in
`backend/app/application/email_service.py`). By default it talks to the local
Postfix → Mailpit relay with no authentication. The relay also supports
authenticated, TLS-encrypted SMTP, which is what Gmail requires.

This guide covers the **Gmail SMTP + App Password** path, which is the
recommended option for transactional mail.

## Before you start: which account?

Gmail only lets you send as the **authenticated account** or a **verified
"Send mail as" alias** on it. Pick the sending account accordingly:

- **Personal `@gmail.com` account** — works, but the `From` will always be that
  Gmail address. Set a `Reply-To` so replies reach the PPG inbox.
- **Institutional `@if.ufrgs.br` account** — only works if the domain is on
  **Google Workspace**. Note that Workspace admins frequently **disable App
  Passwords**; if so, this path won't work and you'll need OAuth/the Gmail API
  (not covered here) or a personal Gmail with `Reply-To`.

## Step 1 — Turn on 2-Step Verification

App Passwords don't exist until 2FA is enabled.

1. Go to <https://myaccount.google.com> → **Security** (left sidebar).
2. Under "How you sign in to Google", click **2-Step Verification** →
   **Get started** and follow the prompts (it will ask for a phone number).
3. Confirm it shows **On** before continuing.

## Step 2 — Create the App Password

1. Go to <https://myaccount.google.com/apppasswords>
   (or Security → search "App passwords"; Google hides it well).
2. Re-enter your Google password if prompted.
3. Under **App name**, type something memorable, e.g. `SigBah backend`, then
   click **Create**.
4. A box shows a **16-character code** like `abcd efgh ijkl mnop`.

> You only see this code **once**. If you lose it, delete it on that page and
> create a new one. Treat it like a password.

## Step 3 — Put it in `backend/.env`

Copy the 16-character code and **remove the spaces**.

```ini
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=youraccount@gmail.com
SMTP_PASSWORD=abcdefghijklmnop        # the App Password, spaces removed
SMTP_FROM=youraccount@gmail.com       # must match the account or a verified alias
SMTP_REPLY_TO=ppgenfis@if.ufrgs.br    # optional: where replies should go
```

Restart the backend after editing `.env`.

## Environment variables reference

| Variable        | Default               | Purpose                                              |
| --------------- | --------------------- | ---------------------------------------------------- |
| `SMTP_HOST`     | `localhost`           | SMTP server hostname                                 |
| `SMTP_PORT`     | `2525`                | SMTP server port (Gmail: `587`)                      |
| `SMTP_USE_TLS`  | `false`               | `true` enables STARTTLS (required by Gmail)          |
| `SMTP_USER`     | *(empty)*             | Login user; when empty, no authentication is sent    |
| `SMTP_PASSWORD` | *(empty)*             | Login password / App Password                        |
| `SMTP_FROM`     | `sigbah@sigbah.local` | `From` address; must match the account or an alias   |
| `SMTP_REPLY_TO` | *(empty)*             | Optional `Reply-To` (e.g. the PPG address)           |

Leaving `SMTP_USER` empty and `SMTP_USE_TLS=false` keeps the original local
Mailpit behavior — no credentials needed for development.

## Troubleshooting

- **"App passwords" option is missing.** 2-Step Verification isn't on yet
  (do Step 1), or it's a Workspace account where the admin disabled App
  Passwords, or "Advanced Protection" is enabled.
- **`535 Username and Password not accepted`.** You used the normal account
  password instead of the App Password, or left spaces in it.
- **Mail sends but `From` shows your Gmail, not the PPG address.** Expected when
  the PPG address isn't a verified send-as alias on the account. Use
  `SMTP_REPLY_TO` so replies still reach the PPG inbox.
- **Connection times out.** Outbound port 587 may be firewalled on the host; in
  that case Gmail SMTP can't be used and you'd need the Gmail API (OAuth) route.

## Other providers

Any authenticated SMTP provider works with the same four `SMTP_*` knobs — only
the host/port and credentials change (e.g. UFRGS's own SMTP server, SendGrid,
Amazon SES). Gmail is just one example.
