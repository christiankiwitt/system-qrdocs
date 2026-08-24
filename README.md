# QRDOCS

QRDOCS is a self-hosted QR-based asset documentation system.

It is designed for physical objects, boxes, equipment, storage, workshop items, and other assets that benefit from a permanent QR label linking to documentation.

A QR code can resolve to:

- a **rich private page** on the local network, and
- a **minimal public page** when scanned from outside the local network.

The same QR URL can serve both views when split DNS is configured.

QRDOCS is intentionally simple: Markdown source files, static HTML output, opaque public tokens, standard web serving, standard DNS, and standard CUPS printing. There is no required cloud platform, database server, or proprietary printer integration.

## Project status

This README describes the intended **v1.0 deployment model**.

QRDOCS v1.0 is CLI-first. A local/mobile web interface for creating and editing assets is planned for a later major release.

## Features

- Create and edit asset documentation from the command line
- Markdown-based source files
- Static HTML generation
- Separate private and public content
- Stable opaque public QR paths
- Optional public pages on a per-asset basis
- Private image support
- Public image support with explicit publication
- Single-label PDF generation
- Batch A4 label-sheet generation
- CUPS printing
- Configurable default printer
- Search and list commands
- Rebuildable static web output
- Provider-neutral networking architecture
- No database server required

## Requirements

### Core

QRDOCS requires:

- Linux
- Python 3.11 or newer
- Python `venv` support
- Git, when installing directly from GitHub
- permission to create files under `/opt`, `/etc`, `/var/lib`, and `/usr/local/bin` during installation

Debian and Debian-derived distributions are the primary v1.0 deployment target.

For Debian/Ubuntu:

```bash
sudo apt update
sudo apt install git python3 python3-venv
```

Python package dependencies are installed into QRDOCS's own virtual environment by `install.sh`.

### Optional components

Depending on how QRDOCS is used, you may also need:

- **nginx** or another web server for serving generated pages
- **CUPS** for printing labels
- **Avahi/mDNS tools** for discovering network printers
- a public DNS hostname/domain if QR pages must work from outside the LAN
- a TLS certificate for HTTPS
- a reverse tunnel, reverse proxy, VPN, VPS, or other inbound-access mechanism if the server cannot accept connections directly from the Internet
- a local DNS resolver capable of split DNS if the same QR URL should show private content at home and public content outside

None of those services are tied to a specific vendor.

---

# Installation

## 1. Clone QRDOCS

```bash
git clone https://github.com/christiankiwitt/qrdocs.git
cd qrdocs
```

For a production deployment, prefer a tagged release rather than an arbitrary development commit.

## 2. Install

Make the scripts executable if necessary:

```bash
chmod +x install.sh uninstall.sh
```

Then run:

```bash
sudo ./install.sh
```

The installer creates an isolated Python environment under:

```text
/opt/qrdocs/venv
```

and exposes the CLI as:

```text
/usr/local/bin/qrdocs
```

Verify the installation:

```bash
qrdocs --help
```

## 3. Persistent-data permissions

QRDOCS is normally operated as a regular user, not as root.

The persistent data directory must therefore be writable by the account that will run `qrdocs`.

For a single-user installation:

```bash
sudo chown -R "$USER":"$(id -gn)" /var/lib/system-qrdocs
```

Do not casually change ownership of an existing multi-user installation. Choose the appropriate owner/group for your environment.

## Installation layout

The default v1.0 layout is:

| Path | Purpose |
| --- | --- |
| `/opt/qrdocs/venv` | Installed Python application and dependencies |
| `/usr/local/bin/qrdocs` | CLI command |
| `/etc/system-qrdocs/config.toml` | Machine-local configuration |
| `/var/lib/system-qrdocs/` | Persistent asset data |
| `/var/lib/system-qrdocs/images/` | Private asset images |
| `/var/lib/system-qrdocs/public/` | Public asset source files |
| `/var/lib/system-qrdocs/public/images/` | Public asset images |

Application files may be replaced during an update.

Configuration and persistent asset data must not be treated as disposable application files.

---

# Configuration

The default configuration file is:

