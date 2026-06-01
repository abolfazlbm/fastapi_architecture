#OAuth2

OAuth 2.0 third-party login plug-in supports login from social platforms such as GitHub and Google

-Support GitHub, Google third-party login
- Support third-party account binding and unbinding
- Support login bounce and binding bounce configuration

## Plug-in type

- Application-level plug-ins

## Configuration instructions

Add the following content to `backend/.env`:

```env
# [Plugin] oauth2
OAUTH2_GITHUB_CLIENT_ID='test'
OAUTH2_GITHUB_CLIENT_SECRET='test'
OAUTH2_GOOGLE_CLIENT_ID='test'
OAUTH2_GOOGLE_CLIENT_SECRET='test'
```

The `[settings]` of `plugin.toml` in the plugin directory contains the following content:

```toml
[settings]
OAUTH2_FRONTEND_BINDING_REDIRECT_URI = 'http://localhost:5173/profile'
OAUTH2_FRONTEND_LOGIN_REDIRECT_URI = 'http://localhost:5173/oauth2/callback'
OAUTH2_GITHUB_REDIRECT_URI = 'http://127.0.0.1:8000/api/v1/oauth2/github/callback'
OAUTH2_GOOGLE_REDIRECT_URI = 'http://127.0.0.1:8000/api/v1/oauth2/google/callback'
OAUTH2_STATE_EXPIRE_SECONDS = 180
OAUTH2_STATE_REDIS_PREFIX = 'fba:oauth2:state'
```

Add the following content to `backend/core/conf.py`:

```python
################################################
# [Plugin] oauth2
################################################
# .env
OAUTH2_GITHUB_CLIENT_ID: str
OAUTH2_GITHUB_CLIENT_SECRET: str
OAUTH2_GOOGLE_CLIENT_ID: str
OAUTH2_GOOGLE_CLIENT_SECRET: str

#Basic configuration (in plugin.toml)
OAUTH2_STATE_REDIS_PREFIX: str
OAUTH2_STATE_EXPIRE_SECONDS: int
OAUTH2_GITHUB_REDIRECT_URI: str
OAUTH2_GOOGLE_REDIRECT_URI: str
OAUTH2_FRONTEND_LOGIN_REDIRECT_URI: str
OAUTH2_FRONTEND_BINDING_REDIRECT_URI: str
```
## Usage

1. After installing and enabling the plug-in, create OAuth applications on GitHub and Google Open Platform respectively.
2. Configure the Client ID and Client Secret assigned by the platform into the project environment variables
3. Make sure the platform callback address is consistent with `OAUTH2_GITHUB_REDIRECT_URI` and `OAUTH2_GOOGLE_REDIRECT_URI`
4. Configure the front-end login bounce address and binding bounce address
5. After restarting the backend service, use third-party login, binding and unbinding capabilities

## Uninstall instructions

- After uninstalling the plug-in, it is recommended to simultaneously remove the relevant environment variables, plug-in basic configuration and plug-in configuration in `backend/core/conf.py`
- If the front-end login page or personal center has integrated third-party login, binding and other capabilities, please clear the corresponding integration simultaneously.

## Contact information

- Author: `wu-clan`
- Feedback method: Submit an Issue or PR