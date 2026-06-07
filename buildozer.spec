[app]

# (str) Title of your application
title = Roxy IRL

# (str) Package name
package.name = RoxyIRL

# (str) Package domain (needs at least 2 dots)
package.domain = org.roxy.irl

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (leave empty to include all)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) List of inclusions using glob patterns
source.exclude_dirs = tests, bin

# (list) List of exclusions using glob patterns
source.exclude_exts = spec

# (list) Application requirements
requirements = python3,kivy,kivymd

# (str) Custom source folders for requirements

# (str) Presplash of the application
presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation
orientation = portrait

# (list) List of service to declare
services = None

# (bool) Fullscreen
fullscreen = 1

# (list) Permissions for the Android app
android.permissions = INTERNET

# (int) Android API level to use
android.api = 34

# (int) Minimum API level
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 34

# (str) Android NDK version to use
android.ndk = 25c

# (bool) Enable AndroidX
android.enable_androidx = True

# (str) Android package name for the SDK
android.package_name = org.roxy.irl

# (str) Application versioning
version.regex = ^\s*#:version:\s+(.*)
version.filename = %(source.dir)s/main.py

# (int) Application version number
version.code = 1

# (str) Application version name
version.name = 1.0

# (bool) Enable pause/resume on Android
android.wakelock = False

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 1

# (int) Number of parallel jobs
jobs = 4

# (str) Directory where the build happens
build_dir = ./.buildozer

# (str) Directory where the bin package is created
bin_dir = ./bin

# (str) Android arch to build for
android.archs = arm64-v8a
