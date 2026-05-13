# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a single-file Korean daily fortune (오늘의 운세) web app: `index.html`.

No build system, package manager, or framework — open `index.html` directly in a browser to run it.

## Architecture

Everything lives in `index.html`:

- **CSS** (inline `<style>`): Dark space-themed UI with glassmorphism cards, CSS animations (twinkling stars, floating moon, slide-up cards)
- **Fortune data** (`content` object): Four categories — 총운 (overall), 연애운 (love), 재물운 (money), 건강운 (health) — each with 8 messages
- **Seeded PRNG** (`makePRNG` / `strToSeed`): LCG algorithm seeded from today's date string, ensuring the same fortune is shown all day and changes at midnight
- **`draw()` function**: Picks stars (2–5), messages, and lucky items (color, number, direction) deterministically using the daily seed, then renders HTML into `#result`

## Key Behavioral Notes

- Fortune output is **deterministic per calendar day** — the "re-draw" button replays the same seed, so results never change within a day. This is intentional.
- Lucky items come from fixed arrays: `luckyColors` (10), `luckyNums` (23), `luckyDirs` (8)
- Star ratings range 2–5 (never 1 or 5 stars) — see `pickStar()`
