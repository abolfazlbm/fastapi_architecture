# Email

Email plug-in, provides email sending function, supports verification codes, notifications and other scenarios

- Support SMTP email sending
- Support email scenarios such as verification codes and notifications
- Supports controlling email service, verification code validity period and Redis prefix based on basic configuration

## Plug-in type

- Application-level plug-ins

## Configuration instructions

Add the following content to `backend/.env`:

```env
#[Plugin]email
EMAIL_USERNAME=''
EMAIL_PASSWORD=''
```

The `[settings]` of `plugin.toml` in the plugin directory contains the following content:

```toml
[settings]
EMAIL_CAPTCHA_EXPIRE_SECONDS = 180
EMAIL_CAPTCHA_REDIS_PREFIX = 'fba:email:captcha'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 465
EMAIL_SSL = true
```

Add the following content to `backend/core/conf.py`:

```python
###############################################
#[Plugin]email
###############################################
# .env
EMAIL_USERNAME:str
EMAIL_PASSWORD: str

#Basic configuration (in plugin.toml)
EMAIL_HOST: str
EMAIL_PORT: int
EMAIL_SSL: bool
EMAIL_CAPTCHA_REDIS_PREFIX: str
EMAIL_CAPTCHA_EXPIRE_SECONDS: int
```

## Usage

1. After installing and enabling the plug-in, configure the correct SMTP account and password
2. Modify `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_SSL` according to the actual email service provider
3. After restarting the backend service, use the email capability through the system page, Swagger or business code

## Uninstall instructions

- After uninstalling the plug-in, it is recommended to simultaneously remove the relevant environment variables, plug-in basic configuration and plug-in configuration in `backend/core/conf.py`
- If the business code is still using the email sending capability, please clean up the corresponding integration simultaneously.

## Contact information

- Author: `wu-clan`
- Feedback method: Submit an Issue or PR