```text
/etc/system-qrdocs/config.toml
```

A minimal example:

```toml
[public]
base_url = "https://qr.example.com"

[printing]
default_printer = "Office_Printer"
```

## Public base URL

`public.base_url` is the externally meaningful base address used when QRDOCS generates public QR URLs.

Example:

```toml
[public]
base_url = "https://qr.example.com"
```

Do not include a per-asset path here.

QRDOCS adds the asset's opaque public path itself.

If public access is not required yet, the value may remain blank while the local setup is being prepared.

## Default printer

The optional default CUPS queue can be configured as:

```toml
[printing]
default_printer = "Office_Printer"
```

An explicit printer supplied on the command line overrides the configured default.

---

# Basic use

Start with:

```bash
qrdocs --help
```

Each subcommand also has its own help:

```bash
qrdocs new --help
qrdocs edit --help
qrdocs public --help
qrdocs label --help
qrdocs print --help
qrdocs search --help
```

## Create an asset

Run:

```bash
qrdocs new
```

Follow the prompts.

QRDOCS asks whether a public page should be created. Public publication is opt-in.

## Edit an asset

```bash
qrdocs edit
```

## List assets

```bash
qrdocs list
```

## Search

```bash
qrdocs search TERM
```

Loose matching is available when useful:

```bash
qrdocs search --loose TERM
```

## Rebuild generated pages

```bash
qrdocs rebuild
```

The source data under `/var/lib/system-qrdocs/` is canonical.

Generated HTML should be considered rebuildable output.

## Create or update a public page

```bash
qrdocs public ASSET-ID
```

Public source data is deliberately separate from private source data.

Making an asset public does **not** mean that all private fields should be copied into the public page.

Keep the public page minimal.

---

# Images

QRDOCS v1.0 supports:

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`
- `.gif`

## Private image

Copy the image into:

```text
/var/lib/system-qrdocs/images/
```

The recommended filename is the asset ID.

Example:

```text
/var/lib/system-qrdocs/images/DEVICE-01.webp
```

Reference it from the private Markdown source:

```markdown
![Device](images/DEVICE-01.webp)
```

Then rebuild:

```bash
qrdocs rebuild
```

## Public image

Public images are separate and must be copied deliberately into:

```text
/var/lib/system-qrdocs/public/images/
```

Example:

```text
/var/lib/system-qrdocs/public/images/DEVICE-01.webp
```

Then rebuild/update the public asset:

```bash
qrdocs public DEVICE-01
```

This separation is intentional. A private image should not become Internet-accessible merely because a private page contains it.

## Copying images from another computer

`scp` is sufficient for v1.0.

From another machine:

```bash
scp ./DEVICE-01.webp user@server:/var/lib/system-qrdocs/images/
```

For a deliberately public image:

```bash
scp ./DEVICE-01.webp user@server:/var/lib/system-qrdocs/public/images/
```

Then SSH to the QRDOCS server and rebuild the appropriate page.

---

# Labels

Generate a label for one asset:

```bash
qrdocs label ASSET-ID
```

Multiple asset IDs can be supplied for batch label generation:

```bash
qrdocs label ITEM-01 ITEM-02 ITEM-03
```

The v1.0 batch format is intended for ordinary A4 sheet printing.

Generated labels contain:

- QR code
- human-readable asset ID
- short title

The URL itself is intentionally not printed as long text on the label.

Use:

```bash
qrdocs label --help
```

for currently available sizing and output options.

---

# Printing with CUPS

QRDOCS uses the standard CUPS `lp` interface.

It does not contain vendor-specific printer drivers or hardcoded printer addresses.

## Install CUPS

On Debian/Ubuntu:

```bash
sudo apt install cups cups-client
sudo systemctl enable --now cups
```

For network-printer discovery, these are also useful:

```bash
sudo apt install avahi-daemon avahi-utils
sudo systemctl enable --now avahi-daemon
```

## Discover printers

CUPS can show available device backends:

```bash
sudo lpinfo -v
```

mDNS/IPP printers can also be inspected with:

```bash
avahi-browse -rt _ipp._tcp
```

A modern IPP printer will commonly advertise a URI similar to:

```text
ipp://printer-hostname.local/ipp/print
```

The exact URI depends on the printer.

## Add a printer queue

For a modern driverless IPP printer:

```bash
sudo lpadmin \
  -p Office_Printer \
  -E \
  -v ipp://printer-hostname.local/ipp/print \
  -m everywhere
