# ROADMAP

Features planned for multi-monitor-wallpaper-gen.

---

## TUI - Full-Featured Config Editor

A terminal-based UI for managing the application without editing YAML directly.

### Core TUI Features

- [ ] Profile/config management.
- [ ] Generating/editing configs.
- [ ] Generate image sets based on selected configuration.

### Technical Notes

- Use library: `textual` for modern TUI experience
- Should work without graphics mode (basic terminal)

---

## Image Processing

### Edge Extension (UV Padding)

Like UV padding in 3D textures - extends image pixels into dead-space around each monitor to hide misalignment artifacts.

- [ ] **Pixel Extension**
  - Repeat the last N pixels of each edge outward into dead-space
  - Dead-space = gaps in virtual canvas where no monitor exists
  - Configurable pixel width (default: 50px)
  - Does NOT overlap with adjacent monitors, only extend into dead space.

---

## Future Ideas (Backlog)

- **Multiple Monitor Profiles**: Save/load different monitor configurations (home vs work)
- **Auto-Set Wallpaper**: Integrate with desktop APIs to set wallpaper(s) directly.
- **Image Preprocessing**: Brightness/contrast/saturation adjustments

---

## Completed

- [x] Automatic screen detection via xrandr
- [x] Manual monitor specification via YAML
- [x] Batch processing
- [x] Cover/Contain fit modes
- [x] Arbitrary monitor arrangements
- [x] Background color filling
- [x] ICC profile baking
- [x] Multi-threaded rendering
