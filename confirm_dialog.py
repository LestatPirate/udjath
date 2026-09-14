"""Countdown confirmation dialog, mirroring macOS's own display-change
confirmation UX: shows the new resolution and auto-reverts if the user
doesn't confirm within the timeout.
"""

from __future__ import annotations

from Cocoa import (
    NSAlert,
    NSAlertFirstButtonReturn,
    NSAlertSecondButtonReturn,
    NSApplication,
    NSMakeRect,
    NSObject,
    NSRunLoop,
    NSRunLoopCommonModes,
    NSTextField,
    NSTimer,
)

DEFAULT_TIMEOUT_SECONDS = 15


class _CountdownController(NSObject):

    def initWithLabel_secondsLeft_(self, label, seconds):
        self = _CountdownController.alloc().init()
        if self is None:
            return None
        self.label = label
        self.seconds_left = seconds
        return self

    def tick_(self, timer):
        self.seconds_left -= 1
        if self.seconds_left <= 0:
            timer.invalidate()
            self.label.setStringValue_("A reverter para a resolução anterior...")
            NSApplication.sharedApplication().stopModalWithCode_(NSAlertSecondButtonReturn)
            return
        self.label.setStringValue_(
            f"Reverte automaticamente para a resolução anterior em {self.seconds_left}s "
            "se não confirmares."
        )


def confirm_resolution(width: int, height: int, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> bool:
    """Shows a countdown confirmation dialog for a just-applied resolution.

    Returns True if the user confirmed "Manter", False if they chose
    "Reverter agora" or the countdown ran out.
    """
    alert = NSAlert.alloc().init()
    alert.setMessageText_(f"Resolução alterada para {width} x {height}")
    alert.setInformativeText_("A imagem está nítida e bem posicionada no ecrã?")
    alert.addButtonWithTitle_("Manter esta resolução")
    alert.addButtonWithTitle_("Reverter agora")

    label = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, 320, 34))
    label.setEditable_(False)
    label.setBezeled_(False)
    label.setDrawsBackground_(False)
    label.setSelectable_(False)
    label.setStringValue_(
        f"Reverte automaticamente para a resolução anterior em {timeout}s se não confirmares."
    )
    alert.setAccessoryView_(label)

    controller = _CountdownController.alloc().initWithLabel_secondsLeft_(label, timeout)
    timer = NSTimer.timerWithTimeInterval_target_selector_userInfo_repeats_(
        1.0, controller, "tick:", None, True
    )
    NSRunLoop.currentRunLoop().addTimer_forMode_(timer, NSRunLoopCommonModes)

    response = alert.runModal()
    timer.invalidate()

    return response == NSAlertFirstButtonReturn
