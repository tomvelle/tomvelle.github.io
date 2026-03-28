# Sort / Sound / See

Sorting algorithm visualizer with sound synthesis, multi-instrument SoundFont support, and screen-recording-friendly display modes.

## How to use

Open `index.html` in any modern browser. No server, no dependencies, no build step.

## Layout

**Default mode:** Two-zone layout. Left is the visualization canvas. Right is the data panel with live stats, algorithm info, sound engine details, and the SoundFont loader.

**16:9 cinematic mode:** Click the "16:9" button in the header. Hides the data panel entirely and constrains the canvas to 16:9 aspect ratio. Clean recording canvas with nothing but the bars and the legend.

**Horizontal mode:** Click "Horiz" to flip the bars sideways. They stack top-to-bottom and grow left-to-right. Combines with 16:9 mode for a widescreen horizontal sort.

Both modes toggle on/off and can be combined.

## Algorithms (12)

Bubble, Selection, Insertion, Merge, Quick, Heap, Radix, Shell, Cocktail Shaker, Comb, Gnome, Bogo.

Each one has its own visual personality. The data panel shows name, time/space complexity, stability, and a plain-English description of what it's doing.

## Sound engines

### Built-in (no files needed)
- **Sine** -- pure, clean
- **Triangle** -- warm, muted
- **Sawtooth** -- bright, buzzy
- **Square** -- hollow, NES/chiptune
- **FM Synth** -- bell-like, metallic

### SoundFont mode (multi-instrument)

1. Select "SoundFont" from the waveform dropdown
2. Drop a .sf2 file onto the drop zone in the data panel (or click to browse)
3. The parser reads the SF2 RIFF structure and extracts every instrument it can find
4. An instrument selector dropdown appears showing all available instruments by name
5. Switch between instruments live while sorting or between sorts

The SF2 parser walks the full header chain: inst (instrument headers) -> ibag (instrument bags) -> igen (instrument generators, looking for oper 53 = sampleID) -> shdr (sample headers) -> smpl (raw PCM data). Each instrument gets its own AudioBuffer with the correct sample rate and original pitch metadata for accurate playback rate shifting.

If the inst chain is missing or malformed (some older/simpler SF2 files), it falls back to enumerating raw samples from the shdr/smpl chunks directly.

If no SF2 is loaded and the waveform is set to SoundFont, it falls back to FM synthesis.

**Where to get .sf2 files:**
- FluidR3_GM.sf2 (full General MIDI, ~140MB, 100+ instruments)
- TimGM6mb.sf2 (lightweight GM, ~6MB)
- MuseScore_General.sf2 (good quality, ~50MB)
- Individual instrument soundfonts from sites like musical-artifacts.com

## Pitch mapping

**Oscillator modes:** `freq = 120 + (value / N) * 1200` Hz (120Hz to 1320Hz)

**SoundFont mode:** `MIDI note = 36 + (value / N) * 60` (C2 to C7)

**Timing:** Compare = 50ms, Swap = 60ms, Sorted marker = 30ms, Completion sweep = ~500ms total across all bars.

## Recording tips

- 16:9 mode + horizontal gives you the cleanest widescreen footage
- Default vertical mode with the data panel visible gives you that "data visualization" aesthetic
- 150-200 bars is the sweet spot for visual density
- Speed 40-60 looks best on camera
- Click "Reverse" before bubble or insertion sort for worst-case drama
- The green completion sweep with ascending tones is always the payoff shot
- Sawtooth and FM are the most sonically interesting for recordings
- With a GM SoundFont loaded, try piano (instrument 1) or marimba for a clean melodic feel, or switch to something like strings or choir for atmosphere
