"""La règle de banc_pnj.ceder, avec les types HANDLE explicites sur Windows 64 bits."""
import os


def ceder():
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        noyau = ctypes.windll.kernel32
        # Sans ces signatures, ctypes tronque le pseudo-handle -1 sur ce poste
        # 64 bits : SetPriorityClass échoue avec ERROR_INVALID_HANDLE (6).
        noyau.GetCurrentProcess.restype = wintypes.HANDLE
        noyau.SetPriorityClass.argtypes = (wintypes.HANDLE, wintypes.DWORD)
        noyau.SetPriorityClass.restype = wintypes.BOOL
    from donjon.banc_pnj import ceder as ceder_banc
    ceder_banc()
