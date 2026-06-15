import os


COMMON_APPS = {
    "spotify": "spotify",
    "discord": "discord",
    "steam": "steam",
    "telegram": "telegram",
    "whatsapp": "whatsapp",
    "obs": "obs64",
    "paint": "mspaint",
    "cmd": "cmd",
    "task manager": "taskmgr"
}


def open_app(app_name):

    app_name = app_name.lower().strip()

    if app_name in COMMON_APPS:

        try:

            os.system(
                f"start {COMMON_APPS[app_name]}"
            )

            return f"Opening {app_name}"

        except:

            return f"Could not open {app_name}"

    return "Application not found."