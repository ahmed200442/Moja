# Mawja V25

Native Android release source transfer for Mawja V25 (version 2.5.0, versionCode 25).

The original V25 source archive is stored in `.mawja-source/part01.b64` through `.mawja-source/part09.b64` so GitHub Actions can reconstruct and build it without requiring a local GitHub client.

Source ZIP SHA-256:
`f4c0b830a2e9c3ab7dc73a56e987ce60a9fd7a39477fa5d28c7fda75b036455f`

The release workflow rebuilds the archive, validates its SHA-256, builds the Android Release APK, uploads the build artifact, and publishes GitHub Release `v2.5.0`.
