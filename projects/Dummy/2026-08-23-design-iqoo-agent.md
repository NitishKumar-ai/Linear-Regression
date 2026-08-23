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
