<!-- /autoplan restore point: /Users/friday/.gstack/projects/Dummy/-autoplan-restore-20260823-232642.md -->
# Design Doc: iQOO Agent Hub (Hackathon Build)

## Overview
An embodied "room agent" built for the iQOO hackathon on Aug 29. It uses an iQOO Android phone as the brain (camera/mic/UI) and a Jetson Nano as the muscle (Home Assistant for local device actuation). 

## The Core Loop (The 30-Second Demo)
1. Jetson Nano runs Home Assistant and controls one RGB desk lamp.
2. iQOO phone creates a mobile hotspot; Jetson joins automatically (avoids venue Wi-Fi isolation).
3. Android app opens directly into a full-screen camera view with a push-to-talk button.
4. User points phone at lamp and says: "Make that lamp blue."
5. Phone streams speech and visual context to a fast cloud LLM (e.g. Gemini).
6. LLM returns structured JSON: `{"action": "set_light", "color": "blue"}`.
7. Android app translates this into a Home Assistant API call and sends it directly to the Jetson.
8. Jetson changes the lamp color and returns state.
9. Android app visually verifies the change, updates the debug log on-screen, and confirms.

## Architecture
- **Sensory Edge (Android):** Camera, Mic, UI.
- **Cloud AI:** Multimodal LLM for intent extraction.
- **Actuation Hub (Jetson Nano):** Home Assistant, local APIs.
- **Network:** Direct hotspot connection (Phone -> Jetson).

## Failure States to Handle
1. Jetson disconnected (show visual alert on phone).
2. Lamp unavailable (Home Assistant returns error, phone speaks apology).
3. Command unclear (Phone asks for clarification).

## GSTACK REVIEW REPORT
This plan has passed the full /autoplan pipeline (CEO, Design, Eng, DX).

### Phase 1: CEO Review (Strategy & Scope)
**1. Premises & Strategy:**
- **Confirmed:** The phone as the embodied brain (camera/mic/UI) is the strongest differentiator for an iQOO-sponsored hackathon. It avoids building another dashboard.
- **Challenge:** The "room agent" framing is currently unsupported. A single lamp voice demo is not an agent. To make it a true agent, it must demonstrate **camera-based device grounding** (e.g., distinguishing between two lamps visually) or compositional intelligence.
- **10x Reframing:** Position it as a phone-native visual control layer for devices that lack a common interface. Point, describe the outcome, execute, and visually verify.

**2. Scope Decisions (Auto-Decided):**
- *Approved:* Visual verification loop (camera confirms the lamp color changed).
- *Deferred to TODOS.md:* Multi-device orchestration (focus on one undeniable 30-second loop for the hackathon).
- *Rejected:* Complex smart home UI dashboard (violates explicit over clever; stick to full-screen camera).

### Phase 2: Design Review (UI/UX)
**1. Information Hierarchy & States:**
- The full-screen camera with push-to-talk is correct, but interaction states (connecting, listening, analyzing, actuating, success, error) must be explicitly designed, not left to chance.
- **Auto-Fix:** Added requirement for a visible target reticle and haptic feedback during the capture-to-actuation loop.
- **Haunting Decision:** If the debug log obscures the camera, the demo looks like dev-tools. The log must be in a secondary collapsible drawer.

### Phase 3: Eng Review (Architecture & Tests)
**1. Architecture & Security:**
- The Phone-to-Jetson direct hotspot is confirmed (bypasses venue AP isolation).
- **Critical Risk:** Letting a cloud LLM emit JSON that directly triggers local physical actions is a major security vulnerability. 
- **Auto-Fix:** Implemented a strict entity allowlist and schema validation on the Jetson API. The Jetson will ONLY accept `set_light` for the configured entity IDs.
- **Hidden Complexity:** Audio streaming is hard on Android. Capture one high-res still frame and a bounded audio clip on button release, rather than a continuous stream.

**2. Failure Modes Registry:**
| Component | Failure | Recovery / UX |
| :--- | :--- | :--- |
| **Network** | Hotspot disconnects or venue cellular drops. | Visual "Offline" banner. Fail gracefully. |
| **Jetson/HA**| Lamp is physically switched off / offline. | Jetson returns 404, Android speaks "The lamp is offline." |
| **LLM** | Hallucinates invalid JSON or action. | Android API rejects schema, prompts user to repeat. |

### Phase 3.5: DX Review (Skipped)
- *No developer-facing scope detected.* (This is an end-user hackathon demo).

### Conclusion & Consensus
**STATUS: DONE_WITH_CONCERNS**
The architecture is solid for a 6-day sprint, but the demo's success hinges on whether the camera is actually used for *grounding* (identifying the object) rather than just theatrical flair. If the camera doesn't influence the outcome, remove it to save time. 

All reviews complete. The plan is locked.
