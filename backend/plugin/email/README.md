# Email

Email plug-in, provides email sending function, supports verification codes, notifications and other scenarios

## Global configuration

Add the following content to `backend/core/conf.py`:

```python
################################################
#[Plugin]email
################################################
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