```

Set it as the system default if desired:

```bash
sudo lpadmin -d Office_Printer
```

## Verify CUPS

Show configured printers and the default:

```bash
lpstat -p -d
```

Show more complete CUPS state:

```bash
lpstat -t
```

Before blaming QRDOCS, test the printer directly:

```bash
lp /path/to/test.pdf
```

To select a queue explicitly:

```bash
lp -d Office_Printer /path/to/test.pdf
```

If those commands do not produce a physical print, fix the CUPS/printer setup first.

## Print through QRDOCS

With the configured/default queue:

```bash
qrdocs print /path/to/label.pdf
```

With an explicit queue:

```bash
qrdocs print /path/to/label.pdf --printer Office_Printer
```

---

# Web serving

QRDOCS generates static pages. A normal web server can serve them.

nginx is the reference v1.0 deployment, but it is not mandatory.

The important design rule is that the **private origin and public origin are separate**.

A typical deployment uses:

```text
Private generated pages:
    /var/www/system-qrdocs/private

Public generated pages:
    /var/www/system-qrdocs-public
```

If these paths are used, create them and make them writable by the account that runs QRDOCS:

```bash
sudo install -d -o "$USER" -g www-data -m 0755 \
  /var/www/system-qrdocs/private \
  /var/www/system-qrdocs-public
```

Adapt ownership and permissions for multi-user or service-account deployments.

---

# Networking architecture

This section matters if QR codes must work from more than one network.

There are three progressively more capable deployment models.

## 1. LAN-only

The simplest setup is entirely private.

Example:

```text
Phone/laptop
     |
 Home LAN
     |
 QRDOCS server
     |
 private static pages
```

A local web server serves the generated private pages.

No public domain is required if QR codes are only expected to work on the home network.

The drawback is obvious: a QR code scanned away from home cannot resolve to the server.

## 2. Public minimal pages

If QR codes should work outside the LAN, the public side needs a stable reachable name.

Usually this means:

1. a public domain or hostname,
2. public DNS,
3. HTTPS,
4. a safe route from the Internet to the **public** QRDOCS origin.

Example:

```text
Internet client
      |
 public DNS
      |
 https://qr.example.com
      |
 tunnel / reverse proxy / forwarded HTTPS
      |
 public QRDOCS origin
      |
 minimal public pages only
```

A public QRDOCS deployment should expose only the information intended for strangers.

Do not expose the private document root as a shortcut.

## 3. Same URL, private at home and public outside

QRDOCS can use the same permanent QR URL in both locations.

Example QR:

```text
https://qr.example.com/q/OPAQUE-TOKEN/
```

Outside the home network:

```text
qr.example.com
      |
 public DNS
      |
 public origin
      |
 minimal public page
```

Inside the home network:

```text
qr.example.com
      |
 local split DNS override
      |
 LAN address of QRDOCS server
      |
 private origin
      |
 rich private page
