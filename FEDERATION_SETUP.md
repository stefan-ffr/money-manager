# Federation Setup (zwei Instanzen)

Vertrauensmodell: **TLS-gebootstrapptes Pairing + gepinnte RSA-Schlüssel + Allowlist.**
Beim Pairing wird der Public Key der Gegenstelle über deren **HTTPS-Endpunkt (Let's Encrypt)**
geholt und gepinnt. Danach wird jede Rechnung mit RSA signiert und gegen den gepinnten Key
geprüft. Federation passiert **nur mit ausdrücklich bewilligten Instanzen**.

## Voraussetzungen (beide Instanzen, z. B. auf pve5)

- Erreichbar über **HTTPS** mit gültigem Zertifikat (Traefik + Let's Encrypt – siehe `docker-compose.prod.yml`).
- In der `.env` je Instanz:
  ```env
  FEDERATION_ENABLED=true
  INSTANCE_DOMAIN=money-a.example.ch     # exakt die öffentliche Domain dieser Instanz
  ```
- Der private Schlüssel liegt unter `INSTANCE_PRIVATE_KEY_PATH` (Default `/app/secrets/instance_key.pem`)
  und wird beim ersten Start automatisch erzeugt. Volume `./secrets` persistent halten.
- Discovery-Dokument prüfen (gibt Public Key + `api_endpoint` zurück):
  ```bash
  curl https://money-a.example.ch/.well-known/money-instance
  ```

## Pairing (jede Seite bewilligt die andere)

Federation ist bewusst **beidseitig explizit**. Auf **Instanz A** (als Admin) Peer B hinzufügen:

- UI: *Einstellungen → Federation → Bewilligte Instanzen* → Domain `money-b.example.ch` eintragen → **Pairen**.
- oder API:
  ```bash
  curl -X POST https://money-a.example.ch/api/v1/federation/peers \
       -H "Authorization: Bearer <ADMIN_TOKEN>" \
       -H "Content-Type: application/json" \
       -d '{"domain":"money-b.example.ch","name":"Instanz B"}'
  ```
  A holt dabei B's Public Key über HTTPS und pinnt ihn (`approved=true`).

Dasselbe auf **Instanz B** für `money-a.example.ch`.

> Alternativ kann eine Instanz via `POST /api/v1/federation/pair-request` (Header `X-Instance`)
> eine Pairing-Anfrage stellen; sie landet als **„Ausstehend"** und muss vom Admin per
> *Bewilligen* (bzw. `PUT /federation/peers/{id} {"approved":true}`) freigegeben werden.

## Rechnung senden

```bash
curl -X POST https://money-a.example.ch/api/v1/federation/invoice/send \
     -H "Authorization: Bearer <USER_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
           "to_user": "rolf@money-b.example.ch",
           "amount": "42.00", "currency": "CHF",
           "description": "Test", "date": "2026-06-02"
         }'
```

- `from_user` wird serverseitig gesetzt (kein Spoofing).
- Ziel muss ein **bewilligter Peer** sein, sonst 403.
- Empfänger `rolf` muss auf B existieren (Abgleich über **Username** oder E-Mail); die Buchung
  landet als **pending/bestätigungspflichtig** auf Rolfs erstem Konto und wird über
  *Federation → akzeptieren/ablehnen* (`/invoice/{id}/accept|reject`) verarbeitet.

## Sicherheitsmerkmale

- Signatur wird über die **exakten empfangenen Bytes** geprüft (Sender signiert den Roh-Body).
- Eingehende Rechnungen nur von **bewilligten** Peers (Allowlist), Verifikation gegen **gepinnten** Key.
- Bei Key-Rotation einer Gegenstelle: Peer-Eintrag → **„Key erneuern"** (`/peers/{id}/refresh`).

## Troubleshooting

- **403 „not an approved federation peer"** → Peer fehlt/ist nicht bewilligt (beide Seiten prüfen).
- **401 „Invalid signature"** → Keys haben rotiert → „Key erneuern"; oder Uhr/Body verändert (Proxy?).
- **404 „not addressed to this instance"** → `INSTANCE_DOMAIN` ≠ Domain im `to_user`.
- **409 beim Empfang** → Empfänger hat (noch) kein Konto.

## Bekannte offene Punkte (GitHub #11)

- Rückmeldung (accept/reject) an die sendende Instanz.
- Konfigurierbares Zielkonto (aktuell erstes Konto des Empfängers).
- Replay-Schutz (Timestamp/Nonce).
