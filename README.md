# 🎯 Laser Defect Placement Tool

An interactive web-based application to place defect stickers (transparent PNGs) on perfect laser die images. Designed for large-scale, automated augmentation of defect datasets while maintaining full visual control.

### 🔹 Snapshot

![Demo](https://raw.githubusercontent.com/Akash-Kadali/Defect-Augmentation-Tool/blob/main/frontend/static/assets/defect_augmentation_tool.png)


---

## 📁 Dataset Structure

```

.
├── Laser\_Perfect\_Colored/
│   ├── Greenish Grey/
│   └── Yellowish Pink/
├── Laser\_Defects\_Colored/
│   ├── Greenish Grey/
│   └── Yellowish Pink/
├── Laser Defects/
│   ├── defect\_1.jpg (original references)
│   └── ...
├── outputs/
│   └── Placed\_Defects/{Color}/DEFECTNAME\_augment\_{1–45}.jpg

````

- Each defect color folder matches its respective perfect background folder.
- Defect stickers are transparent PNGs.
- 45 augmented images are generated for each save.

---

## 🧠 Key Features

✅ **Defect Placement**
- Places **45 identical defect copies** vertically (same X, varying Y)
- All 45 defects transform **synchronously** (scale, rotate, move)
- Control vertical **spacing**, rotation, and size
- Use **keyboard shortcuts** or UI sliders for control

🖱️ **Interactive UI**
- Click to place
- Double-click any defect to **delete**
- Switch to a **new background** while keeping the same defect
- View **sticker preview** and **original reference image**
- Reset, refresh, and download preview at any time

🧮 **Batch Control**
- Control 9 defects at a time using keys `1` to `5`
- Batch movement, scaling, and rotation with:
  - `Arrow Keys`: move
  - `R` / `L`: rotate
  - `+` / `-`: scale
  - `[` / `]`: spacing
  - `0`: reset all defects

💾 **Saving Logic**
- One-click save (`Ctrl+S`) generates **45 JPEGs** for the current placement
- Saves are named: `DEFECTNAME_augment_{1–45}.jpg`
- Each save uses a **new perfect image**
- Once a defect is saved once, it’s marked ✅ and skipped unless manually reselected

📊 **Progress Tracking**
- Progress bar shows number of **unique defects completed**
- Auto-resumes last session (defect, color, image)
- Download placed outputs as a ZIP

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install flask pillow python-dotenv
````

### 2. Set Up Directory

Organize your data into:

* `Laser_Perfect_Colored/{Color}/*.jpg`
* `Laser_Defects_Colored/{Color}/*.png`
* `Laser Defects/*.jpg` or `.png` (originals for display)

Create an `outputs/Placed_Defects` directory.

### 3. Run the App

```bash
python app.py
```

The app will auto-open in your browser.

---

## 🎹 Keyboard Shortcuts

| Action           | Key(s)          |
| ---------------- | --------------- |
| Save 45 defects  | `Ctrl + S`      |
| Download preview | `Ctrl + D`      |
| Move batch       | `← ↑ ↓ →`       |
| Scale batch      | `+ / -`         |
| Rotate batch     | `R / L`         |
| Adjust spacing   | `[ / ]`         |
| Reset defects    | `0`             |
| Delete instance  | `Double-click`  |
| Switch batch     | `1` → `5`       |
| Skip defect      | `⏮ / ⏭` buttons |
| New background   | `♻️` button     |

---

## 📂 Output Structure

Saved images are stored in:

```
outputs/
└── Placed_Defects/
    └── Greenish Grey/
        ├── P12345_augment_1.jpg
        ├── P12345_augment_2.jpg
        └── ...
```

Each `save` generates **45 JPEGs** named after the defect.

---

## 🧩 Tech Stack

* **Frontend:** HTML, CSS, JS (Fabric.js)
* **Backend:** Flask (Python)
* **Session Management:** JSON-based resume system
* **Image Composition:** Pillow, OpenCV (optional)

---

## 📬 Feedback / Support

Built with ❤️ by Sri Akash Kadali. For issues or feature requests, open an issue or ping on Slack.
