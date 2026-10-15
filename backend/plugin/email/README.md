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

The following fields are already included in `backend/core/conf.py`:

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

## Configuration options

- `EMAIL_CAPTCHA_EXPIRE_SECONDS`: Email verification code validity period
- `EMAIL_CAPTCHA_REDIS_PREFIX`: Redis key prefix for email verification codes
- `EMAIL_HOST`: SMTP server address
- `EMAIL_PORT`: SMTP port
- `EMAIL_SSL`: Whether to enable SSL

## Usage

1. After installing and enabling the plug-in, configure the correct SMTP account and password
2. Modify `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_SSL` according to the actual email service provider
3. After restarting the backend service, use the email capability through the system page, Swagger or business code

## Uninstall instructions

- After uninstalling the plugin, remove its environment variables, basic settings, and configuration from `backend/core/conf.py`
- If application code still uses email delivery, remove the corresponding integration

## Contact information

- author:`wu-clan`
- Feedback: submit an issue or pull request
