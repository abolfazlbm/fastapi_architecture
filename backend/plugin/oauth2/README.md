# OAuth2

OAuth 2.0 social-login plugin supporting platforms such as GitHub and Google

- Supports social login through GitHub and Google
- Supports binding and unbinding social accounts
- Supports login and account-binding redirect configuration

## plugin type

- Application-level plugin

## Configuration instructions

Add the following content to `backend/.env`:

```env
# [ Plugin ] oauth2
OAUTH2_GITHUB_CLIENT_ID='YOUR_GITHUB_CLIENT_ID'
OAUTH2_GITHUB_CLIENT_SECRET='YOUR_GITHUB_CLIENT_SECRET'
OAUTH2_GOOGLE_CLIENT_ID='YOUR_GOOGLE_CLIENT_ID'
OAUTH2_GOOGLE_CLIENT_SECRET='YOUR_GOOGLE_CLIENT_SECRET'
```

The `[settings]` section of `plugin.toml` in the plugin directory contains:

```toml
[settings]
OAUTH2_FRONTEND_BINDING_REDIRECT_URI = 'http://localhost:5173/profile'
OAUTH2_FRONTEND_LOGIN_REDIRECT_URI = 'http://localhost:5173/oauth2/callback'
OAUTH2_GITHUB_REDIRECT_URI = 'http://127.0.0.1:8000/api/v1/oauth2/github/callback'
OAUTH2_GOOGLE_REDIRECT_URI = 'http://127.0.0.1:8000/api/v1/oauth2/google/callback'
OAUTH2_STATE_EXPIRE_SECONDS = 180
OAUTH2_STATE_REDIS_PREFIX = 'example:oauth2:state'
```

The current project's `backend/core/conf.py` already contains these fields:

```python
##################################################
# [ Plugin ] oauth2
##################################################
# .env
OAUTH2_GITHUB_CLIENT_ID: str
OAUTH2_GITHUB_CLIENT_SECRET: str
OAUTH2_GOOGLE_CLIENT_ID: str
OAUTH2_GOOGLE_CLIENT_SECRET: str

# Basic configuration(in plugin.toml)
OAUTH2_STATE_REDIS_PREFIX: str
OAUTH2_STATE_EXPIRE_SECONDS: int
OAUTH2_GITHUB_REDIRECT_URI: str
OAUTH2_GOOGLE_REDIRECT_URI: str
OAUTH2_FRONTEND_LOGIN_REDIRECT_URI: str
OAUTH2_FRONTEND_BINDING_REDIRECT_URI: str
```

## Setting descriptions

- `OAUTH2_FRONTEND_BINDING_REDIRECT_URI`:Controls the frontend redirect after social-account binding
- `OAUTH2_FRONTEND_LOGIN_REDIRECT_URI`:Controls the frontend redirect after social login
- `OAUTH2_GITHUB_REDIRECT_URI`:Controls the GitHub OAuth callback URL
- `OAUTH2_GOOGLE_REDIRECT_URI`:Controls the Google OAuth callback URL
- `OAUTH2_STATE_EXPIRE_SECONDS`:Controls the OAuth state lifetime
- `OAUTH2_STATE_REDIS_PREFIX`:Controls the Redis key prefix for OAuth state

## Usage

1. After installing and enabling the plugin, create OAuth applications in GitHub and Google
2. Set each platform's Client ID and Client Secret in the project environment
3. Ensure platform callback URLs match `OAUTH2_GITHUB_REDIRECT_URI`, `OAUTH2_GOOGLE_REDIRECT_URI`
4. Configure frontend redirects for login and account binding
5. Restart the backend, then use social login, binding, and unbinding

## Uninstall instructions

- After uninstalling the plugin, remove its environment variables, basic settings, and configuration from `backend/core/conf.py`
- If the frontend login or profile page integrates social login or binding, remove the corresponding integration

## Contact information

- author:`wu-clan`
- Feedback: submit an issue or pull request
