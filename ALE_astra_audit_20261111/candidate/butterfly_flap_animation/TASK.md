Create a butterfly wing-flap animation in Adobe After Effects.

Remote workspace:
- Task folder: /candidate

Software:
- Launch Adobe After Effects using: /candidate/software/launch_after_effects.bat
- The installed After Effects version may differ from the original submission; use the available AE version opened by this launcher.
- After Effects is the intended tool, but if AE is not available in the environment, any other way to achieve the goal is welcome (the output MP4 is what gets evaluated).

Visible inputs:
- Source butterfly artwork: /candidate/input/butterfly.jpeg
- Detailed task spec: /candidate/input/task_spec.md

What to do:
1. Import the butterfly image into After Effects.
2. Split or mask the butterfly into a central body plus left and right wings.
3. Set wing anchor points near the wing-body joints.
4. Animate the wings with repeated Y-rotation or equivalent perspective deformation.
5. Produce exactly 4 complete wing flap cycles: open -> closed -> open.
6. Move the butterfly along a smooth curved 2.5D-style path through the frame with at least 2 Y-direction turning points.
7. Keep the butterfly texture recognizably tied to the source image at fully open moments.
8. Use a plain dark or black background so the butterfly motion remains clear.

Export requirements:
- Export one H.264 MP4.
- Frame rate: 30 fps.
- Duration: 4.0 to 5.5 seconds.
- Save the final render exactly here: /workspace/submission/output.mp4

Do not modify files under input/. Write only the final MP4 under output/.
