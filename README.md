# 🪴GreenCanvas

**Sketch your plants, grow them in 3D.** 🌱

Creating **unique and accurate 3D plant models** has always been a challenge in computer graphics. Plant structures are inherently complex, and building them by hand often requires significant effort — which is why most virtual environments reuse the same limited sets of plant assets.

GreenCanvas offers an alternative: a **sketch-based modeling addon for Blender** that transforms simple 2D drawings into fully realized 3D plant models, letting you:

✏️ Sketch branches and leaves directly on a 2D canvas inside Blender.

🌿 Generate structured 3D plant geometry through convex hulls, swept surfaces, and B-spline-based leaf modelling.

✨ Create multiple plant variations from a single sketch, supporting both real species and imagined forms.

By lowering the barrier to plant modelling — no specialized hardware, no external sensors — GreenCanvas empowers creators of **virtual environments, scientific visualizations, and fictional worlds** to design custom vegetation with speed and flexibility.

Backed by a systematic review of plant modelling techniques, the addon emphasizes **usability, creative control, and botanical plausibility**, bridging the gap between intuitive sketching and advanced geometry generation.

## 🎥 Video

_

## 🌱 Usage

1. Open Blender and enable the GreenCanvas addon.
2. Switch to the GreenCanvas workspace and click **Start Drawing**.
3. **Draw** plant structures (branches and leaves) on the 2D canvas.
4. Click **Buid Plant** to convert your sketch into a 3D model.
5. Use the additional provided features, such as adjusting the Level of Detail (LoD), propagate leaves along the branches, and generate variations of the model, and/or edit your model like any other Blender object.

## ⚙️ Installation

From Source
1. Download the .zip of the corresponding operative system.
2. In Blender, go to Edit > Preferences > Add-ons > Install and select the .zip.
3. Enable the addon in the list.

From Jacques Lucke's Blender Development VSCode Extension
1. Uncomment and adapt sections with "Remove when deploy" text in __init__.py file
2. Run Blender Start with the extension


### Wheels (Dependencies)

To download cross-platform wheels for Shapely and SciPy, use the included Makefile. Run the following command from your project root:

    make download-wheels

This will automatically fetch the required .whl files into the ./wheels directory for multiple platforms and Python versions.

## 🌿 Technical Details

### Custom UI Widgets

Due to the lack of custom UI widgets in Blender, the custom UI elements presented in the addon (e.g. draggable panels, buttons and sliders) were adapted from [BL_UI_Widgets](https://github.com/jayanam/bl_ui_widgets).

### Research Background

A systematic review of plant modeling techniques was conducted to inform the design and implementation of GreenCanvas. This ensures the generated models are grounded in both creative workflows and botanical accuracy.

