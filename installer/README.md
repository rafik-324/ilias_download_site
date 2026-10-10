# Installer

Aktuelle Version: **1.0.0**

| Ordner | Inhalt |
|---|---|
| `mac/` | `ILIAS-Sync-1.0.0.dmg` (Apple Silicon) mit Prüfsumme. Steht so in `release.ts` |
| `windows/` | später: `ILIAS-Sync-<version>-Setup.exe` (Erstinstallation) und `ILIAS-Sync-<version>-windows.zip` (für Updates in der App) |
| `alt/` | frühere Builds und Test Updates (0.1.0, 0.2.0, 1.0.0-vorab, 1.0.1, 1.0.2), nie veröffentlicht, nicht mehr verwenden |

## Was kommt wohin

* **Bucket `releases` in Lovable Cloud**: genau die Dateien aus `mac/` und `windows/` (ohne `.sha256`), Namen nicht ändern
* **Website `src/lib/release.ts`**: Version, Dateiname, Größe und SHA-256 je Plattform. Erst die Dateien in den Bucket laden, dann `release.ts` ändern und in Lovable auf Publish → Update klicken

## Neue Version

Alte Dateien aus `mac/` und `windows/` nach `alt/` verschieben, neue hineinlegen, diese Datei anpassen.
