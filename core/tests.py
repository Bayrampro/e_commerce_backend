import os
from requests_oauthlib import OAuth2Session

redirect_uri = 'https://127.0.0.1:8000/api/v1/get_google_access_token/'
authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
token_url = 'https://accounts.google.com/o/oauth2/token'

# Создание сессии OAuth2
scope = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]
google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)

# Получение URL для авторизации
authorization_url, state = google.authorization_url(authorization_base_url, access_type="offline")

print('Перейдите по этой ссылке для авторизации:', authorization_url)

# Получение кода авторизации
redirect_response = input('Введите полный URL, на который вы были перенаправлены после авторизации: ')

# Обмен кода авторизации на токен
token = google.fetch_token(token_url, client_secret=client_secret, authorization_response=redirect_response)

print('Ваш токен:', token)
