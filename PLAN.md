# ILIAS Sync Download mit Einmalcodes

Ziel für heute: eine öffentliche Seite unter `https://<projekt>.lovable.app`, auf der Kommilitonen mit einem persönlichen Einmalcode die Mac App (`ILIAS-Sync-0.1.0.dmg`) laden können. 50 Codes, jeder genau einmal einlösbar.

Entschieden (2026-10-09): Variante A, alles bei Lovable (Webseite + Lovable Cloud), kostenlos, keine eigene Domain.

## 1. Was es schon gibt

Website Repo `rafik-324/screenshot-perfect-pix-447`, lokaler Klon `~/dev/ilias_sync-website` (TanStack Start, Lovable verbunden, Ziel Cloudflare Workers).

* `src/components/KeyForm.tsx`: Eingabe im Format `XXXX-XXXX`, Zustände `valid`, `invalid`, `used`, `format`. Die Prüfung ist bisher eine Attrappe (`TODO`)
* `src/routes/download.tsx`: Download Seite mit Karten für macOS und Windows, Links stehen auf `#`
* `src/routes/danke.tsx`, `src/routes/datenschutz.tsx` (Abschnitt "Schlüsselsystem" existiert schon)
* `src/start.ts`: CSRF Schutz für Server Funktionen ist aktiv

Es fehlt nur das Backend dahinter: Codes speichern, Code atomar einlösen, DMG geschützt ausliefern.

## 2. Ablauf für den Nutzer

1. Kommilitone bekommt per WhatsApp/Mail einen Link `https://<projekt>.lovable.app/?code=K7QM-4XRT`
2. Seite öffnet sich, Code ist schon im Feld, Klick auf "Einlösen"
3. Server prüft und markiert den Code als eingelöst, Weiterleitung zu `/download`
4. Klick auf "Für macOS laden" holt einen Download Link, der 10 Minuten gültig ist
5. Wer denselben Code danach eingibt, bekommt "Schlüssel wurde bereits verwendet."

**Kulanz bei Abbruch**: Derselbe Code funktioniert noch 1 Stunde lang erneut, aber nur im selben Browser (zufällige Geräte ID im `localStorage`, beim ersten Einlösen gespeichert). Danach oder in einem anderen Browser ist er verbraucht.

## 3. Technik

### Datenbank (Lovable Cloud = Supabase Postgres)

```sql
create table public.download_codes (
  code_hash   text primary key,          -- SHA-256 des normalisierten Codes, nie der Code selbst
  label       text,                      -- optional, z. B. "Code 07", kein Name
  redeemed_at timestamptz,
  device_id   text
);
alter table public.download_codes enable row level security;
-- keine Policies: Browser (anon Schlüssel) kann die Tabelle weder lesen noch schreiben

-- Einlösen in einem einzigen Schritt, damit zwei gleichzeitige Versuche nicht beide durchgehen
create or replace function public.redeem_code(p_hash text, p_device text)
returns text language plpgsql security definer set search_path = public as $$
declare r public.download_codes;
begin
  update public.download_codes
     set redeemed_at = coalesce(redeemed_at, now()),
         device_id   = coalesce(device_id, p_device)
   where code_hash = p_hash
     and (redeemed_at is null
          or (device_id = p_device and redeemed_at > now() - interval '1 hour'))
  returning * into r;
  if found then return 'ok'; end if;
  if exists (select 1 from public.download_codes where code_hash = p_hash) then return 'used'; end if;
  return 'invalid';
end $$;
revoke all on function public.redeem_code(text, text) from public, anon, authenticated;
grant execute on function public.redeem_code(text, text) to service_role;
```

### Speicher

* Privater Bucket `releases` in Lovable Cloud, darin `ILIAS-Sync-0.1.0.dmg` (44 MB, Grenze im kostenlosen Plan 50 MB pro Datei)
* Kein öffentlicher Zugriff, nur über signierte Links mit 10 Minuten Laufzeit

### Edge Function `redeem-code` (Supabase, Deno)

Läuft in Lovable Cloud, hat den Service Schlüssel automatisch als Umgebungsvariable, der Browser sieht ihn nie.

* Eingabe `{ code, device_id, platform }`
* Code normalisieren (Großbuchstaben, Format prüfen), SHA-256 bilden, `redeem_code` aufrufen
* Bei `ok`: `createSignedUrl("releases", "ILIAS-Sync-0.1.0.dmg", 600)` zurückgeben, Dateiname als Download Name
* Bei `used` / `invalid`: nur den Status zurückgeben, keine weiteren Details
* Windows: bis die `.exe` existiert, Status `not_available`

Gegen Durchprobieren reicht die Länge: 8 Zeichen aus 32 (ohne `0 O 1 I`) sind 40 Bit, also etwa 1 Billion Möglichkeiten. Bei 50 gültigen Codes bräuchte man im Schnitt rund 20 Milliarden Versuche für einen Treffer. Eine Sperre nach Fehlversuchen ist deshalb nicht Teil von heute.

