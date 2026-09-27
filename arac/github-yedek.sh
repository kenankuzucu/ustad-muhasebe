#!/usr/bin/env bash
# ÜSTAD MUHASEBE → GitHub yedeği (tek komut)
#   Kullanım:  bash arac/github-yedek.sh "v1.3 · bütçe ekranı düzeltmeleri"
# Kaynak proje:  C:\Users\kenan\Downloads\Programs\MUHASEBE\USTAD-MUHASEBE
# Depo       :  https://github.com/kenankuzucu/ustad-muhasebe  (özel · kategori: MUHASEBE)
#
# Kişisel veri (veri/, yedek/, cikti/, build/, dist/, *.exe) DEPOYA GİRMEZ.
set -u
KAYNAK="C:/Users/kenan/Downloads/Programs/MUHASEBE/USTAD-MUHASEBE"
DEPO="C:/Users/kenan/OneDrive/Desktop/USTAD-GITHUB-YEDEK/2026-09-27/USTAD-MUHASEBE-KAYNAK"
MESAJ="${1:-ÜSTAD MUHASEBE güncelleme}"

export GITHUB_TOKEN=$(grep -m1 '^GITHUB_TOKEN=' "C:/Users/kenan/AppData/Local/hermes/.env" | cut -d= -f2- | tr -d '"'"'"'\r')
export GIT_TERMINAL_PROMPT=0
[ -z "${GITHUB_TOKEN:-}" ] && { echo "HATA: GITHUB_TOKEN bulunamadi"; exit 1; }

echo "== 1) Kaynak koddan depo klasorune esitleme (kisisel veri haric) =="
for d in panel sunucu arac; do
  rm -rf "$DEPO/$d"; mkdir -p "$DEPO/$d"
  ( cd "$KAYNAK/$d" && tar -cf - --exclude=__pycache__ --exclude='*.log' . ) | ( cd "$DEPO/$d" && tar -xf - )
done
for f in BASLAT.bat AG-AC.bat OKU-BENI.md; do cp -f "$KAYNAK/$f" "$DEPO/$f"; done

echo "== 2) Sir taramasi =="
if grep -rnE "ghp_|gho_|github_pat_|AIza[0-9A-Za-z_-]{20,}" "$DEPO" --include='*.py' --include='*.js' --include='*.html' --include='*.md' 2>/dev/null | grep -v 'AIza\.\.\.'; then
  echo "!!! SIR BULUNDU — push IPTAL"; exit 1
fi
echo "   temiz."

echo "== 3) Commit + push =="
cd "$DEPO" || exit 1
git add -A
if git diff --cached --quiet; then echo "   degisiklik yok, push gerekmiyor."; else
  git -c core.autocrlf=false commit -q -m "$MESAJ"
fi
git -c credential.helper='!f() { echo username=kenankuzucu; echo password=$GITHUB_TOKEN; }; f' push origin main 2>&1 | sed "s/$GITHUB_TOKEN/***TOKEN***/g"

echo "== 4) Dogrulama (yerel HEAD == uzak main) =="
YEREL=$(git rev-parse HEAD)
UZAK=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/kenankuzucu/ustad-muhasebe/commits/main | grep -m1 '"sha"' | cut -d'"' -f4)
echo "   yerel: $YEREL"
echo "   uzak : $UZAK"
[ "$YEREL" = "$UZAK" ] && echo "   ✔ YEDEK TAMAM" || echo "   ✘ ESIT DEGIL — push tekrar denenmeli"
