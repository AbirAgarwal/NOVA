GUI_ROOT = None


def minimize_nova():

    global GUI_ROOT

    if GUI_ROOT:
        GUI_ROOT.withdraw()

    return "NOVA minimized."


def restore_nova():

    global GUI_ROOT

    if GUI_ROOT:
        GUI_ROOT.deiconify()
        GUI_ROOT.lift()
        GUI_ROOT.focus_force()

    return "NOVA restored."

def exit_nova():
    
    if GUI_ROOT:
        GUI_ROOT.destroy()
    
    return "Shutting down NOVA."