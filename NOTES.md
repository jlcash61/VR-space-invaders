# SPACE INVADERS VR — FLEET LOG

> Project notebook for humans and AI sessions alike. Each chat session starts fresh;
> this file is the shared memory. Update it when design decisions or known issues change.

Last updated: 2026-11-23 (Scene 1 + drone economy + Galaga/challenge stages)

---

## FILES

| File | What it is |
|---|---|
| `index.html` | Landing page, links 2D + VR versions |
| `space_invaders.html` | 2D canvas classic (672x768, arcade scale 3) |
| `space_invaders_vr.html` | Three.js + WebXR "Quest 2 edition" (the flagship) |
| `serve_quest_vr.py` | Local HTTPS server so the Quest browser can load the VR page |
| `NOTES.md` | This file |

---

## HOW TO RUN / TEST

- 2D: open `space_invaders.html` directly in a browser.
- VR: `python serve_quest_vr.py`, open the served URL on the Quest 2 over HTTPS, press ENTER VR.
- Desktop preview of the VR game works on any machine (mouse aim, A/D strafe, click/space fire).
- **`?wave=N` URL param** (both games): jump straight to any wave. `?wave=3` = Galaga, `?wave=4` = challenge stage. Great for testing.
- AI auto-play built in: 2D = "AI Pilot" (B key), VR = "AI Auto-Turret" (B key). Used heavily by the headless test harness.

### Headless test harness (temp folder, not in repo)
`%LOCALAPPDATA%\Temp\opencode\galaga_test\harness.mjs` (+ three.module.js)
- Stubs DOM/canvas/audio, injects a state probe + restart/strafe/force-rescue hooks,
  simulates minutes of AI-piloted play at 60fps, reports observed phases/banners/scores.
- Run: `node harness.mjs 2d3 | 2d4 | vr1 | vr3 | vr4 | all`
- If we change game logic meaningfully, re-run these. All current runs: 0 errors.

---

## CORE DESIGN DECISIONS (agreed)

1. **Stage cycle** (both games): waves repeat `invaders → invaders → GALAGA → CHALLENGE`.
   Implemented as `stageTypeFor(w)`: w%4==3 → galaga, w%4==0 → challenge, else invaders.
2. **Galaga stage**: aliens fly in along Bézier squadrons (row per squadron, alternating
   sides), then the formation *breathes* (no marching), then divers peel off, fire mid-dive,
   exit, and re-enter from the top back to their slot. Flying enemies (entry/dive) are worth
   DOUBLE points. 2D divers collide with the player and kill (Galaga-style); VR divers strafe
   through your airspace lobbing plasma. Roster: Boss (150, pink), Butterfly (80, cyan),
   Bee (50, gold) — new sprites in both engines. In VR these are voxel models.
3. **Challenge stage** (every 4th wave): 5 squadrons of 40 bees fly choreographed loops,
   NO enemy fire, 100 pts each, results banner, PERFECT (40/40) = +1000.
4. **Scene 1 — seated carrier cockpit (VR)**: player is seated in a carrier gunship
   (bucket seat, headrest, tub walls, dashboard + neon trim, armrest consoles under the
   blasters, strapped-in pilot legs: thighs/knees/shins/boots, harness straps, footplate +
   skirt). The whole carrier banks when strafing. Desktop gets virtual gloved hands holding
   turret remotes (idle sway, recoil kick on fire, lean on strafe) — hidden in VR where real
   controllers are the controls. HUD/crosshair unchanged.
5. **Holo status card** (VR, head-locked bottom-right): HULL hearts, per-hand wrist-shield
   charge bars, WING drone count, active power-up timers, achievement count.
