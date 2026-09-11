# Email

Email plugin providing email delivery for verification codes, notifications, and other scenarios

- Supports sending email through SMTP
- Supports verification-code, notification, and other email scenarios
- Supports basic settings for the email service, verification-code lifetime, and Redis prefix

## plugin type

- Application-level plugin

## Configuration instructions

Add the following content to `backend/.env`:

```env
# [ Plugin ] email
EMAIL_USERNAME=''
EMAIL_PASSWORD=''
```

The `[settings]` section of `plugin.toml` in the plugin directory contains:

```toml
[settings]
EMAIL_CAPTCHA_EXPIRE_SECONDS = 180
EMAIL_CAPTCHA_REDIS_PREFIX = 'example:email:captcha'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 465
EMAIL_SSL = true
```

The current project's `backend/core/conf.py` already contains these fields:

```python
##################################################
# [ Plugin ] email
##################################################
# .env
EMAIL_USERNAME: str
EMAIL_PASSWORD: str

# Basic configuration(in plugin.toml)
EMAIL_HOST: str
EMAIL_PORT: int
EMAIL_SSL: bool
EMAIL_CAPTCHA_REDIS_PREFIX: str
EMAIL_CAPTCHA_EXPIRE_SECONDS: int
```

## Setting descriptions

- `EMAIL_CAPTCHA_EXPIRE_SECONDS`:Controls the email verification-code lifetime
- `EMAIL_CAPTCHA_REDIS_PREFIX`:Controls the Redis key prefix for email verification codes
- `EMAIL_HOST`:Controls the SMTP server address
- `EMAIL_PORT`:Controls the SMTP port
- `EMAIL_SSL`:Controls whether SSL is enabled

## Usage

1. After installing and enabling the plugin, configure valid SMTP credentials
2. Update these values for your email provider `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_SSL`
3. Restart the backend, then use email through the UI, Swagger, or application code

## Uninstall instructions

- After uninstalling the plugin, remove its environment variables, basic settings, and configuration from `backend/core/conf.py`
- If application code still uses email delivery, remove the corresponding integration

## Contact information

- author:`wu-clan`
- Feedback: submit an issue or pull request
