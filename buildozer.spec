[app]

title = Roxy IRL
package.name = RoxyIRL
package.domain = org.roxy.irl
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.exclude_exts = spec
requirements = python3,kivy,kivymd,requests
presplash.filename = %(source.dir)s/data/presplash.png
icon.filename = %(source.dir)s/data/icon.png
orientation = portrait
fullscreen = 1
android.permissions = INTERNET
android.enable_androidx = True
android.package_name = org.roxy.irl
android.accept_sdk_license = True
version = 1.0
version.code = 1

[buildozer]

log_level = 1
jobs = 4
bin_dir = ./bin
android.archs = arm64-v8a
warn_on_root = 0
