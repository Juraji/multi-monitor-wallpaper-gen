# ROADMAP

Features planned for multi-monitor-wallpaper-gen.

---

## TUI - Full-Featured Config Editor

A terminal-based UI for managing the application without editing YAML directly.

### Core TUI Features

- [ ] **App Shell**
  - [ ] Main menu with navigation (Screens, Image Sets, Settings, Preview, Generate)
  - [ ] Keyboard navigation (arrows, enter, escape, shortcuts)
  - [ ] Status bar showing current state/actions

- [ ] **Screen Management View**
  - [ ] List all detected/configured screens
  - [ ] Add/Edit/Remove screens manually
  - [ ] Re-detect monitors via xrandr
  - [ ] Edit screen properties (device_id, position, resolution, ICC profile)
  - [ ] Visual ASCII representation of monitor layout

- [ ] **Image Set Management**
  - [ ] List all image sets with thumbnails (ASCII or terminal graphics)
  - [ ] Add/Edit/Delete image sets
  - [ ] Browse and select images for each screen
  - [ ] Drag-and-drop reordering (if possible with keybindings)
  - [ ] Bulk operations (select all, delete multiple)

- [ ] **Settings View**
  - [ ] Edit global settings (background color, fit mode, compression quality)
  - [ ] Default image selection

- [ ] **Preview**
  - [ ] Preview generated wallpaper in terminal (ASCII art / sixel / kitty protocol if available)
  - [ ] Quick preview of individual monitor crops

- [ ] **Actions**
  - [ ] Run generate command from within TUI
  - [ ] Set as wallpaper (if backend supports it)

### Technical Notes

- Use library: `textual` or `npyscreen` or `curses`
- Prefer: `textual` for modern TUI experience
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
