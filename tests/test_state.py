from palette_state import MAX_COLORS, Palette


def test_set_and_undo():
    p = Palette()
    p.set(["#111111"])
    p.set(["#222222", "#333333"])
    p.undo()
    assert p.colors == ["#111111"]


def test_add_remove_and_cap():
    p = Palette()
    for i in range(MAX_COLORS + 3):
        p.add(f"#{i:06x}")
    assert len(p.colors) == MAX_COLORS
    p.remove("#000000")
    assert "#000000" not in p.colors


def test_add_ignores_duplicates():
    p = Palette()
    p.add("#abcdef")
    p.add("#abcdef")
    assert p.colors == ["#abcdef"]


def test_choose_calls_back_and_ends_the_session():
    p, got = Palette(), []
    p.pick.start("slot", "Foreground", got.append)
    assert p.pick.active and p.pick.label == "Foreground"
    p.pick.choose("#112233")
    assert got == ["#112233"] and not p.pick.active


def test_cancel_does_not_call_back():
    p, got = Palette(), []
    p.pick.start("slot", "Foreground", got.append)
    p.pick.cancel()
    assert got == [] and not p.pick.active


def test_choose_when_inactive_is_a_no_op():
    Palette().pick.choose("#ffffff")


def test_starting_again_replaces_the_session():
    p, a, b = Palette(), [], []
    p.pick.start("one", "Foreground", a.append)
    p.pick.start("two", "Background", b.append)
    p.pick.choose("#010203")
    assert a == [] and b == ["#010203"] and p.pick.owner is None


def test_listeners_are_notified():
    p, calls = Palette(), []
    p.pick.subscribe(lambda: calls.append(1))
    p.pick.start("slot", "x", lambda c: None)
    p.pick.cancel()
    assert len(calls) == 2