```

This requires **split DNS**.

The local DNS resolver returns the QRDOCS server's private LAN address for the public hostname, while normal public DNS continues to point external clients toward the public endpoint.

The result is one permanent QR label with two context-dependent views.

---

# Public domain and DNS

If outside access is required, use a hostname you control, for example:

```text
qr.example.com
```

Create the necessary public DNS record for the chosen public-access method.

The exact record depends on the architecture:

- an `A`/`AAAA` record for a directly reachable server,
- a record pointing to a reverse proxy/VPS,
- or a provider-specific record for an outbound tunnel.

QRDOCS itself does not care which DNS provider is used.

## Split DNS

For same-URL private/public behavior, configure the LAN DNS resolver so:

```text
qr.example.com -> LAN_IP_OF_QRDOCS_SERVER
```

Only LAN clients should receive this override.

External DNS must continue resolving the hostname to the public access path.

After configuring split DNS, test from both sides.

On the LAN:

```bash
getent hosts qr.example.com
```

or:

```bash
dig qr.example.com
```

The answer should be the private LAN address.

On a phone using cellular data rather than Wi-Fi, the same hostname should resolve through public DNS.

Do not rely on per-device `/etc/hosts` modifications for the final deployment. They are acceptable for temporary testing but defeat the purpose of centralized split DNS.

---

# HTTPS and certificates

Use HTTPS for public QR URLs.

If the same hostname is also used on the LAN through split DNS, the local/private HTTPS server must present a certificate valid for that same hostname.

Example:

```text
https://qr.example.com
```

The browser should see a valid certificate whether the request arrived through public DNS or split DNS.

## Certificate issuance

Common ACME validation methods include:

- HTTP validation
- DNS validation

DNS-based validation is especially useful when:

- the server is behind CGNAT,
- inbound port 80/443 cannot be forwarded,
- or the local/private server must obtain a certificate for a public hostname without being directly reachable from the Internet.

Keep DNS API credentials, ACME credentials, tunnel credentials, and private keys outside the Git repository.

Credential files should normally be root-readable only, for example:

```bash
sudo chmod 600 /path/to/credential-file
```

Certificate renewal should be automated and the web server must reload the renewed certificate.

---

# CGNAT and inbound connectivity

Before designing public access around ordinary router port forwarding, check whether the Internet connection has a publicly routable address.

Many residential and mobile connections use **carrier-grade NAT (CGNAT)**.

With CGNAT, the router's WAN address is not directly reachable from the public Internet, so ordinary inbound port forwarding may not work at all.

Possible solutions include:

- an outbound HTTPS tunnel
- a reverse tunnel
- a VPS-based reverse proxy
- a VPN/overlay network where appropriate
- obtaining a public address from the ISP

For QRDOCS public pages, an outbound tunnel is often convenient because the home server initiates the connection and no inbound NAT rule is required.

Keep the tunnel pointed at the **public QRDOCS origin**, not the private document root.

---

# Recommended nginx separation

The exact nginx configuration depends on the host, certificate paths, and network design.

The following pattern shows the important separation.

## Private LAN HTTP origin

A direct LAN-only site may look like:

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    root /var/www/system-qrdocs/private;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Using `default_server` avoids an unrelated named virtual host accidentally catching direct requests to the server's LAN IP.

## Public origin bound only to localhost

If an outbound tunnel runs on the same machine, the public origin can be bound only to loopback:

```nginx
server {
    listen 127.0.0.1:8081;

    server_name _;

    root /var/www/system-qrdocs-public;
    index index.html;

    location /q/ {
        try_files $uri $uri/ =404;
    }

    location / {
        return 404;
    }
}
```

A tunnel or reverse proxy can then target:

```text
http://127.0.0.1:8081
```

Binding the public origin to loopback prevents it from becoming an unnecessary additional LAN-facing service.

The `location / { return 404; }` rule is deliberate: the public QR origin should not become a browsable private documentation site.

## Private HTTPS for split DNS

For same-URL behavior on the LAN:

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name qr.example.com;

    ssl_certificate     /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    root /var/www/system-qrdocs/private;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

The LAN DNS resolver then maps `qr.example.com` to this server's private address.

Validate nginx before reloading:

```bash
sudo nginx -t
```

Then:

```bash
sudo systemctl reload nginx
```

---

# Public/private content model

The public/private split is a security boundary, not just a styling choice.

Private source:

```text
/var/lib/system-qrdocs/
```

Public source:

```text
/var/lib/system-qrdocs/public/
```

Private images:

```text
/var/lib/system-qrdocs/images/
```

Public images:

```text
/var/lib/system-qrdocs/public/images/
```

Do not automatically mirror the private tree into the public tree.

A public page should contain only the minimum information that is useful if a labeled object is found or accessed outside the trusted network.

Typical public information might include:

- asset ID
- short description
- owner surname or organization
- contact address intended for recovery
- limited status information

Avoid publishing:

- private notes
- home/internal location details
- credentials
- network information
- serial information that does not need to be public
- anything copied into the page merely because it exists privately

---

# Opaque QR tokens are not passwords

Public QR paths use opaque tokens.

Example:

```text
/q/long-random-token/
```

This prevents easy guessing and avoids exposing sequential asset IDs in public URLs.

However, an opaque URL is **not authentication**.

Anyone who obtains the URL can access the public page.

Therefore:

- never place secrets on a public page,
- do not treat possession of a QR token as proof of identity,
- and do not use the public side for confidential documentation.

---

# Backups

The critical persistent state is under:

```text
/var/lib/system-qrdocs/
```

Back up the entire directory.

This includes the public-token mapping used to keep already-printed QR labels stable.

Losing the token mapping and recreating public pages with different tokens can invalidate physical labels that have already been attached to assets.

Also back up:

```text
/etc/system-qrdocs/config.toml
```

Generated web output can normally be recreated with:

```bash
qrdocs rebuild
```

so the source data and token mapping are more important than generated HTML.

A simple local backup example:

```bash
sudo tar -czf qrdocs-backup.tar.gz \
  /etc/system-qrdocs \
  /var/lib/system-qrdocs
