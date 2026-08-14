extends CharacterBody3D
## Self-contained first-person walk controller for previewing a Level Factory
## themed building. NO addons, NO project input actions (it polls keys directly),
## so it drops into the walk preview as-is. Includes basic STAIR-STEPPING so you
## can climb the greybox stairs instead of getting stuck on the first riser.
##
## Controls: WASD move, mouse look, Space jump, Shift sprint, Esc toggle mouse.

@export var speed: float = 4.5
@export var sprint_speed: float = 8.0
@export var jump_velocity: float = 5.0
@export var mouse_sensitivity: float = 0.0025
@export var max_step_height: float = 0.5  # auto-climb steps up to this tall

@onready var _camera: Camera3D = $Camera3D


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	# Snap to stairs on the way DOWN so we don't launch off each step edge.
	floor_snap_length = maxf(floor_snap_length, max_step_height)
	floor_max_angle = deg_to_rad(60)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * mouse_sensitivity)
		_camera.rotate_x(-event.relative.y * mouse_sensitivity)
		_camera.rotation.x = clampf(_camera.rotation.x, -1.4, 1.4)
	elif event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		Input.mouse_mode = (
			Input.MOUSE_MODE_VISIBLE
			if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED
			else Input.MOUSE_MODE_CAPTURED
		)


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity += get_gravity() * delta
	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = jump_velocity

	var dir := Vector3.ZERO
	if Input.is_key_pressed(KEY_W):
		dir -= transform.basis.z
	if Input.is_key_pressed(KEY_S):
		dir += transform.basis.z
	if Input.is_key_pressed(KEY_A):
		dir -= transform.basis.x
	if Input.is_key_pressed(KEY_D):
		dir += transform.basis.x
	dir.y = 0.0
	dir = dir.normalized()

	var spd := sprint_speed if Input.is_key_pressed(KEY_SHIFT) else speed
	velocity.x = dir.x * spd
	velocity.z = dir.z * spd

	var grounded := is_on_floor()
	var pos_before := global_position
	move_and_slide()
	# If we were on the ground and a low step stopped us, lift over it — but only
	# by the movement this frame was DENIED, never a fixed jump (a fixed forward
	# hop stacked on the normal move each frame is what made the player rocket
	# ~4x near a stair). A real wall still blocks.
	if grounded and velocity.y <= 0.1:
		_step_up(pos_before, delta)


func _step_up(pos_before: Vector3, delta: float) -> void:
	if not is_on_wall():
		return
	var horiz := Vector3(velocity.x, 0.0, velocity.z)
	if horiz.length() < 0.05:
		return
	# Only complete the blocked REMAINDER of this frame's intended move, so total
	# horizontal displacement stays exactly one frame's worth (no speed boost).
	var wanted := horiz * delta
	var moved := global_position - pos_before
	moved.y = 0.0
	var remaining := wanted - moved
	remaining.y = 0.0
	if remaining.length() < 0.001:
		return  # we weren't actually blocked
	var raised := global_transform
	raised.origin += Vector3.UP * max_step_height
	# Lifted by a step height, is the remaining path clear? If still blocked it's
	# a real wall (or a step too tall) -> don't climb.
	if test_move(raised, remaining):
		return
	raised.origin += remaining
	# Settle down onto the step surface; only snap if there IS ground within
	# reach, so we never teleport out over a ledge.
	var landing := KinematicCollision3D.new()
	if test_move(raised, Vector3.DOWN * (max_step_height + 0.05), landing):
		global_position = raised.origin + landing.get_travel()
