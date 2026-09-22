# HyperFrames delivery

Use HyperFrames as the editable composition layer when the team needs a browser-reviewable video project instead of only a Premiere timeline.

## Composition contract

Represent every kept interval explicitly. HyperFrames timing attributes use seconds. The canonical cut plan uses frames, and the exporter performs the conversion once using the sequence frame rate.

```html
<video
  src="./public/media/body.mp4"
  data-start="0"
  data-duration="90"
  data-media-start="12"
  data-track-index="1"
></video>
<audio
  src="./public/media/body.mp4"
  data-start="0"
  data-duration="90"
  data-media-start="12"
  data-track-index="0"
></audio>
```

Use `data-start`, `data-duration`, and `data-media-start` in seconds. Each source-time edit must create equal composition durations across its layers. Picture and source audio normally use matching offsets; an intentional picture offset is represented by a different source range with the same duration.

For aligned alternate picture, add another `<video>` on a higher `data-track-index` with the same composition timing and the mapped source offset. Do not add its audio unless the edit calls for it.

## Folder layout

Keep source media inside the composition's `public/media/` folder or use a stable project-relative asset path. Store the machine-readable cut plan next to the composition so Premiere and HyperFrames exports are generated from the same decisions.

Export a validated plan with:

```bash
python3 scripts/export_hyperframes.py cut-plan.json path/to/hyperframes-project
```

Each source should provide `hyperframes_src`, pointing to a path the project server can load. The exporter also writes the validated plan beside `index.html` and creates `hyperframes.json`; it does not copy or render media.

## Validation

Run the normal HyperFrames check and snapshot/preview workflow. Review every retake boundary and at least three sync landmarks distributed through the body. A green composition check proves structure, not editorial correctness or lip sync.
