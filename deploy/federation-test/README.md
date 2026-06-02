# Federation-Test: zwei Instanzen auf Proxmox (pve5.th1.juroct.net)

Zwei getrennte LXCs, je eine Money-Manager-Instanz, TLS via **Let's Encrypt DNS-01**
(Host nicht öffentlich auf 80/443 nötig). Single-Origin: das Frontend proxyt `/api`
und `/.well-known/money-instance` an das Backend – kein separates `api.`-Subdomain nötig.

> Voraussetzung: Die `:latest`-Images enthalten die Federation-Features. Dafür muss
> PR #12 nach `main` gemergt sein (dann baut CI die Images neu). Bei „latest" ggf.
> `docker compose pull` ausführen.

## 0. DNS (für beide Instanzen)

Beim DNS-Provider von `juroct.net` je einen A/AAAA-Record auf die jeweilige LXC-IP:

```
money-a.th1.juroct.net   →  <IP LXC A>
money-b.th1.juroct.net   →  <IP LXC B>
```

DNS-01 braucht **API-Zugang zum DNS-Provider**. Standard hier: Cloudflare-Token
(`Zone:DNS:Edit`). Anderer Provider? In `traefik.dns01.yml` `DNS_PROVIDER` + die
Credential-Variablen anpassen (siehe https://doc.traefik.io/traefik/https/acme/#providers).

## 1. LXC anlegen (pro Instanz, in Proxmox)

- Debian 12 Template, ≥ 1 GB RAM, ≥ 8 GB Disk.
- Features: `nesting=1` (für Docker). Unprivileged geht mit `nesting=1,keyctl=1`.
- Docker installieren:
  ```bash
  curl -fsSL https://get.docker.com | sh
  ```

## 2. Dateien & Netzwerk (pro LXC)

```bash
git clone https://github.com/stefan-ffr/money-manager.git
cd money-manager
docker network create traefik-public

# Traefik-Env
cp deploy/federation-test/.env.example deploy/federation-test/.env
$EDITOR deploy/federation-test/.env        # DOMAIN, ACME_EMAIL, CF_DNS_API_TOKEN, TRAEFIK_AUTH

# App-Env (Root-Compose)
cp .env.example .env
$EDITOR .env
```

In **`.env`** (Root) pro Instanz mindestens setzen:
```env
DOMAIN=money-a.th1.juroct.net          # B-LXC: money-b.th1.juroct.net
POSTGRES_PASSWORD=<stark>
SECRET_KEY=<lang-zufällig>
FEDERATION_ENABLED=true
INSTANCE_DOMAIN=money-a.th1.juroct.net  # = DOMAIN
WEBAUTHN_RP_ID=money-a.th1.juroct.net
WEBAUTHN_ORIGIN=https://money-a.th1.juroct.net
CORS_ORIGINS=https://money-a.th1.juroct.net
```

## 3. Starten (pro LXC)

```bash
# Traefik (DNS-01)
docker compose -f deploy/federation-test/traefik.dns01.yml --env-file deploy/federation-test/.env up -d
# App-Stack
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml pull && docker compose -f docker-compose.prod.yml up -d  # für :latest
```

Prüfen (von irgendwo):
```bash
curl https://money-a.th1.juroct.net/.well-known/money-instance   # muss public_key + api_endpoint liefern
```

## 4. Benutzer anlegen

Auf **jeder** Instanz im Browser `https://money-a…` öffnen → Registrieren (Passkey).
Der Empfänger-User auf B muss einen **Username** haben, den du beim Senden adressierst
(`username@money-b.th1.juroct.net`). Beide Nutzer sollten **Admin** sein, um Peers zu pairen
(erster registrierter User ist i. d. R. Superuser; sonst in der DB `is_superuser=true` setzen).

## 5. Pairing (beide Seiten bewilligen)

UI: *Einstellungen → Federation → Bewilligte Instanzen* → auf A `money-b.th1.juroct.net`
hinzufügen (**Pairen**), auf B `money-a.th1.juroct.net`. Oder per API – siehe
[../../FEDERATION_SETUP.md](../../FEDERATION_SETUP.md).

## 6. Testbuchung

Auf A eine föderierte Rechnung an B senden:
```bash
curl -X POST https://money-a.th1.juroct.net/api/v1/federation/invoice/send \
     -H "Authorization: Bearer <USER_TOKEN_A>" -H "Content-Type: application/json" \
     -d '{"to_user":"<userB>@money-b.th1.juroct.net","amount":"12.50","currency":"CHF","description":"Test","date":"2026-06-02"}'
```
Auf B sollte die Buchung als **bestätigungspflichtig** erscheinen → akzeptieren/ablehnen.

## Troubleshooting

- **Cert kommt nicht** → `docker logs traefik`; DNS-01-Token/Provider prüfen; `acme.json` löschen und neu.
- **`/.well-known` 404** → altes Frontend-Image (vor dem Nginx-Fix) → `docker compose pull` + neu starten.
- **401 Invalid signature / 403 not approved** → Pairing auf beiden Seiten? Keys rotiert? „Key erneuern".
- **Login geht nicht (Passkey)** → `WEBAUTHN_RP_ID/ORIGIN` = exakt die Domain; HTTPS aktiv.
- Weitere Fälle: [../../FEDERATION_SETUP.md](../../FEDERATION_SETUP.md).