6. **Drone economy (VR)**: drones are EARNED, not given.
   - Milestones: clear wave 2 → 1st drone ("First Wingman"); clear a challenge stage → 2nd
     (later challenge clears +200; if at cap, +300 instead).
   - Cap 2 active drones. They orbit the player during play (firing at nearest hostile every
     ~0.7s), return to carrier docks between waves.
   - Drone hull hits do NOT destroy them (they're earned upgrades).
   - Boss tractor beam can STEAL an active drone (see below). Killing the carrier boss
     recovers it. Capture no longer costs a life in VR.
7. **Tractor beam**: boss (row 0) occasionally runs a beam attack instead of a dive — flies
   over the player, projects a cone ~3.6s. Linger ~1s inside → steal. A mini voxel fighter
   rides beside the boss until recovered. Beam runs only trigger when the player owns ≥1 drone.
   2D version: capture costs no life, rescue grants DUAL FIGHTER (two ships, two lasers,
   `player.laser` + `player.laser2`; `updatePlayerLaser(l, dt)` handles both).
8. **Wrist shields (VR)**: Grip = shield. Energy drains while held (~2.5s), recharges while
   released (~4.5s), locks out until 60% after a full drain. Energy bar on each blaster
   (cyan→amber→red). The 4 vertical force-field generators (HP, regen, collapse) unchanged.
9. **Autofire (VR + desktop)**: hold to fire; cooldown grows each consecutive shot until the
   guns stall; release resets. Shield Extender power-up halves shield drain for 30s;
   Full Auto power-up disables the ramp for 30s.
10. **Power-ups (VR)**: drops from kills (~14%), one on field at a time, drift toward the
    player, collected by head or hand. Cyan octahedron = Shield Extender, green = Full Auto.
11. **Persistence**: hi-score (both games) + best-wave (2D, shown on title screen) via
    localStorage. VR wave progress is NOT auto-resumed (use `?wave=`).
12. **Fiction**: the VR player is a person, not a ship — so the tractor beam steals an
    earned drone, never "you". 2D keeps the authentic reserve-ship fiction.

---

## VR CONTROLS (Quest 2)

- Trigger: fire (hold = autofire with ramping cooldown)
- Grip: wrist shield (limited energy)
- Left stick: strafe • Right stick: snap turn
- Desktop: mouse aim (alien-snapping crosshair), click/space fire, A/D strafe, B = AI turret

---

## KNOWN ISSUES / TUNING CANDIDATES  (user: "some things to fix" — list TBD next session)

- Beam-attack frequency, dive aggression, and drone orbit placement are untuned for a
  brand-new VR player — expect feedback here.
- Shots freeze during the GAME_OVER screen (deliberate dramatic pause, same as arcade).
  Wave-clear lets stray shots fly out instead (fixed this session).
- Unused power-ups persist across wave transitions (harmless drift).
- 2D: dual-fighter death shows a single wreck (cosmetic).
- 2D capture costs no life; VR capture used to cost a life — now costs the drone instead.

## PARKED IDEAS (not built)

- **TRANSFORMATIONS (the big one — user's core vision, 2026-11-23):** The game is an
  escalation story. Working title: **"INVADERS FROM SPACE"** (italic, angled font; possible
  tagline "THEY'RE CHANGING."). Enemies visibly evolve across tiers, and the player evolves
  in parallel (turrets → shields → drones → command).
  - Tier ladder (~1 tier per 2 waves): (1) classic marchers → (2) THE TRANSFORMATION MOMENT:
    one invader breaks formation mid-wave and VISIBLY unfolds wings / ignites engines while
    diving; afterwards some spawn pre-evolved as Fighters (dive + bank + fire) → (3) Bombers
    (slow, tanky, heavy shots, flanking) → (4) Interceptors (fast feint dives) → (5) Command
    Ship (large, coordinates pincer dives from both flanks, possibly shielded) → (6+) full
    combined squadrons with complementary patterns.
  - The morph is shown IN GAMEPLAY, never told: VR = hidden wing/engine voxel clusters that
    scale/rotate in over ~1.5s + emissive engine glow while the alien exits formation;
    2D = mid-morph sprite (invader silhouette + sprouting wing/flame pixels) crossfading
    into the Fighter sprite.
  - Rename pass needed: page titles, landing page, both title screens, holo marquee →
    "INVADERS FROM SPACE."
  - Player mirror ladder: two turrets → wrist shields → earned drones (BUILT) → power-ups
    (BUILT) → drone commands (parked, see below).
- Drone commands: spend shield-bar charge to send a drone at your aim point (hand bars as
  drone remotes — user liked this direction).
- More achievements: perfect challenge, drone recoveries, multi-kill dives (card already
  has an ACHV counter to build on).
- Dock-pad visual polish on the carrier (hangar bay feel).
- 2D drone parity (orbiting bomb-blockers) if desired.
- Authentic Galaga model for 2D (beam lifts your active cannon).

---

## ARCHITECTURE NOTES (for future sessions)

- Both files are single self-contained HTML files with one big script. No build step.
- Stage branching: 2D `update()` → `if (galagaWave) updateGalagaStage(dt) else if
  (challengeStage) updateChallengeStage(dt) else {march + UFO}`. VR `updateGame()` mirrors
  this. `ratio` is hoisted above the branch (bomb-spawn code below still uses it).
- Alien states (both engines): `entry → formation → diving/beaming → reentry`, plus
  `challenge` (fly-through, not part of the formation system).
- Galaga math: cubic Bézier (`bezPoint` 2D / `bez3v` VR); formation breathing =
  scale offsets around formation center (`galagaFormationPos`).
- Wave-clear triggers drone milestones (`checkDroneMilestones`) in VR before the banner text
  is composed (milestone banner is appended to challenge results).
- VR capture flow: beam hold → `capturedFlag=true`, `a.hasCaptured=true`, pop one active
  drone, attach mini fighter to boss. Laser-kill of a boss with `hasCaptured` →
  `recoverDrone()` + banner. `a.beamMesh` must be removed on kill AND on hold-expiry AND on
  wave rebuild (cleanup lives in `buildAlienWave`).
- If `wingmanDrone` / old single-drone references appear anywhere: they are GONE — the
  system is `activeDrones[]` + `droneProgress` + `DRONE_CAP` (2).
- Sounds: `playDive`/`diveWhoosh` (divers), `playTractor`/`tractorTick` (beam hold).
- localStorage keys: `space_invaders_hi`, `space_invaders_vr_hi`, `space_invaders_best_wave`.
