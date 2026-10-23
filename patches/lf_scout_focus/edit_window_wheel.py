import sys, pathlib
O = '''	elif event.is_action_pressed("ui_down"):
		# down through the building: the whole of it, then the top floor, then each one below
		focus(n - 1 if _focus < 0 else maxi(_focus - 1, 0))
	elif event.is_action_pressed("ui_up"):
		# up through it, and past the top floor the whole building again
		focus(-1 if (_focus < 0 or _focus >= n - 1) else _focus + 1)'''
N = '''	elif event.is_action_pressed("ui_down") or _wheel(event, MOUSE_BUTTON_WHEEL_DOWN):
		# down through the building: the whole of it, then the top floor, then each one below -- the arrow or the wheel
		focus(n - 1 if _focus < 0 else maxi(_focus - 1, 0))
	elif event.is_action_pressed("ui_up") or _wheel(event, MOUSE_BUTTON_WHEEL_UP):
		# up through it, and past the top floor the whole building again
		focus(-1 if (_focus < 0 or _focus >= n - 1) else _focus + 1)'''
O2 = '''func _unhandled_input(event: InputEvent) -> void:'''
N2 = '''func _wheel(event: InputEvent, button: MouseButton) -> bool:
	"""One notch of the scroll wheel, the walker's: "scroll wheel should be the up down as well (floors)"."""
	var b: InputEventMouseButton = event as InputEventMouseButton
	return b != null and b.pressed and b.button_index == button


func _unhandled_input(event: InputEvent) -> void:'''
O3 = "it, a flick keeps it turning; left alone"
N3 = "it, a flick keeps it turning, the scroll wheel steps the floors as up/down do; left alone"
for p in sys.argv[1:]:
    p = pathlib.Path(p)
    t = p.read_text(encoding="utf-8")
    if p.suffix == ".gd":
        assert t.count(O) == 1 and t.count(O2) == 1
        t = t.replace(O, N).replace(O2, N2)
    else:
        assert t.count(O3) == 1
        t = t.replace(O3, N3)
    p.write_text(t, encoding="utf-8", newline="\n")
    print("ok", p.name)
