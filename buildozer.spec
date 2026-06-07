[app]

# (str) Title of your application
title = Roxy IRL

# (str) Package name
package.name = RoxyIRL

# (str) Package domain (needs at least 2 dots)
package.domain = org.roxy.irl

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Source files to exclude
source.exclude_exts = spec

# (list) Application requirements - use kivy[base] as base
requirements = python3,kivy,kivymd

# (str) Presplash
presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon
icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET

# (bool) Enable AndroidX
android.enable_androidx = True

# (str) Package name
android.package_name = org.roxy.irl

# (int) Application version number
version.code = 1

# (str) Application version name
version.name = 1.0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 1

# (int) Number of parallel jobs
jobs = 4

# (str) Directory where the bin package is created
bin_dir = ./bin

# (str) Android arch to build for
android.archs = arm64-v8a
