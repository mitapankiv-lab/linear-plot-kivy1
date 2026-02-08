# (Этот файл создан автоматически для проекта "Графический калькулятор линейных функций")
[app]
# (название приложения)
title = Графический калькулятор линейных функций
# (имя пакета — должно быть латиницей и без пробелов)
package.name = graficheskiy_kalkulyator_lineynykh_funktsiy
package.domain = org.example
# (версия приложения)
version = 1.0.0
# (путь к исходникам; "." — текущая папка проекта)
source.dir = .
# (включаемые расширения)
source.include_exts = py,kv,png,jpg
# (требуемые python-пакеты)
requirements = python3,kivy
# ориентация экрана
orientation = portrait
# логирование (0-2)
log_level = 2

# (Android)
[buildozer]
# директория для сборки (можешь изменить)
build_dir = ./.buildozer

[app]
# минимальные настройки android (если нужно, можно изменить)
android.api = 33
android.minapi = 21
# java версия (OpenJDK)
android.sdk = 24

# Параметры подписи (если хочешь, можешь заполнить позже)
# android.release_keystore = /home/user/.keystore/my-release-key.jks
# android.release_keyalias = myalias
# android.release_keystore_pass = your_keystore_password
# android.release_keyalias_pass = your_key_password

# Опции пакета
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/splash.png

# Доп. опции
# presplash.image = %(source.dir)s/data/presplash.png
# orientation уже задан выше

[buildozer:android]
# можно оставить по умолчанию
# android.ndk = 19b
# android.ndk_path = /path/to/ndk
# android.sdk_path = /path/to/sdk