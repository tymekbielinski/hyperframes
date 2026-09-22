#!/usr/bin/env node
/**
 * slice.mjs — cut the rendered scene REEL into one MP4 per scene, named with its Premiere
 * timeline timecode, and write deliver/TIMECODES.csv.
 *
 *   node scripts/slice.mjs --reel renders/reel.mp4 [--out deliver] [--fps 30]
 *
 * Scene order/durations come from index.html (data-start / data-duration of each slot) and the
 * timeline placement (tl_in / tl_out) from STORYBOARD.md. Cuts are frame-exact: each clip is
 * re-encoded from the reel with -ss/-frames:v so no keyframe rounding creeps in.
 */
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const args = Object.fromEntries(process.argv.slice(2).map((a, i, arr) => a.startsWith("--") ? [a.slice(2), arr[i + 1]] : []).filter(Boolean));
const reel = resolve(args.reel || "renders/reel.mp4");
const outDir = resolve(args.out || "deliver");
const fps = Number(args.fps || 30);
if (!existsSync(reel)) { console.error("reel not found: " + reel); process.exit(1); }
mkdirSync(outDir, { recursive: true });

const index = readFileSync("index.html", "utf8");
const slots = [...index.matchAll(/data-composition-id="([^"]+)"[^>]*data-composition-src="[^"]+"[^>]*data-start="([\d.]+)"[^>]*data-duration="([\d.]+)"/g)]
  .map((m) => ({ id: m[1], start: Number(m[2]), dur: Number(m[3]) }));

const sb = readFileSync("STORYBOARD.md", "utf8");
const frames = {};
for (const block of sb.split(/^## Frame /m).slice(1)) {
  const src = block.match(/- src: compositions\/frames\/([^\s]+)\.html/);
  const tlIn = block.match(/- tl_in: ([\d.]+)/), tlOut = block.match(/- tl_out: ([\d.]+)/);
  const title = block.split("\n")[0].replace(/^\d+ — /, "").trim();
  if (src) frames[src[1]] = { tlIn: Number(tlIn[1]), tlOut: Number(tlOut[1]), title };
}

const tc = (s) => { const f = Math.round(s * fps); const ff = f % fps, S = Math.floor(f / fps); return `${String(Math.floor(S / 3600)).padStart(2, "0")}:${String(Math.floor(S / 60) % 60).padStart(2, "0")}:${String(S % 60).padStart(2, "0")}:${String(ff).padStart(2, "0")}`; };
const tcFile = (s) => tc(s).replace(/:/g, "-").slice(3);   // MM-SS-FF

const rows = [["scene", "file", "timeline_in_tc", "timeline_out_tc", "timeline_in_s", "timeline_out_s", "in_frame", "out_frame", "duration_s", "frames", "title"]];
for (const s of slots) {
  const f = frames[s.id];
  if (!f) { console.warn("no storyboard block for " + s.id + " — skipped"); continue; }
  const startFrame = Math.round(s.start * fps), nFrames = Math.round(s.dur * fps);
  const num = s.id.slice(0, 2);
  const file = `scene-${num}_${tcFile(f.tlIn)}.mp4`;
  const out = resolve(outDir, file);
  // frame-exact: seek to the exact frame boundary and take exactly nFrames frames
  execFileSync("ffmpeg", ["-nostdin", "-v", "error", "-y", "-ss", (startFrame / fps).toFixed(6), "-i", reel, "-frames:v", String(nFrames),
    "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-r", String(fps), "-movflags", "+faststart", out], { stdio: "inherit" });
  const inFrame = Math.round(f.tlIn * fps), outFrame = inFrame + nFrames;
  rows.push([s.id, file, tc(f.tlIn), tc(outFrame / fps), f.tlIn.toFixed(2), (outFrame / fps).toFixed(2), inFrame, outFrame, s.dur.toFixed(2), nFrames, JSON.stringify(f.title)]);
  console.log(`${file}  ←  reel ${tc(s.start)} +${nFrames}f   →  timeline ${tc(f.tlIn)}`);
}
writeFileSync(resolve(outDir, "TIMECODES.csv"), rows.map((r) => r.join(",")).join("\n") + "\n");
console.log(`\n${rows.length - 1} clips + TIMECODES.csv → ${outDir}`);
