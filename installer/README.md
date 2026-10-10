# Installer

Aktuelle Version: **1.0.0**

| Ordner | Inhalt |
|---|---|
| `mac/` | `ILIAS-Sync-1.0.0.dmg` (Apple Silicon) mit Prüfsumme |
| `windows/` | `ILIAS-Sync-1.0.0-Setup.exe` (Erstinstallation) und `ILIAS-Sync-1.0.0-windows.zip` (für Updates in der App), je mit Prüfsumme |
| `update/` | `ILIAS-Sync-1.0.2.dmg`: zeigt das Popup bei jeder anderen Server Version (auch älter, zum Zurückrollen), Update Prüfung schon 3 s nach dem Start. Steht in `release.ts` |
| `alt/` | frühere Builds (0.1.0, 0.2.0, 1.0.1), nie veröffentlicht, nicht mehr verwenden |

## Was kommt wohin

* **Bucket `releases` in Lovable Cloud**: genau die Dateien aus `mac/` und `windows/` (ohne `.sha256`), Namen nicht ändern
* **Website `src/lib/release.ts`**: Version, Dateiname, Größe und SHA-256 je Plattform. Erst die Dateien in den Bucket laden, dann `release.ts` ändern und in Lovable auf Publish → Update klicken

## Neue Version

Alte Dateien aus `mac/` und `windows/` nach `alt/` verschieben, neue hineinlegen, diese Datei anpassen.
