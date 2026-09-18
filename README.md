# Monster Siege

An offline-first location-based monster invasion game where the monsters come to you.

## Core concept

Instead of requiring the player to travel around the real world to find encounters, Monster Siege uses the player's location as a home/base. Monsters spawn around the base, close in over time, and increase a local threat meter. When the threat reaches a threshold, a raid boss appears.

## Initial gameplay loop

1. Establish the player's current location as the base.
2. Generate nearby monster encounters.
3. Monsters approach the base over time.
4. Defeating monsters changes the local threat state.
5. Reaching a threat threshold triggers a raid boss.
6. Defeat the raid boss and receive rewards.
7. Start the next invasion cycle.

## Project direction

The first milestone is a playable prototype. Core simulation should be designed offline-first, with networking treated as an optional enhancement rather than a requirement for the main gameplay loop.

## Planned systems

- Player/base location
- Nearby monster spawning
- Monster movement toward the base
- Threat meter and escalation
- Raid boss spawning
- Combat
- Rewards and progression
- Local persistence
- Optional online synchronization later

## Development principle

**The monsters come to the player.**

The project should remain playable without a continuous internet connection.
