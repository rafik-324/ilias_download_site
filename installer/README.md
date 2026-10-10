# Installer

Aktuelle Version: **1.0.0**

| Ordner | Inhalt |
|---|---|
| `mac/` | `ILIAS-Sync-1.0.0.dmg` (Apple Silicon) mit Prüfsumme |
| `windows/` | `ILIAS-Sync-1.0.0-Setup.exe` (Erstinstallation) und `ILIAS-Sync-1.0.0-windows.zip` (für Updates in der App), je mit Prüfsumme |
| `update/` | Test Update `ILIAS-Sync-1.0.1.dmg`: nur die Versionsnummer ist neu. Zum Testen der Update Funktion: 1.0.0 aus `mac/` installieren, 1.0.1 in den Bucket laden, die App meldet das Update |
| `alt/` | frühere Testbuilds (0.1.0, 0.2.0), nie veröffentlicht, nicht mehr verwenden |

## Was kommt wohin

* **Bucket `releases` in Lovable Cloud**: genau die Dateien aus `mac/` und `windows/` (ohne `.sha256`), Namen nicht ändern
* **Website `src/lib/release.ts`**: Version, Dateiname, Größe und SHA-256 je Plattform. Erst die Dateien in den Bucket laden, dann `release.ts` ändern und in Lovable auf Publish → Update klicken

## Neue Version

Alte Dateien aus `mac/` und `windows/` nach `alt/` verschieben, neue hineinlegen, diese Datei anpassen.
