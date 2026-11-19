#!/bin/sh
# Builds release files into release/:
#   smartnav-x86_64            standalone binary (no Python/Tk needed), built on Debian 12
#                              so it also runs on ETAP 23 / Pardus 23 (older glibc)
#   smartnav_<version>_all.deb Pardus/Debian package (uses the system's python3-tk)
#   smartnav-pardus.tar.gz     binary + kur.sh, for USB / no-internet installs
# Needs podman (or docker) and dpkg-deb.
set -eu
cd "$(dirname "$0")/.."

VERSION=$(python3 -c 'import smartnav; print(smartnav.__version__)')
OUT=release
P=packaging/pardus
ENGINE=$(command -v podman || command -v docker)

python3 -m unittest -q
rm -rf "$OUT" && mkdir -p "$OUT"

# --- standalone binary, built in Debian 12 for the oldest glibc we target ---
"$ENGINE" run --rm -v "$PWD:/src:Z" -w /tmp debian:bookworm sh -ec '
    apt-get update -qq && apt-get install -y -qq python3 python3-tk python3-pip binutils >/dev/null
    pip3 install -q --break-system-packages pyinstaller==6.11.1
    cp /src/smartnav.py .
    pyinstaller --log-level WARN --onefile --noconsole --name smartnav smartnav.py
    install -m 755 dist/smartnav /src/release/smartnav-x86_64
'

# --- .deb ---
ROOT=$(mktemp -d)
trap 'rm -rf "$ROOT"' EXIT
install -d "$ROOT/DEBIAN" "$ROOT/usr/bin" "$ROOT/usr/share/smartnav" "$ROOT/usr/share/applications" \
    "$ROOT/usr/share/icons/hicolor/scalable/apps" "$ROOT/usr/share/doc/smartnav"
install -m 644 smartnav.py "$ROOT/usr/share/smartnav/"
printf '#!/bin/sh\nexec python3 /usr/share/smartnav/smartnav.py "$@"\n' > "$ROOT/usr/bin/smartnav"
chmod 755 "$ROOT/usr/bin/smartnav"
install -m 644 "$P/smartnav.svg" "$ROOT/usr/share/icons/hicolor/scalable/apps/"
sed -e 's|@EXEC@|smartnav|' -e 's|@ICON@|smartnav|' "$P/smartnav.desktop" > "$ROOT/usr/share/applications/smartnav.desktop"
chmod 644 "$ROOT/usr/share/applications/smartnav.desktop"
printf 'Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/\nUpstream-Name: smartnav\nSource: https://github.com/bugracdnc/smartnav\n' \
    > "$ROOT/usr/share/doc/smartnav/copyright"
chmod 644 "$ROOT/usr/share/doc/smartnav/copyright"
cat > "$ROOT/DEBIAN/control" <<CONTROL
Package: smartnav
Version: $VERSION
Architecture: all
Maintainer: Buğra Çalışkandinç <bugracaliskandinc@gmail.com>
Depends: python3, python3-tk, libxtst6
Suggests: xdotool
Section: education
Priority: optional
Homepage: https://github.com/bugracdnc/smartnav
Description: Always-on-top slide navigation buttons for smart boards
 SmartNav: akıllı tahtada sunum ve PDF'lerde ileri/geri gezinmek için
 her zaman üstte duran, dokunmatik dostu ◀ ▶ düğmeleri.
CONTROL
find "$ROOT" -type d -exec chmod 755 {} +
dpkg-deb --root-owner-group -Zxz --build "$ROOT" "$OUT/smartnav_${VERSION}_all.deb" >/dev/null

# --- offline bundle ---
B="$ROOT/bundle/smartnav-pardus"
mkdir -p "$B"
cp "$OUT/smartnav-x86_64" "$B/smartnav"
cp "$P/smartnav.svg" "$P/smartnav.desktop" "$P/kur.sh" "$P/kaldir.sh" "$B/"
tar -C "$ROOT/bundle" -czf "$OUT/smartnav-pardus.tar.gz" smartnav-pardus

(cd "$OUT" && sha256sum -- * > SHA256SUMS)
ls -l "$OUT"