### Webseite (Änderungen im Website Repo)

* `KeyForm.tsx`: Attrappe durch Aufruf der Edge Function ersetzen, `?code=` aus der URL vorbelegen, Geräte ID erzeugen, Ergebnis (Code + Ablaufzeit) in `sessionStorage` für `/download`
* `download.tsx`: Ohne eingelösten Code Hinweis plus Link zur Startseite. Mit Code: Klick auf macOS holt frischen signierten Link (gleiche Funktion, Kulanz Stunde greift) und startet den Download. Windows Karte "kommt bald", deaktiviert
* Texte korrigieren, die nicht stimmen:
  * "Apple Silicon & Intel" -> "Apple Silicon (M1 oder neuer) · ab macOS 12"
  * "Beim ersten Start fragt die App deinen Schlüssel ab": stimmt nicht, die App fragt nur Uni-ID und Passwort
  * Schritt 3 "landen sortiert im Downloads-Ordner": stimmt nicht, im selbst gewählten Uni Ordner
  * Hinweis zum ersten Start ergänzen: Systemeinstellungen -> Datenschutz & Sicherheit -> "Trotzdem öffnen"
* Umami Einwilligung im KeyForm: vorerst entfernen (kein Umami eingerichtet), Datenschutzseite entsprechend anpassen. Gespeichert wird nur Hash, Zeitpunkt und Geräte ID

### Codes erzeugen (lokal, Skript `make_codes.py` in diesem Ordner)

* 50 Codes mit `secrets`, Alphabet ohne `0 O 1 I`, Format `XXXX-XXXX`
* Ausgabe 1: `codes.txt`, nur die Codes, einer pro Zeile. **Bleibt hier lokal, nie ins Repo**
* Ausgabe 2: `insert_codes.sql` mit nur den Hashes, zum Einspielen in die Datenbank
* Mehr Codes später: Skript erneut laufen lassen, hängt neue an

## 4. Reihenfolge heute

| # | Schritt | Wer | Dauer |
|---|---|---|---|
| 1 | Im Lovable Projekt **Lovable Cloud einschalten** | Nutzer | 5 min |
| 2 | Codes erzeugen (`codes.txt`, `insert_codes.sql`) | Claude | 10 min |
| 3 | Tabelle, Funktion und Codes einspielen: SQL im Lovable Chat ausführen lassen ("Führe diese Migration aus") oder im Cloud SQL Editor | Nutzer, SQL von Claude | 10 min |
| 4 | Bucket `releases` (privat) anlegen, DMG hochladen | Nutzer | 5 min |
| 5 | Edge Function, `KeyForm`, `download.tsx`, Texte, Datenschutz anpassen, lokal bauen (`npm run build`), pushen | Claude | 60 bis 90 min |
| 6 | In Lovable prüfen, dass die Edge Function deployt ist (sonst im Lovable Chat deployen lassen), **Publish** | Nutzer | 5 min |
| 7 | Test: Code einlösen, DMG laden, zweiter Versuch "bereits verwendet", anderer Browser, Kulanz Stunde | beide | 15 min |
| 8 | Testcode in der Datenbank zurücksetzen bzw. als verbraucht stehen lassen, echte Links verschicken | Nutzer | |

Gesamt etwa 2 bis 2,5 Stunden.

## 5. Risiken und offene Punkte

* **Lovable Cloud Guthaben**: Kostenloser Plan hat ein kleines monatliches Cloud Guthaben. 50 Downloads à 44 MB = 2,2 GB Traffic. Nach dem ersten Tag im Cloud Bereich nachsehen, wie viel verbraucht ist. Notfalls Download auf Cloudflare R2 umziehen (Variante C), die Seite bleibt gleich
* **Edge Function Deploy**: Ob Lovable Funktionen aus `supabase/functions/` im Repo automatisch deployt, beim ersten Push prüfen. Sonst im Lovable Chat anstoßen
* **Impressum**: Platzhalter (Adresse, E-Mail) sind noch offen. Für eine nur privat verteilte, nicht beworbene Seite vorerst tragbar, vor einer breiteren Veröffentlichung füllen
* **Gatekeeper**: App ist ad hoc signiert, jeder muss einmal "Trotzdem öffnen". Steht auf der Download Seite
* **Weitergabe**: Der Code schützt nur den Download. Wer die DMG hat, kann sie weitergeben. Ohne Uni-ID der Uni Mannheim nützt die App aber nichts
* **Windows**: Karte bleibt deaktiviert, bis die `.exe` gebaut und getestet ist. Dann zweite Datei in `releases`, `platform: "win"` freischalten

## 6. Spätere Version der App

Neue DMG hochladen (`ILIAS-Sync-<version>.dmg`), Dateiname in der Edge Function (oder als Secret `MAC_FILE`) anpassen. Codes bleiben gültig bzw. verbraucht wie gehabt.
