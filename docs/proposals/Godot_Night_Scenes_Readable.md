# Making Night Scenes Readable in Godot

## The goal

A night scene should feel dark without making the player work to understand the image. Keep the sky and distant spaces dark, preserve enough soft fill to read important shapes, and use local lights to create contrast and guide attention.

> **Keep the night dark, but don’t crush the image. Use restrained ambient fill for readability and localized lights for mood, contrast, and direction.**

This is the useful idea from the Unreal tutorial: control the appearance of the sky separately from the light that keeps the scene visible. In Godot, the main controls are the `WorldEnvironment` and `DirectionalLight3D`.

## Build the lighting in layers

1. **Night sky:** Choose a dark blue-gray sky. A procedural sky works for a simple setup; `PhysicalSkyMaterial` also supports a night-sky texture.
2. **Moonlight:** Add a `DirectionalLight3D` with low energy and a subtle cool tint. Rotate it to create a direction for shadows and highlights. Treat it as gentle shaping light, not daylight painted blue.
3. **Ambient fill:** In the `WorldEnvironment` Environment resource, use a restrained ambient color or ambient light from the sky. This lifts shadow detail so silhouettes, navigation, and gameplay-critical objects remain readable.
4. **Local sources:** Use windows, streetlights, signs, fires, and player equipment to create distinct pools of light. These should establish contrast and help the player read the space. Emission makes a surface look bright; use actual lights or GI when it also needs to illuminate nearby geometry.
5. **Camera and tone mapping:** Tune exposure after the lighting. Keep exposure consistent unless an intentional adaptation effect is part of the design. A filmic tone mapper can help retain both bright lights and darker detail, but it will not fix a poorly balanced lighting setup.

## Godot setup order

1. Add a `WorldEnvironment` and create an `Environment` resource.
2. Set **Background** to **Sky** and assign a sky material. For stars, use a night-sky texture or a custom sky shader; don’t expect the basic lighting setup to create stars automatically.
3. Set **Ambient Light** to a low-intensity cool neutral. Start with a constant color if you need predictable fill, or use the sky as the source for more natural variation.
4. Add a `DirectionalLight3D`. Set its color and energy modestly, then rotate it until its shadows and highlights help describe the scene.
5. Place local lights at visible, plausible sources. Use their range and energy to light nearby surfaces, not the whole level.
6. Run the game and adjust the environment and lights while looking through the player camera. Editor preview lighting may not match the scene that actually runs.

Godot lets a directional light affect the scene, the sky, or both. That can help when the sky’s appearance and the scene’s illumination need separate control. With a `PhysicalSkyMaterial`, the first `DirectionalLight3D` also drives the sky’s sun direction, color, and energy, so check the result when changing that light.

## Readability check

Review the scene from normal gameplay distance and ask:

- Can I identify the player, nearby threats, and important interactable objects?
- Can I read the main route without making every corner equally bright?
- Are there dark areas that feel intentional, rather than like missing information?
- Do local lights create useful pools and focal points, or do they wash out the night?
- Can I still see detail near bright lamps and signs, or are those areas blown out?
- Does the scene work on the target display, not just in the editor?

If the whole scene feels washed out, reduce ambient fill and strengthen selected local lights. If shadows collapse into featureless black, raise the ambient fill slightly or add a motivated light near the area that needs to read. Avoid fixing every problem by raising camera exposure: that brightens the whole image and can flatten the scene.

## Team rule of thumb

**Use ambient light to preserve basic readability. Use moonlight to shape the scene. Use local lights to direct attention. Keep the sky dark enough to sell the time of day.**

There is no universal energy value for a “good night.” The right balance depends on the scene scale, materials, camera exposure, renderer, and target display. Tune in the running game, one lighting layer at a time.

## Godot documentation

- [Environment and post-processing](https://docs.godotengine.org/en/stable/tutorials/3d/environment_and_post_processing.html)
- [PhysicalSkyMaterial](https://docs.godotengine.org/en/stable/classes/class_physicalskymaterial.html)
- [DirectionalLight3D](https://docs.godotengine.org/en/stable/classes/class_directionallight3d.html)
- [Introduction to global illumination](https://docs.godotengine.org/en/stable/tutorials/3d/global_illumination/introduction_to_global_illumination.html)
