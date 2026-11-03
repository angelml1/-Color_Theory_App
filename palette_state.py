# where the current palette colors are kept
# history tracked for undo functionality
from dataclasses import dataclass, field

MAX_COLORS = 12


class PickMode:
    """Shared 'eyedropper is active' state. A page starts a session, and the
    palette sidebar switches from 'click to remove' to 'click to choose'."""

    def __init__(self):
        self.owner = None
        self.label = ""
        self._callback = None
        self._listeners = []

    @property
    def active(self) -> bool:
        return self._callback is not None

    def subscribe(self, fn):
        self._listeners.append(fn)

    def _notify(self):
        for fn in list(self._listeners):
            fn()

    def _clear(self):
        self.owner, self.label, self._callback = None, "", None

    def start(self, owner, label: str, callback):
        """Begin picking. Replaces any session that was already active."""
        self.owner, self.label, self._callback = owner, label, callback
        self._notify()

    def cancel(self):
        if self.active:
            self._clear()
            self._notify()

    def choose(self, hex_color: str):
        callback = self._callback
        if callback is None:
            return
        self._clear()
        self._notify()
        callback(hex_color)


@dataclass
class Palette:
    colors: list[str] = field(default_factory=list)
    history: list[list[str]] = field(default_factory=list)
    pick: PickMode = field(default_factory=PickMode, repr=False, compare=False)
    _listeners: list = field(default_factory=list, repr=False)

    def subscribe(self, fn):
        self._listeners.append(fn)

    def _notify(self):
        for fn in self._listeners:
            fn()

    def set(self, colors):
        self.history = (self.history + [list(self.colors)])[-20:]
        self.colors = list(colors)[:MAX_COLORS]
        self._notify()

    def add(self, hex_color: str):
        if hex_color not in self.colors and len(self.colors) < MAX_COLORS:
            self.set(self.colors + [hex_color])

    def remove(self, hex_color: str):
        if hex_color in self.colors:
            self.set([c for c in self.colors if c != hex_color])

    def undo(self):
        if self.history:
            self.colors = self.history.pop()
            self._notify()