```

Store backups somewhere other than the QRDOCS server itself.

---

# Updating

From the cloned repository:

```bash
git pull --ff-only
sudo ./install.sh
```

The installer updates the application environment while preserving an existing:

```text
/etc/system-qrdocs/config.toml
```

and:

```text
/var/lib/system-qrdocs/
```

Back up persistent data before significant upgrades.

For controlled production systems, update between tagged releases rather than tracking the development branch continuously.

After an update:

```bash
qrdocs --help
qrdocs rebuild
```

Then verify at least one known private and public QR URL.

---

# Uninstalling

From the repository:

```bash
sudo ./uninstall.sh
```

The uninstaller removes:

```text
/opt/qrdocs
/usr/local/bin/qrdocs
```

It deliberately preserves:

```text
/etc/system-qrdocs
/var/lib/system-qrdocs
```

This prevents uninstalling the application from silently deleting the asset database and stable QR mappings.

If the configuration and data are genuinely no longer needed, remove them manually only after taking any required backup:

```bash
sudo rm -rf /etc/system-qrdocs
sudo rm -rf /var/lib/system-qrdocs
```

---

# Troubleshooting

## `qrdocs: command not found`

Check:

```bash
ls -l /usr/local/bin/qrdocs
```

and:

```bash
ls -l /opt/qrdocs/venv/bin/qrdocs
```

Re-run:

```bash
sudo ./install.sh
```

if the installation is incomplete.

## Permission denied under `/var/lib/system-qrdocs`

Check ownership:

```bash
ls -ld /var/lib/system-qrdocs
```

For a single-user installation, make the operating account the owner:

```bash
sudo chown -R "$USER":"$(id -gn)" /var/lib/system-qrdocs
```

Do not blindly do this on a multi-user deployment.

## nginx returns the wrong site

List enabled virtual hosts and inspect the effective configuration:

```bash
sudo nginx -T
```

Check for:

- another `default_server`
- a named virtual host catching the request
- wrong `server_name`
- wrong document root
- tunnel traffic arriving on a different port than expected

Always validate before reloading:

```bash
sudo nginx -t
```

## Public URL works, but LAN still shows public content

Split DNS is probably not active.

On a LAN client:

```bash
getent hosts qr.example.com
```

The hostname should resolve to the QRDOCS server's private LAN address.

If it resolves to the public endpoint, fix the LAN DNS override.

## LAN URL works by IP but not by hostname

Check:

1. local DNS resolution,
2. nginx `server_name`,
3. TLS certificate validity,
4. firewall rules,
5. whether the client is actually using the intended DNS resolver.

## HTTPS certificate warning only on LAN

The private HTTPS virtual host must present a valid certificate for the public QR hostname.

A certificate for the server's local hostname or raw IP address is not equivalent.

## Public access fails behind a home router

Check whether the connection is behind CGNAT before spending time on port-forwarding rules.

Compare the router's WAN address with the address seen externally.

If the router does not have a publicly routable address, use an outbound/reverse access method or obtain a public address from the ISP.

## Tunnel works but exposes too much

The tunnel should target the public origin only.

A safe local pattern is:

```text
Tunnel -> 127.0.0.1:8081 -> public document root
```

Do not point the tunnel at the private nginx site.

## Printer appears in CUPS but nothing prints

Test outside QRDOCS:

```bash
lpstat -t
lp -d PRINTER_NAME /path/to/test.pdf
```

If direct `lp` printing fails, troubleshoot:

- printer URI
- IPP support
- queue state
- network reachability
- printer-side errors
- driverless support

QRDOCS cannot compensate for a non-working CUPS queue.

## A QR code opens a 404 outside the LAN

If the asset is private-only, this can be expected.

A normal public QR URL requires a corresponding public page if it must resolve on the Internet.

With split DNS configured, the same URL can still resolve to the private page while on the LAN.

---

# Known v1.0 limitations

- QRDOCS v1.0 is CLI-first.
- Image upload is manual.
- Public/private same-URL behavior depends on external split-DNS configuration.
- A private-only asset can return a public 404 when scanned outside the LAN.
- Public access requires external DNS/network infrastructure; QRDOCS does not automatically provision a domain, certificates, tunnels, or firewall rules.
- Printer support depends on a working CUPS queue.
- Batch labels are designed around ordinary A4 printing; specialized roll-label printers may require additional testing.
- Templates are intentionally minimal in v1.0.
- Search is simple text matching rather than a database-backed search engine.
- Opaque public URLs reduce guessability but are not authentication.

---

# Security notes

- Do not commit secrets to the repository.
- Do not place tunnel credentials in QRDOCS configuration unless a future integration explicitly requires them.
- Do not commit DNS API tokens.
- Do not commit TLS private keys.
- Keep credential files readable only by the account/service that requires them.
- Keep the public origin separate from the private document root.
- Prefer binding a tunnel-only public origin to `127.0.0.1`.
- Treat public QR tokens as shareable URLs, not passwords.
- Review public asset content before publishing it.
- Keep the operating system, web server, tunnel software, and TLS tooling updated.

---

# Recovery checklist

If QRDOCS is being restored onto a replacement machine:

1. Install Linux and required packages.
2. Clone the QRDOCS repository.
3. Run `sudo ./install.sh`.
4. Restore `/etc/system-qrdocs/`.
5. Restore **all of** `/var/lib/system-qrdocs/`, including the public-token mapping.
6. Restore or recreate web-server configuration.
7. Restore or reissue TLS certificates.
8. Restore DNS/tunnel configuration.
9. Restore CUPS queues if printing is required.
10. Run `qrdocs rebuild`.
11. Verify a known private URL.
12. Verify a known public URL from outside the LAN.
13. Verify the same URL from inside the LAN if split DNS is used.
14. Generate and print a test label.
15. Scan the physical label before declaring recovery complete.

Do not regenerate stable public tokens casually during recovery. Existing physical labels depend on them.

---

# Architecture summary

A full deployment can look like this:

```text
                         INTERNET
                            |
                     public DNS
                            |
                 https://qr.example.com
                            |
              tunnel / reverse proxy
                            |
                     127.0.0.1:8081
                            |
                    PUBLIC nginx
                            |
              minimal public HTML
                            |
                  /q/opaque-token/


HOME / TRUSTED LAN
        |
   local DNS
        |
 split-DNS override
 qr.example.com -> LAN IP
        |
  https://qr.example.com
        |
    PRIVATE nginx
        |
   rich private HTML


QRDOCS CLI
    |
    +-- private Markdown/images
    |      /var/lib/system-qrdocs/
    |
    +-- public Markdown/images
    |      /var/lib/system-qrdocs/public/
    |
    +-- generated static web pages
    |
    +-- label PDFs
    |
    +-- CUPS -> printer
```

The exact DNS provider, certificate authority, tunnel provider, router, and printer vendor are deployment choices rather than QRDOCS dependencies.

---

# License

QRDOCS is released under the MIT License.

See [`LICENSE`](LICENSE).
