# Validation Report

## Core MKHSS Speedups
- OK: Generate CRS: computed 8.84x, reported 8.80x
- OK: Generate key pair: computed 14.93x, reported 15.00x
- OK: Encode input share: computed 3.96x, reported 4.00x
- OK: Init RMS Alice: computed 21.91x, reported 22.00x
- OK: Init RMS Bob: computed 16.23x, reported 16.00x
- OK: Sync sender share: computed 4.00x, reported 4.00x
- OK: Sync received share: computed 34.33x, reported 35.00x
- OK: Multiply memory and input: computed 44.92x, reported 45.00x
- OK: Convert input to memory: computed 39.95x, reported 40.00x

## Fuzzy PAKE Speedups
- OK: Setup: computed 8.88x, reported 8.90x
- OK: AttrKeyGen: computed 3.27x, reported 3.30x
- OK: AttrKeyDer: computed 34.29x, reported 34.00x
- OK: Complete exchange: computed 33.33x, reported 33.00x

## Geolocation Implied Baselines
- OK: Setup: implied baseline 258.72 ms
- OK: AttrKeyGen A: implied baseline 256.00 ms
- OK: AttrKeyGen B: implied baseline 358.02 ms
- OK: AttrKeyDer A: implied baseline 53040.00 ms
- OK: AttrKeyDer B: implied baseline 49980.00 ms
- OK: Complete exchange: implied baseline 54450.00 ms

## Communication Baselines
- OK: Geolocation: 301.1 kB -> 903.3 kB baseline
- OK: Fuzzy PAKE: 556.1 kB -> 1668.3 kB baseline

## Network-Budget Transfer Times
- OK: Geolocation over 10 Mbps: computed 0.24088 s, reported 0.24088 s
- OK: Geolocation over 2 Mbps: computed 1.20440 s, reported 1.20440 s
- OK: Geolocation over 125 kbps: computed 19.27040 s, reported 19.27040 s
- OK: Fuzzy PAKE over 10 Mbps: computed 0.44488 s, reported 0.44488 s
- OK: Fuzzy PAKE over 2 Mbps: computed 2.22440 s, reported 2.22440 s
- OK: Fuzzy PAKE over 125 kbps: computed 35.59040 s, reported 35.59040 s

## SwarmGate State Machine
- OK: required lifecycle states are present

