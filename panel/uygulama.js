/* ==========================================================================
   ÜSTAD MUHASEBE · panel motoru (saf JS, kütüphane yok)
   ========================================================================== */
"use strict";

const $ = (s, k = document) => k.querySelector(s);
const $$ = (s, k = document) => Array.from(k.querySelectorAll(s));
const KACT = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const RENK = { turkuaz: "#22d3ee", pembe: "#f472b6", altin: "#fbbf24", yesil: "#34d399", mor: "#a78bfa", kirmizi: "#fb7185", mavi: "#60a5fa" };
const PALET = [RENK.turkuaz, RENK.pembe, RENK.altin, RENK.yesil, RENK.mor, RENK.mavi, RENK.kirmizi, "#facc15"];
const TEMALAR = [
  ["gece", "Gece", "Koyu lacivert · turkuaz + pembe + altın"],
  ["gunduz", "Gündüz", "Açık zemin · aynı renkler, okunması kolay"],
  ["altin", "Altın", "ÜSTAD altını · kahve zemin · turkuaz"],
  ["lavanta", "Lavanta", "Mor + fuşya · yumuşak gece"],
  ["okyanus", "Okyanus", "Mavi + turkuaz + lime"],
  ["orman", "Orman", "Yeşil + lime + amber"],
  ["gul", "Gül", "Pembe + gül kurusu · sıcak gece"],
  ["neon", "Neon", "Turkuaz + mor + kırmızı · parlak kenar"],
  ["kahve", "Kahve", "Amber + kahve · sıcak toprak"],
  ["zumrut", "Zümrüt", "Derin yeşil + lime + altın"],
  ["kuzey", "Kuzey", "Kutup mavisi + lila · sakin"],
  ["limon", "Limon", "Lime + sarı · ferah"],
  ["bordo", "Bordo", "Şarap kırmızısı + gül + altın"],
];
const PALETLER = [
  ["tatli", "Tatlı", "turkuaz · pembe · altın", ["#22d3ee", "#f472b6", "#fbbf24"]],
  ["canli", "Canlı", "fuşya · sarı · yeşil", ["#ff5fa2", "#ffd166", "#06d6a0"]],
  ["pastel", "Pastel", "yumuşak tonlar", ["#7dd3fc", "#fbcfe8", "#fde68a"]],
  ["sicak", "Sıcak", "turuncu · kırmızı", ["#ff8a4c", "#ff6b6b", "#ffd24c"]],
  ["kuzey", "Kuzey", "mavi · lila", ["#60a5fa", "#a5b4fc", "#e0e7ff"]],
  ["zumrut", "Zümrüt", "yeşil · lime", ["#10b981", "#34d399", "#a3e635"]],
];

/* --------------------------------------------------------------------- LOGO
   Tatlı, ilgi çekici ve muhasebeye yakışan amblem: altın kalkan içinde
   defter (çizgili sayfa) + Türk lirası sikkesi + sütun grafiği, iki yanında
   simetrik para desteleri. Renkleri temadan/paletten gelir. */
function logoSVG() {
  return `<svg viewBox="0 0 120 120" role="img" aria-label="ÜSTAD MUHASEBE amblemi">
  <defs>
    <linearGradient id="lgAltin" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fff6d0"/><stop offset=".4" stop-color="#fbbf24"/>
      <stop offset=".8" stop-color="#f0930b"/><stop offset="1" stop-color="#b45309"/>
    </linearGradient>
    <linearGradient id="lgAksan" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="var(--turkuaz)"/><stop offset=".55" stop-color="var(--pembe)"/>
      <stop offset="1" stop-color="var(--altin)"/>
    </linearGradient>
    <linearGradient id="lgZemin" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="var(--turkuaz)" stop-opacity=".95"/>
      <stop offset=".5" stop-color="var(--mor)" stop-opacity=".9"/>
      <stop offset="1" stop-color="var(--pembe)" stop-opacity=".95"/>
    </linearGradient>
    <linearGradient id="lgSayfa" x1=".2" y1="0" x2=".8" y2="1">
      <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#dfeaf7"/>
    </linearGradient>
    <radialGradient id="lgIsik" cx=".32" cy=".2" r=".85">
      <stop offset="0" stop-color="#ffffff" stop-opacity=".85"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- tatlı yuvarlak zemin -->
  <g class="kalkanNefes">
    <path d="M60 4 C93 4 116 24 116 60 C116 96 93 116 60 116 C27 116 4 96 4 60 C4 24 27 4 60 4 Z"
          fill="url(#lgZemin)"/>
    <path d="M60 9 C90 9 111 27 111 60 C111 93 90 111 60 111 C30 111 9 93 9 60 C9 27 30 9 60 9 Z"
          fill="#121a29" opacity=".86"/>
    <ellipse cx="42" cy="30" rx="30" ry="20" fill="url(#lgIsik)" opacity=".13"/>
  </g>

  <!-- dönen altın halka -->
  <g class="halkaDon">
    <circle cx="60" cy="60" r="55" fill="none" stroke="url(#lgAksan)" stroke-width="2.4"
            stroke-dasharray="9 11" stroke-linecap="round" opacity=".9"/>
  </g>

  <!-- ABAKÜS: çerçeveli, net -->
  <g class="bakirParlak">
    <rect x="31" y="22" width="58" height="30" rx="7" fill="#0b1322" stroke="url(#lgAltin)" stroke-width="1.6"/>
    <g stroke="#66798f" stroke-width="1" opacity=".5">
      <line x1="37" y1="31" x2="83" y2="31"/><line x1="37" y1="38" x2="83" y2="38"/><line x1="37" y1="45" x2="83" y2="45"/>
    </g>
    <g>
      <circle cx="43" cy="31" r="3.3" fill="var(--turkuaz)"/><circle cx="52" cy="31" r="3.3" fill="var(--turkuaz)"/>
      <circle cx="70" cy="31" r="3.3" fill="var(--pembe)"/>
      <circle cx="48" cy="38" r="3.3" fill="var(--altin)"/><circle cx="57" cy="38" r="3.3" fill="var(--altin)"/>
      <circle cx="66" cy="38" r="3.3" fill="var(--altin)"/><circle cx="75" cy="38" r="3.3" fill="var(--altin)"/>
      <circle cx="40" cy="45" r="3.3" fill="var(--yesil)"/>
      <circle cx="58" cy="45" r="3.3" fill="var(--mor)"/><circle cx="67" cy="45" r="3.3" fill="var(--mor)"/>
      <circle cx="76" cy="45" r="3.3" fill="var(--turkuaz)"/>
    </g>
  </g>

  <!-- AÇIK DEFTER (abaküsün altında, iki yapraklı) -->
  <g transform="translate(26 55)">
    <path d="M0 4 C11 -2 27 -2 34 2 L34 40 C27 36 11 36 0 41 Z" fill="url(#lgSayfa)" stroke="#9db0c6" stroke-width="1.1"/>
    <path d="M68 4 C57 -2 41 -2 34 2 L34 40 C41 36 57 36 68 41 Z" fill="url(#lgSayfa)" stroke="#9db0c6" stroke-width="1.1"/>
    <line x1="34" y1="2" x2="34" y2="40" stroke="#b3c2d3" stroke-width="1.3"/>
    <g stroke="#8ea3ba" stroke-width="1.4" stroke-linecap="round" opacity=".8">
      <line x1="6" y1="13" x2="27" y2="10"/><line x1="6" y1="21" x2="27" y2="18"/><line x1="6" y1="29" x2="23" y2="26"/>
      <line x1="41" y1="10" x2="62" y2="13"/><line x1="41" y1="18" x2="62" y2="21"/><line x1="41" y1="26" x2="58" y2="29"/>
    </g>
  </g>

  <!-- ÖNDEKİ SEVİMLİ ₺ SİKKESİ (defterin alt ortasına biner — simetrik) -->
  <g class="paraSal">
    <circle cx="60" cy="86" r="18.5" fill="url(#lgAltin)" stroke="#8a5a06" stroke-width="1.5"/>
    <circle cx="60" cy="86" r="14.6" fill="none" stroke="#fff7dd" stroke-width="1.1" opacity=".75"/>
    <text x="60" y="93.5" text-anchor="middle" font-size="20" font-weight="800"
          font-family="Segoe UI, system-ui, sans-serif" fill="#6b3f04">&#8378;</text>
    <circle cx="52" cy="72" r="2" fill="#fff8dc" opacity=".85"/>
  </g>

  <!-- iki yanda simetrik küçük sikkeler -->
  <g>
    <circle cx="17" cy="89" r="7.4" fill="url(#lgAltin)" stroke="#8a5a06" stroke-width="1"/>
    <circle cx="103" cy="89" r="7.4" fill="url(#lgAltin)" stroke="#8a5a06" stroke-width="1"/>
    <text x="17" y="92.6" text-anchor="middle" font-size="8.6" font-weight="800" fill="#7a4a05">&#8378;</text>
    <text x="103" y="92.6" text-anchor="middle" font-size="8.6" font-weight="800" fill="#7a4a05">&#8378;</text>
  </g>

  <!-- kıvılcımlar -->
  <g class="kivilcim" fill="#fff8dc">
    <circle cx="15" cy="64" r="2.2"/><circle cx="104" cy="66" r="2.2"/>
    <circle cx="24" cy="20" r="1.6"/><circle cx="97" cy="22" r="1.9"/>
    <circle cx="60" cy="6" r="1.6"/>
  </g>
</svg>`;
}
function logoYerlestir() {
  $$("[data-logo]").forEach((y) => { if (!y.dataset.doldu) { y.innerHTML = logoSVG(); y.dataset.doldu = "1"; } });
}
function paletAyarla(p) {
  document.documentElement.setAttribute("data-palet", p);
  $$(".paletDugme").forEach((b) => b.classList.toggle("aktif", b.dataset.palet === p));
  const a = JSON.parse(localStorage.getItem("ustad_ayar") || "{}");
  a.palet = p;
  localStorage.setItem("ustad_ayar", JSON.stringify(a));
  api("/api/renk", { palet: p }).catch(() => {});
}

let DURUM = { sayilar: {}, ayar: {}, ozet: null, ekran: "genel", cari_id: null, hesap_id: null, rapor_tur: "gelir-gider", kilit: false };

/* ------------------------------------------------------------- biçim */
function para(n, kisa = false) {
  n = Number(n || 0);
  if (kisa && Math.abs(n) >= 1000) return (n / 1000).toFixed(1).replace(".", ",") + " B";
  return n.toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " ₺";
}
function sayi(n) { return Number(n || 0).toLocaleString("tr-TR", { maximumFractionDigits: 2 }); }
function tarihKisa(s) {
  if (!s) return "—";
  const p = String(s).slice(0, 10).split("-");
  return p.length === 3 ? `${p[2]}.${p[1]}.${p[0]}` : s;
}
function simdiTarih() {
  return new Date().toLocaleDateString("tr-TR", { day: "2-digit", month: "long", year: "numeric", weekday: "long" });
}
function bugunISO() { const d = new Date(); return d.toISOString().slice(0, 10); }

/* ------------------------------------------------------------- ağ */
function oturumTokeni() { return localStorage.getItem("ustad_token") || ""; }
/* Ağ sağlamlığı: antivirüs/proxy araya girdiğinde bağlantı kopabiliyor ya da
   yarım yanıt dönebiliyor. Bu yüzden her istek 3 kez denenir, yarım yanıt
   yeni bağlantıyla tekrarlanır. */
async function api(yol, veri, deneme = 0) {
  const ayrac = yol.indexOf("?") >= 0 ? "&" : "?";
  const s = { cache: "no-store", headers: {} };
  if (veri) {
    s.method = "POST";
    s.headers["Content-Type"] = "application/json";
    s.body = JSON.stringify(veri);
  }
  const t = oturumTokeni();
  if (t) s.headers["X-Oturum"] = t;
  try {
    const r = await fetch(yol + ayrac + "_t=" + Date.now(), s);
    const metin = await r.text();
    let j = null;
    try { j = JSON.parse(metin); } catch (e) { j = null; }
    if (j === null) {
      if (deneme < 2) return api(yol, veri, deneme + 1);
      throw new Error("Sunucudan geçersiz yanıt geldi — tekrar dene");
    }
    if (!r.ok) {
      if (j.hata) throw new Error(j.hata);
      if (r.status === 403) throw new Error("Bu işlem için yetkin yok.");
    }
    return j;
  } catch (e) {
    if (deneme < 2 && /fetch|network|bağlantı/i.test(String(e.message))) {
      await new Promise((z) => setTimeout(z, 300));
      return api(yol, veri, deneme + 1);
    }
    throw e;
  }
}

/* ------------------------------------------------------------- bildirim */
let bildirimZaman = null;
function bildir(metin, kotu = false) {
  const k = $("#bildirim");
  k.textContent = metin;
  k.className = "bildirim" + (kotu ? " kotu" : "");
  clearTimeout(bildirimZaman);
  bildirimZaman = setTimeout(() => k.classList.add("gizli"), 3200);
}

/* ------------------------------------------------------------- modal */
let modalKaydet = null;
function modalAc(baslik, icerik, dugmeler) {
  $("#modalBaslik").textContent = baslik;
  $("#modalGovde").innerHTML = icerik;
  const alt = $("#modalAlt");
  alt.innerHTML = "";
  (dugmeler || []).forEach((d) => {
    const b = document.createElement("button");
    b.className = "dugme " + (d.sinif || "");
    b.textContent = d.ad;
    b.onclick = () => d.tikla && d.tikla();
    alt.appendChild(b);
  });
  $("#modal").classList.remove("gizli");
}
function modalKapat() { $("#modal").classList.add("gizli"); $("#modalGovde").innerHTML = ""; }

/* ------------------------------------------------------------- tablo */
function tablo(basliklar, satirlar, sec = {}) {
  const sagSutun = sec.sagSutun || [];
  const h = ['<div class="tabloSar">'];
  if (sec.baslik) h.push(`<div class="tabloBas"><h3>${KACT(sec.baslik)}</h3><span class="kartNot">${satirlar.length} kayıt</span></div>`);
  h.push('<div style="overflow:auto;max-height:' + (sec.yukseklik || "none") + '"><table><thead><tr>');
  basliklar.forEach((b, i) => h.push(`<th class="${sagSutun.includes(i) || /tutar|toplam|bakiye|borç|alacak|maaş|kalan|değer|ödeme|fiyat|kdv/i.test(b) ? "sayi" : ""}">${KACT(b)}</th>`));
  if (sec.islem) h.push('<th class="sayi">İşlem</th>');
  h.push("</tr></thead><tbody>");
  if (!satirlar.length) h.push(`<tr><td colspan="${basliklar.length + (sec.islem ? 1 : 0)}"><div class="bos">Kayıt yok — sağ üstteki düğmeyle yeni kayıt ekleyebilirsin.</div></td></tr>`);
  satirlar.forEach((s, j) => {
    h.push('<tr class="' + (j % 2 ? "zebra" : "") + '">');
    s.forEach((d, i) => {
      if (d && typeof d === "object" && d.hucre) h.push(`<td class="${d.sinif || ""}">${d.hucre}</td>`);
      else {
        const sag = sagSutun.includes(i) || /tutar|toplam|bakiye|borç|alacak|maaş|kalan|değer|ödeme|fiyat|kdv/i.test(basliklar[i] || "");
        h.push(`<td class="${sag ? "para" : ""}">${KACT(d)}</td>`);
      }
    });
    if (sec.islem) h.push(`<td class="sayi">${s[s.length - 1] && s[s.length - 1].hucre ? "" : ""}${sec.islem}</td>`);
    h.push("</tr>");
  });
  h.push("</tbody></table></div>");
  if (sec.toplamlar) {
    h.push('<div class="tabloToplam">' + sec.toplamlar.map((t) => `<span>${KACT(t[0])}: <b>${t[1]}</b></span>`).join("") + "</div>");
  }
  h.push("</div>");
  return h.join("");
}

/* ------------------------------------------------------------- grafikler */
function cizgiGrafik(seri) {
  if (!seri || !seri.length) return "";
  const G = 900, Y = 320, sol = 74, sag = 18, ust = 26, alt = 42;
  const icG = G - sol - sag, icY = Y - ust - alt;
  const enb = Math.max(1, ...seri.map((s) => Math.max(s.gelir, s.gider, s.kar)));
  const yuk = (v) => ust + icY - (v / enb) * icY;
  const adim = icG / seri.length;
  let h = [`<svg class="grafik" viewBox="0 0 ${G} ${Y}" preserveAspectRatio="none">`,
    `<defs>
      <linearGradient id="gGelir" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${RENK.yesil}"/><stop offset="1" stop-color="${RENK.turkuaz}"/></linearGradient>
      <linearGradient id="gGider" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${RENK.pembe}"/><stop offset="1" stop-color="${RENK.mor}"/></linearGradient>
    </defs>`];
  for (let i = 0; i <= 4; i++) {
    const y = ust + (icY / 4) * i;
    const deger = Math.round(enb * (1 - i / 4));
    h.push(`<line x1="${sol}" y1="${y}" x2="${G - sag}" y2="${y}" stroke="currentColor" stroke-opacity=".12" stroke-dasharray="3 5"/>`);
    h.push(`<text x="${sol - 10}" y="${y + 4}" text-anchor="end" font-size="11.5" fill="currentColor" fill-opacity=".55">${sayi(deger)}</text>`);
  }
  const bw = Math.max(6, adim * 0.26);
  seri.forEach((s, i) => {
    const x = sol + i * adim + adim / 2;
    h.push(`<rect x="${x - bw - 1}" y="${yuk(s.gelir)}" width="${bw}" height="${ust + icY - yuk(s.gelir)}" rx="4" fill="url(#gGelir)"/>`);
    h.push(`<rect x="${x + 1}" y="${yuk(s.gider)}" width="${bw}" height="${ust + icY - yuk(s.gider)}" rx="4" fill="url(#gGider)"/>`);
    h.push(`<text x="${x}" y="${Y - 14}" text-anchor="middle" font-size="11" fill="currentColor" fill-opacity=".62">${KACT(s.ay)}</text>`);
  });
  const nokta = seri.map((s, i) => `${sol + i * adim + adim / 2},${yuk(s.kar)}`).join(" ");
  h.push(`<polyline points="${nokta}" fill="none" stroke="${RENK.altin}" stroke-width="2.6" stroke-linejoin="round" stroke-dasharray="0"/>`);
  seri.forEach((s, i) => {
    h.push(`<circle cx="${sol + i * adim + adim / 2}" cy="${yuk(s.kar)}" r="3.6" fill="${RENK.altin}" stroke="#0b1220" stroke-width="1.4"><title>${s.ay}: kâr ${para(s.kar)}</title></circle>`);
  });
  h.push("</svg>");
  return h.join("");
}

function halkaGrafik(kategoriler) {
  const veri = (kategoriler || []).slice(0, 7);
  const toplam = veri.reduce((t, k) => t + k.tutar, 0) || 1;
  const R = 62, C = 2 * Math.PI * R;
  let ofs = 0;
  const dilimler = veri.map((k, i) => {
    const oran = k.tutar / toplam;
    const s = `<circle cx="80" cy="80" r="${R}" fill="none" stroke="${PALET[i % PALET.length]}" stroke-width="24"
      stroke-dasharray="${(oran * C).toFixed(2)} ${(C - oran * C).toFixed(2)}"
      stroke-dashoffset="${(-ofs * C).toFixed(2)}" transform="rotate(-90 80 80)"><title>${KACT(k.ad)} · ${para(k.tutar)}</title></circle>`;
    ofs += oran;
    return s;
  }).join("");
  const liste = veri.map((k, i) => `<div class="halkaSatir"><i style="background:${PALET[i % PALET.length]}"></i>
      <span>${KACT(k.ad)}</span><b>${para(k.tutar)}</b></div>`).join("");
  return `<div class="halkaSar">
    <svg viewBox="0 0 160 160" style="width:172px;height:172px;flex:0 0 172px">${dilimler}
      <text x="80" y="76" text-anchor="middle" font-size="13" fill="currentColor" fill-opacity=".6">TOPLAM</text>
      <text x="80" y="96" text-anchor="middle" font-size="15" font-weight="700" fill="currentColor">${para(toplam, true)}</text>
    </svg><div class="halkaListe">${liste || '<div class="bos">Kayıt yok</div>'}</div></div>`;
}

/* ------------------------------------------------------------- giriş perdesi
   Şifre artık SUNUCUDA doğrulanır (PBKDF2 + oturum jetonu); rol de sunucudan gelir.
   İstemci tarafındaki sayaç yalnızca hızlı denemeyi engellemek için durur. */
function kilitDurumu() {
  const k = JSON.parse(localStorage.getItem("ustad_kilit") || '{"hata":0,"kadar":0}');
  if (k.kadar && Date.now() > k.kadar) { k.hata = 0; k.kadar = 0; localStorage.setItem("ustad_kilit", JSON.stringify(k)); }
  return k;
}
async function girisDene(kullanici, sifre) {
  const k = kilitDurumu();
  if (k.kadar && Date.now() < k.kadar) {
    const sn = Math.ceil((k.kadar - Date.now()) / 1000);
    return { tamam: false, mesaj: `Çok fazla hatalı giriş — ${sn} saniye bekle.` };
  }
  let c;
  try {
    const r = await fetch("/api/giris", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ kullanici: kullanici.trim().toLowerCase(), sifre }),
    });
    c = await r.json();
  } catch (e) {
    return { tamam: false, mesaj: "Sunucuya ulaşılamadı — BASLAT.bat ile sunucuyu aç." };
  }
  if (c && c.tamam) {
    localStorage.setItem("ustad_kilit", JSON.stringify({ hata: 0, kadar: 0 }));
    localStorage.setItem("ustad_token", c.token || "");
    localStorage.setItem("ustad_kullanici", JSON.stringify({ ad: c.ad, rol: c.rol, rol_ad: c.rol_ad }));
    return { tamam: true, rol: c.rol_ad };
  }
  k.hata = (k.hata || 0) + 1;
  if (k.hata >= 5) { k.kadar = Date.now() + 60000; k.hata = 0; }
  localStorage.setItem("ustad_kilit", JSON.stringify(k));
  return { tamam: false, mesaj: k.kadar ? "5 hatalı giriş — 60 saniye kilitlendi." : `Kullanıcı veya şifre hatalı (${5 - k.hata} hak kaldı).` };
}
function kilitAc() {
  $("#perde").classList.add("gizli");
  $("#uygulama").classList.remove("gizli");
  oturumYukle();
}
function ekranSec(ad) { DURUM.ekran = ad; }

/* ------------------------------------------------------------- temel yükleme */
async function baslat() {
  logoYerlestir();
  $("#ustTarih").textContent = simdiTarih();
  const yerel = JSON.parse(localStorage.getItem("ustad_ayar") || "{}");
  if (yerel.palet) paletAyarla(yerel.palet);
  try {
    const d = await api("/api/durum");
    DURUM.sayilar = d.sayilar || {};
    DURUM.ayar = d.ayar || {};
    const t = yerel.tema || d.ayar.tema || "gece";
    temaAyarla(t);
    $("#yanSurum").textContent = `v${d.surum} · ${d.db} · ${(d.db_boyut / 1024).toFixed(0)} KB`;
    $("#yanFirmaAd").textContent = "ÜSTAD MUHASEBE";
    const alt = $("#yanFirmaAlt");
    if (alt) alt.textContent = "TAM TEŞKİLAT · " + (d.firma || "ÜSTAD SALON KENAN");
    rozetleriYenile();
    uyarilariYenile();
  } catch (e) {
    bildir("Sunucuya ulaşılamadı — BASLAT.bat ile sunucuyu aç.", true);
    $("#yanSurum").textContent = "sunucu yok";
  }
}
async function rozetleriYenile() {
  try {
    const d = await api("/api/durum");
    $("#rozetCari").textContent = (d.sayilar || {}).cari || 0;
    $("#rozetFatura").textContent = (d.sayilar || {}).fatura || 0;
  } catch (e) { /* sunucu yok */ }
  try { const h = await api("/api/harcama-ozet?gun=1"); $("#rozetHarcama").textContent = h.kayit_sayisi || 0; }
  catch (e) { $("#rozetHarcama").textContent = "—"; }
  try { const g = await api("/api/gorev"); $("#rozetGorev").textContent = (g.kayit || []).filter((x) => x.durum === "Açık").length; }
  catch (e) { $("#rozetGorev").textContent = "0"; }
  try {
    const c = await api("/api/cek");
    $("#rozetCek").textContent = (c.vadesi_gecen || []).length + (c.yaklasan || []).length;
  } catch (e) { $("#rozetCek").textContent = "0"; }
}
async function uyarilariYenile() {
  try {
    const u = await api("/api/bildirim");
    DURUM.uyarilar = u.kayit || [];
    $("#canRozet").textContent = DURUM.uyarilar.length;
    $("#canRozet").style.display = DURUM.uyarilar.length ? "flex" : "none";
    if (DURUM.uyarilar.length && !sessionStorage.getItem("ustad_uyari_gosterildi")) {
      sessionStorage.setItem("ustad_uyari_gosterildi", "1");
      bildir(`${DURUM.uyarilar.length} uyarı var — sağ üstteki çandan bak.`);
    }
  } catch (e) { $("#canRozet").style.display = "none"; }
}
function uyariPaneli() {
  const k = $("#canPanel");
  if (k) { k.remove(); return; }
  const p = document.createElement("div");
  p.id = "canPanel";
  p.className = "canPanel";
  const u = DURUM.uyarilar || [];
  p.innerHTML = `<div class="kartUst" style="margin-bottom:10px"><h3>Uyarılar · ${u.length}</h3>
      <span class="kartNot">vadesi geçen · yaklaşan · bütçe · stok</span></div>` +
    (u.length ? u.map((x) => `<div class="uyariSatir ${x.seviye}">
        <div><b>${KACT(x.baslik)}</b><span>${KACT(x.mesaj)}</span></div></div>`).join("")
      : '<div class="bos">Şu an uyarı yok — her şey yolunda.</div>') +
    '<div style="display:flex;gap:8px;margin-top:10px"><button class="dugme" id="canYenile">Yenile</button>' +
    '<button class="dugme" id="canKapat">Kapat</button></div>';
  $("#ustSagBildirim") || document.querySelector(".ustSag").appendChild(p);
  $("#canYenile").onclick = async () => { await uyarilariYenile(); p.remove(); uyariPaneli(); };
  $("#canKapat").onclick = () => p.remove();
}
async function oturumYukle() {
  const k = JSON.parse(localStorage.getItem("ustad_kullanici") || "{}");
  if (k.rol_ad) {
    const s = $("#yanSurum");
    if (s) s.title = `Giriş: ${k.ad} (${k.rol_ad})`;
  }
  await ekranCiz("genel");
}
function temaAyarla(t) {
  document.documentElement.setAttribute("data-tema", t);
  $$(".temaDugme").forEach((b) => b.classList.toggle("aktif", b.dataset.tema === t));
  const a = JSON.parse(localStorage.getItem("ustad_ayar") || "{}");
  a.tema = t;
  localStorage.setItem("ustad_ayar", JSON.stringify(a));
  api("/api/ayar", { tema: t }).catch(() => {});
}

/* ------------------------------------------------------------- ekran yönlendirme */
const BASLIKLAR = {
  genel: ["Genel Bakış", "İşletmenin canlı durumu — gelir, gider, kasa, uyarılar ve nakit akışı"],
  cari: ["Cari Yönetimi", "Müşteri ve tedarikçi kartları · hareketler · ekstre · tahsilat"],
  harcama: ["Harcamalar · Sade Defter", "Kurumsal olmayan günlük gelir/gider defteri — ekle, düzenle, sil"],
  butce: ["Bütçe", "Kategori bazlı aylık bütçe · harcama çubuğu · aşım uyarısı"],
  gorev: ["Görevler & Hatırlatma", "Vergi, ödeme, sayım ve takip işleri — gecikeni kırmızı"],
  gorusme: ["Görüşmeler", "Müşteri görüşme kayıtları ve takip planı"],
  gelir: ["Gelirler", "Kategori bazlı gelir defteri"],
  gider: ["Giderler", "Kategori bazlı gider defteri"],
  kasa: ["Kasa & Bankalar", "Kasa ve banka hesapları · giriş çıkış hareketleri"],
  fatura: ["Faturalar", "Satış ve alış faturaları · KDV · ödeme durumu"],
  cek: ["Çek & Senet", "Alınan/verilen çek-senet · vade takvimi · durum takibi"],
  tekrar: ["Tekrarlayan Kayıt & Abonelik", "Kira, maaş, faturalar her ay kendiliğinden düşsün"],
  stok: ["Stok Yönetimi", "Ürün, miktar, kritik seviye ve stok değeri"],
  personel: ["Personel & Bordro", "Çalışanlar · maaş · avans/prim/izin (puantaj)"],
  ai: ["Muhasebe Asistanı", "Kendi verinle konuşan Türkçe asistan — sayı uydurmaz, defterden okur"],
  fis: ["Fiş & Fatura Fotoğrafları", "Telefondan fotoğraf yükle · toplu işle · deftere aktar"],
  rapor: ["Raporlar", "Gelir-gider, kâr-zarar, KDV, anomali, nakit akışı, yıl karnesi — Word/Excel/PDF"],
  cikti: ["Word / Excel / PDF Çıktıları", "Üretilen belgeler; çift tıkla indir, sil ile temizle"],
  ayarlar: ["Ayarlar & Yedek", "Firma · kullanıcılar ve roller · AI anahtarı · ağ · otomatik yedek"],
};

async function ekranCiz(ad) {
  DURUM.ekran = ad;
  $$(".menuOge").forEach((b) => b.classList.toggle("aktif", b.dataset.ekran === ad));
  const [b, alt] = BASLIKLAR[ad] || ["ÜSTAD MUHASEBE", ""];
  $("#ekranBaslik").textContent = b;
  $("#ekranAlt").textContent = alt;
  $("#icerik").innerHTML = '<div class="bos">Yükleniyor…</div>';
  $("#yan").classList.remove("acik");
  try {
    await (EKRANLAR[ad] || EKRANLAR.genel)();
    sayaclar($("#icerik"));
  } catch (e) {
    $("#icerik").innerHTML = `<div class="kart"><div class="kartEtiket">HATA</div><div class="kartAltYazi">${KACT(e.message)}</div></div>`;
  }
}

/* ==========================================================================
   EKRANLAR
   ========================================================================== */
const EKRANLAR = {};

/* ---------------------------------------------------------- 1) GENEL BAKIŞ */
EKRANLAR.genel = async () => {
  const o = await api("/api/ozet");
  DURUM.ozet = o;
  $("#icerik").innerHTML = `
    <div class="izgara k4" style="margin-bottom:14px">
      <div class="kart yesil"><div class="kartEtiket">Günlük Gelir</div>
        <div class="kartDeger yesil" data-sayac="${o.gunluk_gelir}">${para(o.gunluk_gelir)}</div>
        <div class="kartAltYazi">Bu ay: <b>${para(o.aylik_gelir)}</b></div></div>
      <div class="kart pembe"><div class="kartEtiket">Günlük Gider</div>
        <div class="kartDeger pembe" data-sayac="${o.gunluk_gider}">${para(o.gunluk_gider)}</div>
        <div class="kartAltYazi">Bu ay: <b>${para(o.aylik_gider)}</b></div></div>
      <div class="kart turkuaz"><div class="kartEtiket">Aylık Net Kâr</div>
        <div class="kartDeger turkuaz" data-sayac="${o.net_kar}">${para(o.net_kar)}</div>
        <div class="kartAltYazi">Gelir − gider</div></div>
      <div class="kart altin"><div class="kartEtiket">Kasa + Banka Toplamı</div>
        <div class="kartDeger altin" data-sayac="${o.kasa_toplam}">${para(o.kasa_toplam)}</div>
        <div class="kartAltYazi">${DURUM.sayilar.hesap || 0} hesap</div></div>
    </div>

    <div class="izgara k4" style="margin-bottom:14px">
      <div class="kart"><div class="kartEtiket">Bizim Alacağımız</div>
        <div class="kartDeger yesil" data-sayac="${o.toplam_alacak}">${para(o.toplam_alacak)}</div><div class="kartAltYazi">${o.cari_adet} cari kartı</div></div>
      <div class="kart"><div class="kartEtiket">Bizim Borcumuz</div>
        <div class="kartDeger kirmizi" data-sayac="${o.toplam_borc}">${para(o.toplam_borc)}</div><div class="kartAltYazi">tedarikçilere</div></div>
      <div class="kart kirmizi"><div class="kartEtiket">Vadesi Geçen Fatura</div>
        <div class="kartDeger kirmizi uyariNabiz" data-sayac="${o.vadesi_gecen_tutar}">${para(o.vadesi_gecen_tutar)}</div><div class="kartAltYazi">${o.vadesi_gecen_adet} fatura</div></div>
      <div class="kart"><div class="kartEtiket">Bekleyen Fatura</div>
        <div class="kartDeger altin" data-sayac="${o.bekleyen_fatura_tutar}">${para(o.bekleyen_fatura_tutar)}</div><div class="kartAltYazi">${o.bekleyen_fatura_adet} fatura</div></div>
    </div>

    <div class="izgara k3" style="margin-bottom:14px">
      <div class="kart" style="grid-column:span 2">
        <div class="kartUst"><h3>Gelir · Gider · Kâr Grafiği (12 ay)</h3><span class="damga turkuaz">12 AY</span></div>
        ${cizgiGrafik(o.seri)}
        <div class="lejant">
          <span><i style="background:linear-gradient(180deg,${RENK.yesil},${RENK.turkuaz})"></i>Gelir</span>
          <span><i style="background:linear-gradient(180deg,${RENK.pembe},${RENK.mor})"></i>Gider</span>
          <span><i style="background:${RENK.altin}"></i>Kâr</span>
        </div>
      </div>
      <div class="kart"><div class="kartUst"><h3>Gelir Kategori Dağılımı</h3></div>
        ${halkaGrafik(o.kategoriler)}</div>
    </div>

    <div class="izgara k2">
      <div class="kart"><div class="kartUst"><h3>Son İşlemler</h3><span class="kartNot">son 10 cari hareketi</span></div>
        <table><thead><tr><th>Tarih</th><th>Cari</th><th>Açıklama</th><th class="sayi">Borç</th><th class="sayi">Alacak</th></tr></thead><tbody>
        ${(o.son_islemler || []).map((s) => `<tr><td>${tarihKisa(s.tarih)}</td><td>${KACT(s.unvan || "—")}</td>
          <td>${KACT(s.aciklama || "—")}</td><td class="para">${s.borc ? para(s.borc) : "—"}</td>
          <td class="para paraPoz">${s.alacak ? para(s.alacak) : "—"}</td></tr>`).join("")}
        </tbody></table></div>

      <div class="kart"><div class="kartUst"><h3>En Çok Borçlu Cariler</h3><span class="kartNot">EN ÇOK KULLANILAN</span></div>
        ${(o.en_borclu || []).map((c, i) => `<div class="halkaSatir"><i style="background:${PALET[i % PALET.length]}"></i>
          <span>${KACT(c.unvan)}</span><b class="paraPoz">${para(c.bakiye)}</b></div>`).join("") || '<div class="bos">Borçlu cari yok</div>'}
        <div class="tabloToplam">
          <span>Kritik stok: <b>${o.kritik_stok} ürün</b></span>
          <span>Aktif personel: <b>${o.personel_adet}</b></span>
          <span>Fatura: <b>${o.fatura_adet}</b></span>
        </div></div>
    </div>`;
};

/* ---------------------------------------------------------- 2) CARİ YÖNETİMİ */
const CARI_SEKME = ["Kart Bilgileri", "Hareketler", "Ekstre", "Faturalar", "Tahsilat / Ödeme", "Notlar"];
let cariSekme = 0;

EKRANLAR.cari = async () => {
  const d = await api("/api/cari");
  DURUM.cariler = d.kayit;
  if (!DURUM.cari_id && d.kayit.length) DURUM.cari_id = d.kayit[0].id;
  $("#icerik").innerHTML = `
    <div class="izgara" style="grid-template-columns:calc(310px * var(--olcek)) 1fr;align-items:start">
      <div class="tabloSar">
        <div class="tabloBas"><h3>Cari Kartları</h3><span class="kartNot">${d.toplam} kayıt</span></div>
        <div style="padding:10px"><input id="cariAra" class="aramaAlan" placeholder="Cari ara…"
          style="width:100%;padding:8px 11px;border-radius:12px;border:1px solid var(--cizgi);background:var(--kart2)"></div>
        <div id="cariListe" style="max-height:62vh;overflow:auto"></div>
        <div class="tabloToplam"><span>Alacak: <b class="paraPoz">${para(d.alacak)}</b></span>
          <span>Borç: <b class="paraNeg">${para(d.borc)}</b></span></div>
      </div>
      <div id="cariDetay"></div>
    </div>
    <div style="margin-top:12px;display:flex;gap:9px;flex-wrap:wrap">
      <button class="dugme birincil" id="cariYeni">+ Yeni Cari Kartı</button>
      <button class="dugme" id="cariWord">Word'e Aktar</button>
      <button class="dugme" id="cariExcel">Excel'e Aktar</button>
    </div>`;
  cariListeCiz();
  $("#cariAra").oninput = () => cariListeCiz($("#cariAra").value);
  $("#cariYeni").onclick = () => cariForm(null);
  $("#cariWord").onclick = () => indir("/api/disa-aktar?kaynak=cari&tur=docx");
  $("#cariExcel").onclick = () => indir("/api/disa-aktar?kaynak=cari&tur=xlsx");
  cariDetayCiz();
};

function cariListeCiz(ara = "") {
  const a = ara.toLowerCase();
  const kayit = (DURUM.cariler || []).filter((c) => !a || (c.unvan || "").toLowerCase().includes(a) || (c.kod || "").toLowerCase().includes(a));
  $("#cariListe").innerHTML = kayit.map((c) => `
    <div class="cariOge ${c.id === DURUM.cari_id ? "aktif" : ""}" data-cari="${c.id}">
      <div><b>${KACT(c.unvan)}</b><div class="kartNot">${KACT(c.kod || "")} · ${KACT(c.tip || "")}</div></div>
      <span class="para ${c.bakiye > 0 ? "paraPoz" : c.bakiye < 0 ? "paraNeg" : "paraNotr"}">${para(c.bakiye)}</span>
    </div>`).join("") || '<div class="bos">Cari bulunamadı</div>';
  $$("[data-cari]").forEach((k) => (k.onclick = () => { DURUM.cari_id = Number(k.dataset.cari); cariListeCiz($("#cariAra").value); cariDetayCiz(); }));
}

async function cariDetayCiz() {
  const c = (DURUM.cariler || []).find((x) => x.id === DURUM.cari_id);
  const kok = $("#cariDetay");
  if (!c) { kok.innerHTML = '<div class="kart"><div class="bos">Sol taraftan bir cari seç veya yeni kart oluştur.</div></div>'; return; }
  kok.innerHTML = `
    <div class="kart" style="margin-bottom:12px">
      <div class="kartUst">
        <div><h3>${KACT(c.unvan)}</h3><div class="kartNot">${KACT(c.kod || "")} · ${KACT(c.tip || "")} · ${KACT(c.telefon || "telefon yok")}</div></div>
        <div style="display:flex;gap:8px;align-items:center">
          <span class="damga ${c.bakiye > 0 ? "yesil" : c.bakiye < 0 ? "kirmizi" : "turkuaz"}">
            ${c.bakiye > 0 ? "Bizden Alacaklı" : c.bakiye < 0 ? "Biz Borçluyuz" : "Kapalı"} · ${para(Math.abs(c.bakiye))}</span>
          <button class="dugme kucuk" id="cariDuzenle">Düzenle</button>
          <button class="dugme kucuk kirmizi" id="cariSil">Sil</button>
        </div>
      </div>
      <div class="sekmeler">${CARI_SEKME.map((s, i) => `<button class="sekme ${i === cariSekme ? "aktif" : ""}" data-cs="${i}">${s}</button>`).join("")}</div>
      <div id="cariSekmeIcerik"></div>
    </div>`;
  $$("[data-cs]").forEach((b) => (b.onclick = () => { cariSekme = Number(b.dataset.cs); cariDetayCiz(); }));
  $("#cariDuzenle").onclick = () => cariForm(c);
  $("#cariSil").onclick = () => sil("cari", c.id, c.unvan, () => ekranCiz("cari"));
  cariSekmeCiz(c);
}

async function cariSekmeCiz(c) {
  const k = $("#cariSekmeIcerik");
  if (cariSekme === 0) {
    const satir = (a, b) => `<div class="halkaSatir"><span>${a}</span><b>${KACT(b || "—")}</b></div>`;
    k.innerHTML = `<div class="izgara k2">
      <div>${satir("Cari Kodu", c.kod)}${satir("Ünvan", c.unvan)}${satir("Tip", c.tip)}
        ${satir("Vergi Dairesi", c.vergi_dairesi)}${satir("Vergi / TC No", c.vergi_no)}${satir("Yetkili", c.yetkili)}</div>
      <div>${satir("Telefon", c.telefon)}${satir("E-posta", c.email)}${satir("İl / İlçe", (c.il || "") + " / " + (c.ilce || ""))}
        ${satir("Açılış Bakiyesi", para(c.acilis_bakiye))}${satir("Risk Limiti", para(c.risk_limiti))}${satir("Adres", c.adres)}</div>
    </div>`;
  } else if (cariSekme === 1) {
    const h = await api(`/api/hareket?cari_id=${c.id}`);
    const borcT = h.kayit.reduce((t, x) => t + (x.borc || 0), 0);
    const alacakT = h.kayit.reduce((t, x) => t + (x.alacak || 0), 0);
    k.innerHTML = tablo(["Tarih", "Evrak No", "Açıklama", "Borç", "Alacak", "Kaynak", "İşlem"],
      h.kayit.map((x) => [tarihKisa(x.tarih), x.evrak_no, x.aciklama,
      { hucre: x.borc ? para(x.borc) : "—", sinif: "para" }, { hucre: x.alacak ? para(x.alacak) : "—", sinif: "para paraPoz" }, x.kaynak,
      { hucre: `<button class="dugme kucuk" data-cr-duzenle="${x.id}">Düzenle</button>
                <button class="dugme kucuk kirmizi" data-cr-sil="${x.id}">Sil</button>` }]),
      { baslik: "Cari Hareketleri", yukseklik: "44vh", sagSutun: [3, 4],
        toplamlar: [["Toplam Borç", para(borcT)], ["Toplam Alacak", para(alacakT)], ["Bakiye", para(borcT - alacakT)]] })
      + `<div style="margin-top:10px;display:flex;gap:8px"><button class="dugme birincil" id="harYeni">+ Hareket Ekle</button>
         <button class="dugme" id="harExcel">Excel</button><button class="dugme" id="harWord">Word</button></div>`;
    $$("[data-cr-duzenle]").forEach((b) => (b.onclick = () => {
      const x = h.kayit.find((y) => y.id === Number(b.dataset.crDuzenle));
      if (x) hareketForm(c, x);
    }));
    $$("[data-cr-sil]").forEach((b) => (b.onclick = () => {
      const x = h.kayit.find((y) => y.id === Number(b.dataset.crSil));
      if (x) sil("hareket", x.id, (x.aciklama || "hareket") + " · " + para((x.borc || 0) + (x.alacak || 0)), () => cariDetayCiz());
    }));
    $("#harYeni").onclick = () => hareketForm(c);
    $("#harExcel").onclick = () => indir("/api/disa-aktar?kaynak=hareket&tur=xlsx");
    $("#harWord").onclick = () => indir("/api/disa-aktar?kaynak=hareket&tur=docx");
  } else if (cariSekme === 2) {
    const h = await api(`/api/hareket?cari_id=${c.id}`);
    const sirali = [...h.kayit].sort((a, b) => (a.tarih || "").localeCompare(b.tarih || ""));
    let yuruyen = Number(c.acilis_bakiye || 0);
    const satirlar = sirali.map((x) => {
      yuruyen += (x.borc || 0) - (x.alacak || 0);
      return [tarihKisa(x.tarih), x.evrak_no, x.aciklama,
        x.borc ? para(x.borc) : "", x.alacak ? para(x.alacak) : "",
        { hucre: `<b class="${yuruyen > 0 ? "paraPoz" : yuruyen < 0 ? "paraNeg" : ""}">${para(yuruyen)}</b>`, sinif: "para" }];
    });
    k.innerHTML = `<div class="kartNot" style="margin-bottom:9px">Açılış bakiyesi: <b>${para(c.acilis_bakiye)}</b> ·
      devreden bakiye: <b>${para(yuruyen)}</b></div>`
      + tablo(["Tarih", "Evrak", "Açıklama", "Borç", "Alacak", "Yürüyen Bakiye"], satirlar,
        { baslik: c.unvan + " · Ekstre", yukseklik: "46vh", sagSutun: [3, 4, 5] });
  } else if (cariSekme === 3) {
    const f = await api(`/api/fatura?cari_id=${c.id}`);
    k.innerHTML = tablo(["No", "Tür", "Tarih", "Vade", "Toplam", "Ödenen", "Kalan", "Durum"],
      f.kayit.map((x) => [x.no, x.tur, tarihKisa(x.tarih), tarihKisa(x.vade), { hucre: para(x.toplam), sinif: "para" },
      { hucre: para(x.tahsil), sinif: "para paraPoz" }, { hucre: para(x.toplam - x.tahsil), sinif: "para" },
      { hucre: `<span class="damga ${x.durum === "Ödendi" ? "yesil" : x.durum === "Kısmi" ? "altin" : "kirmizi"}">${x.durum}</span>` }]),
      { baslik: "Faturalar", sagSutun: [4, 5, 6] });
  } else if (cariSekme === 4) {
    const h = await api("/api/hesap");
    k.innerHTML = `<div class="izgara k2">
      <div class="kart yesil"><div class="kartEtiket">Tahsilat Gir</div>
        <div class="formIzgara" style="margin-top:10px">
          <div class="alan genis"><label>Tutar (₺)</label><input id="thTutar" type="number" step="0.01" placeholder="0,00"></div>
          <div class="alan"><label>Tarih</label><input id="thTarih" type="date" value="${bugunISO()}"></div>
          <div class="alan"><label>Hesap</label><select id="thHesap">${h.kayit.map((x) => `<option value="${x.id}">${KACT(x.ad)} — ${para(x.bakiye)}</option>`).join("")}</select></div>
          <div class="alan genis"><label>Açıklama</label><input id="thAck" placeholder="Nakit tahsilat"></div>
        </div>
        <button class="dugme yesil tam" id="thKaydet" style="margin-top:10px">Tahsilatı Kaydet</button></div>
      <div class="kart kirmizi"><div class="kartEtiket">Ödeme Yap</div>
        <div class="formIzgara" style="margin-top:10px">
          <div class="alan genis"><label>Tutar (₺)</label><input id="odTutar" type="number" step="0.01" placeholder="0,00"></div>
          <div class="alan"><label>Tarih</label><input id="odTarih" type="date" value="${bugunISO()}"></div>
          <div class="alan"><label>Hesap</label><select id="odHesap">${h.kayit.map((x) => `<option value="${x.id}">${KACT(x.ad)} — ${para(x.bakiye)}</option>`).join("")}</select></div>
          <div class="alan genis"><label>Açıklama</label><input id="odAck" placeholder="Ödeme"></div>
        </div>
        <button class="dugme kirmizi tam" id="odKaydet" style="margin-top:10px">Ödemeyi Kaydet</button></div>
    </div>`;
    const tablo_ = (tur) => async () => {
      const tutar = Number($(tur === "tahsilat" ? "#thTutar" : "#odTutar").value || 0);
      if (!tutar) return bildir("Tutar gir.", true);
      const govde = tur === "tahsilat"
        ? { cari_id: c.id, tarih: $("#thTarih").value, evrak_no: "TH-" + Date.now().toString().slice(-6), aciklama: $("#thAck").value || "Tahsilat", borc: 0, alacak: tutar, kaynak: "kasa", hesap_id: Number($("#thHesap").value) }
        : { cari_id: c.id, tarih: $("#odTarih").value, evrak_no: "OD-" + Date.now().toString().slice(-6), aciklama: $("#odAck").value || "Ödeme", borc: tutar, alacak: 0, kaynak: "kasa", hesap_id: Number($("#odHesap").value) };
      await api("/api/hareket/kaydet", govde);
      if (tur === "tahsilat") await api("/api/kasa-hareket/kaydet", { hesap_id: govde.hesap_id, tarih: govde.tarih, tur: "giriş", tutar, aciklama: govde.aciklama, cari_id: c.id, evrak_no: govde.evrak_no });
      else await api("/api/kasa-hareket/kaydet", { hesap_id: govde.hesap_id, tarih: govde.tarih, tur: "çıkış", tutar, aciklama: govde.aciklama, cari_id: c.id, evrak_no: govde.evrak_no });
      bildir(tur === "tahsilat" ? "Tahsilat kaydedildi" : "Ödeme kaydedildi");
      const d = await api("/api/cari"); DURUM.cariler = d.kayit;
      cariListeCiz($("#cariAra") ? $("#cariAra").value : ""); cariDetayCiz();
    };
    $("#thKaydet").onclick = tablo_("tahsilat");
    $("#odKaydet").onclick = tablo_("odeme");
  } else {
    k.innerHTML = `<div class="alan"><label>Cari Notu</label>
      <textarea id="cariNot" rows="6" style="width:100%;padding:11px;border-radius:14px;border:1px solid var(--cizgi);background:var(--kart2)">${KACT(c.notlar || "")}</textarea></div>
      <button class="dugme birincil" id="notKaydet" style="margin-top:10px">Notu Kaydet</button>`;
    $("#notKaydet").onclick = async () => {
      await api("/api/cari/kaydet", { ...c, notlar: $("#cariNot").value });
      bildir("Not kaydedildi");
      const d = await api("/api/cari"); DURUM.cariler = d.kayit; cariDetayCiz();
    };
  }
}

function alanlar(hedef, deger, genislikler) {
  return `<div class="formIzgara">${hedef.map((h) => {
    const ad = h.ad, anahtar = h.anahtar || ad;
    const deger_ = deger && deger[anahtar] != null ? deger[anahtar] : (h.varsayilan || "");
    const genis = (genislikler || []).includes(anahtar) || h.genis;
    let icerik;
    if (h.tur === "sec") icerik = `<select data-alan="${anahtar}">${(h.secenekler || []).map((s) => `<option value="${KACT(s)}" ${String(s) === String(deger_) ? "selected" : ""}>${KACT(s)}</option>`).join("")}</select>`;
    else if (h.tur === "coklu") icerik = `<textarea data-alan="${anahtar}" rows="3">${KACT(deger_)}</textarea>`;
    else icerik = `<input data-alan="${anahtar}" type="${h.tur || "text"}" step="0.01" value="${KACT(deger_)}" placeholder="${KACT(h.ipucu || "")}">`;
    return `<div class="alan ${genis ? "genis" : ""}"><label>${KACT(ad)}</label>${icerik}</div>`;
  }).join("")}</div>`;
}
function alanTopla() {
  const g = {};
  $$("[data-alan]", $("#modalGovde")).forEach((e) => {
    g[e.dataset.alan] = e.type === "number" ? Number(e.value || 0) : e.value;
  });
  return g;
}

const CARI_ALANLAR = [
  { ad: "Cari Kodu", anahtar: "kod", ipucu: "C-013" }, { ad: "Ünvan", anahtar: "unvan", ipucu: "Ad Soyad / Firma" },
  { ad: "Tip", anahtar: "tip", tur: "sec", secenekler: ["Müşteri", "Tedarikçi", "Personel", "Kurum", "Diğer"], varsayilan: "Müşteri" },
  { ad: "Yetkili Kişi", anahtar: "yetkili" }, { ad: "Telefon", anahtar: "telefon" },
  { ad: "E-posta", anahtar: "email" }, { ad: "Vergi Dairesi", anahtar: "vergi_dairesi" }, { ad: "Vergi / TC No", anahtar: "vergi_no" },
  { ad: "İl", anahtar: "il" }, { ad: "İlçe", anahtar: "ilce" },
  { ad: "Açılış Bakiyesi", anahtar: "acilis_bakiye", tur: "number" }, { ad: "Risk Limiti", anahtar: "risk_limiti", tur: "number" },
  { ad: "Adres", anahtar: "adres", genis: true }, { ad: "Notlar", anahtar: "notlar", tur: "coklu", genis: true },
];
function cariForm(c) {
  modalAc(c ? "Cari Kartı Düzenle" : "Yeni Cari Kartı", alanlar(CARI_ALANLAR, c), [
    { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
    { ad: "Kaydet", sinif: "birincil", tikla: async () => {
      const g = alanTopla();
      if (!g.unvan) return bildir("Ünvan zorunlu.", true);
      if (c) g.id = c.id;
      await api("/api/cari/kaydet", g);
      modalKapat(); bildir("Cari kaydedildi");
      const d = await api("/api/cari"); DURUM.cariler = d.kayit; cariListeCiz($("#cariAra") ? $("#cariAra").value : ""); cariDetayCiz();
      $("#rozetCari").textContent = d.toplam;
    } },
  ]);
}
async function hareketForm(c, kayit) {
  const h = await api("/api/hesap");
  const aln = [
    { ad: "Tarih", anahtar: "tarih", tur: "date", varsayilan: bugunISO() },
    { ad: "Evrak No", anahtar: "evrak_no" }, { ad: "Açıklama", anahtar: "aciklama" },
    { ad: "Borç (bize borçlanır)", anahtar: "borc", tur: "number" },
    { ad: "Alacak (tahsilat)", anahtar: "alacak", tur: "number" },
    { ad: "Kasa / Banka", anahtar: "hesap_id", tur: "sec", secenekler: h.kayit.map((x) => x.id), varsayilan: h.kayit[0] && h.kayit[0].id },
    { ad: "Kaynak", anahtar: "kaynak", tur: "sec", secenekler: ["elle", "kasa", "fatura", "banka", "diğer"], varsayilan: "elle" },
  ];
  modalAc(c.unvan + (kayit ? " · Hareketi Düzenle" : " · Hareket Ekle"),
    alanlar(aln, kayit || { tarih: bugunISO(), evrak_no: "HR-" + Date.now().toString().slice(-6) }), [
    { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
    { ad: "Kaydet", sinif: "birincil", tikla: async () => {
      const g = alanTopla();
      g.cari_id = c.id;
      g.hesap_id = Number(g.hesap_id);
      if (kayit) g.id = kayit.id;
      await api("/api/hareket/kaydet", g);
      modalKapat(); bildir(kayit ? "Hareket güncellendi" : "Hareket kaydedildi");
      const d = await api("/api/cari"); DURUM.cariler = d.kayit; cariListeCiz($("#cariAra") ? $("#cariAra").value : ""); cariDetayCiz();
    } },
  ]);
}

/* ---------------------------------------------------------- 3) GÖRÜŞMELER */
EKRANLAR.gorusme = async () => {
  const d = await api("/api/gorusme");
  const c = await api("/api/cari");
  $("#icerik").innerHTML = `
    <div class="izgara k4" style="margin-bottom:12px">
      <div class="kart turkuaz"><div class="kartEtiket">Toplam Görüşme</div><div class="kartDeger turkuaz">${d.kayit.length}</div></div>
      <div class="kart yesil"><div class="kartEtiket">Sonuçlanan</div><div class="kartDeger yesil">${d.kayit.filter((x) => x.sonuc === "Sonuçlandı").length}</div></div>
      <div class="kart altin"><div class="kartEtiket">Planlanan</div><div class="kartDeger altin">${d.kayit.filter((x) => x.durum === "Devam ediyor").length}</div></div>
      <div class="kart pembe"><div class="kartEtiket">Cari Kartı</div><div class="kartDeger pembe">${c.toplam}</div></div>
    </div>
    ${tablo(["Tarih", "Saat", "Cari", "Konu", "Sonuç", "Takip", "Durum", "İşlem"],
    d.kayit.map((x) => [tarihKisa(x.tarih), x.saat, x.unvan, x.konu, x.sonuc, x.takip,
    { hucre: `<span class="damga ${x.durum === "Tamamlandı" ? "yesil" : "altin"}">${KACT(x.durum)}</span>` },
    { hucre: `<button class="dugme kucuk" data-gor-duzenle="${x.id}">Düzenle</button>
              <button class="dugme kucuk kirmizi" data-gor-sil="${x.id}">Sil</button>` }]),
    { baslik: "Görüşme Kayıtları", yukseklik: "58vh" })}
    <div style="margin-top:12px;display:flex;gap:9px">
      <button class="dugme birincil" id="gorYeni">+ Yeni Görüşme</button>
      <button class="dugme" id="gorWord">Word</button><button class="dugme" id="gorExcel">Excel</button>
    </div>`;
  const aln = [
    { ad: "Cari", anahtar: "cari_id", tur: "sec", secenekler: c.kayit.map((x) => x.id) },
    { ad: "Tarih", anahtar: "tarih", tur: "date", varsayilan: bugunISO() },
    { ad: "Saat", anahtar: "saat", varsayilan: "10:00" },
    { ad: "Konu", anahtar: "konu", genis: true },
    { ad: "Sonuç", anahtar: "sonuc", tur: "sec", secenekler: ["Sonuçlandı", "Bekliyor", "İptal"] },
    { ad: "Durum", anahtar: "durum", tur: "sec", secenekler: ["Tamamlandı", "Devam ediyor"] },
    { ad: "Takip Notu", anahtar: "takip", genis: true },
  ];
  const gorForm = (kayit) => modalAc(kayit ? "Görüşmeyi Düzenle" : "Yeni Görüşme Kaydı",
    alanlar(aln, kayit || { tarih: bugunISO(), durum: "Devam ediyor" }), [
    { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
    { ad: "Kaydet", sinif: "birincil", tikla: async () => {
      const g = alanTopla();
      if (kayit) g.id = kayit.id;
      await api("/api/gorusme/kaydet", g); modalKapat(); bildir(kayit ? "Görüşme güncellendi" : "Görüşme kaydedildi"); ekranCiz("gorusme");
    } },
  ]);
  $("#gorYeni").onclick = () => gorForm(null);
  $$("[data-gor-duzenle]").forEach((b) => (b.onclick = () => {
    const x = d.kayit.find((y) => y.id === Number(b.dataset.gorDuzenle));
    if (x) gorForm(x);
  }));
  $$("[data-gor-sil]").forEach((b) => (b.onclick = () => {
    const x = d.kayit.find((y) => y.id === Number(b.dataset.gorSil));
    if (x) sil("gorusme", x.id, x.konu + " · " + (x.unvan || ""), () => ekranCiz("gorusme"));
  }));
  $("#gorWord").onclick = () => indir("/api/disa-aktar?kaynak=gorusme&tur=docx");
  $("#gorExcel").onclick = () => indir("/api/disa-aktar?kaynak=gorusme&tur=xlsx");
};

/* ---------------------------------------------------------- SADE HARCAMA DEFTERİ */
const HARCAMA_GIDER = ["Market", "Yemek & Kafe", "Yakıt", "Kira", "Elektrik & Su", "İnternet & Telefon",
  "Kıyafet", "Sağlık", "Eğitim", "Kuaför & Bakım", "Çocuk", "Diğer"];
const HARCAMA_GELIR = ["Maaş", "Ek İş", "Kira Geliri", "Satış", "Diğer Gelir"];
let harcamaTur = "gider";
let harcamaKat = "Market";
let harcamaFiltre = "hepsi";

function kategoriRengi(ad) {
  let h = 0;
  for (const ch of String(ad || "")) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return PALET[h % PALET.length];
}

function miniCubuk(seri) {
  if (!seri || !seri.length) return "";
  const G = 900, Y = 210, sol = 42, sag = 10, ust = 14, alt = 28;
  const icG = G - sol - sag, icY = Y - ust - alt;
  const enb = Math.max(1, ...seri.map((s) => Math.max(s.gelir, s.gider)));
  const yuk = (v) => ust + icY - (v / enb) * icY;
  const adim = icG / seri.length;
  const bw = Math.max(2.4, adim * 0.34);
  let h = [`<svg class="miniCubuk" viewBox="0 0 ${G} ${Y}" preserveAspectRatio="none">`];
  for (let i = 0; i <= 2; i++) {
    const y = ust + (icY / 2) * i;
    h.push(`<line x1="${sol}" y1="${y}" x2="${G - sag}" y2="${y}" stroke="currentColor" stroke-opacity=".12" stroke-dasharray="3 5"/>`);
    h.push(`<text x="${sol - 8}" y="${y + 4}" text-anchor="end" font-size="10.5" fill="currentColor" fill-opacity=".55">${sayi(Math.round(enb * (1 - i / 2)))}</text>`);
  }
  seri.forEach((s, i) => {
    const x = sol + i * adim + adim / 2;
    if (s.gider > 0) h.push(`<rect x="${x - bw}" y="${yuk(s.gider)}" width="${bw}" height="${ust + icY - yuk(s.gider)}" rx="2" fill="url(#gGider)"><title>${s.etiket} gider ${para(s.gider)}</title></rect>`);
    if (s.gelir > 0) h.push(`<rect x="${x}" y="${yuk(s.gelir)}" width="${bw}" height="${ust + icY - yuk(s.gelir)}" rx="2" fill="url(#gGelir)"><title>${s.etiket} gelir ${para(s.gelir)}</title></rect>`);
    if (i % 5 === 0 || i === seri.length - 1)
      h.push(`<text x="${x}" y="${Y - 10}" text-anchor="middle" font-size="10" fill="currentColor" fill-opacity=".6">${KACT(s.etiket)}</text>`);
  });
  h.push('<defs><linearGradient id="gGelir" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#34d399"/><stop offset="1" stop-color="#22d3ee"/></linearGradient><linearGradient id="gGider" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fb7185"/><stop offset="1" stop-color="#f472b6"/></linearGradient></defs>');
  h.push("</svg>");
  return h.join("");
}

function sayaclar(kok) {
  $$("[data-sayac]", kok || document).forEach((el) => {
    const hedef = Number(el.dataset.sayac || 0);
    const t0 = performance.now();
    const adim = (t) => {
      const o = Math.min(1, (t - t0) / 700);
      const yumus = 1 - Math.pow(1 - o, 3);
      el.textContent = para(hedef * yumus);
      if (o < 1) requestAnimationFrame(adim);
    };
    requestAnimationFrame(adim);
  });
}

function kartSayac(etiket, deger, renk, alt, ekSinif) {
  return `<div class="kart ${ekSinif || ""}"><div class="kartEtiket">${KACT(etiket)}</div>
    <div class="kartDeger ${renk}" data-sayac="${Number(deger || 0).toFixed(2)}">${para(0)}</div>
    <div class="kartAltYazi">${alt || ""}</div></div>`;
}

function harcamaFormu(kayit) {
  const t = kayit ? kayit.tur : harcamaTur;
  const katListe = t === "gelir" ? HARCAMA_GELIR : HARCAMA_GIDER;
  const secili = kayit ? kayit.kategori : harcamaKat;
  const ciz = () => {
    modalAc(kayit ? "Kaydı Düzenle" : (t === "gelir" ? "Gelir Ekle" : "Gider Ekle"), `
      <div class="formIzgara">
        <div class="alan genis"><label>Tür</label>
          <div class="turSec">
            <button type="button" class="turDugme gelir ${t === "gelir" ? "aktif" : ""}" data-tur="gelir">▲ GELİR</button>
            <button type="button" class="turDugme gider ${t === "gider" ? "aktif" : ""}" data-tur="gider">▼ GİDER</button>
          </div></div>
        <div class="alan"><label>Tutar (₺)</label>
          <input id="hTutar" type="number" step="0.01" value="${kayit ? kayit.tutar : ""}" placeholder="0,00"></div>
        <div class="alan"><label>Tarih</label>
          <input id="hTarih" type="date" value="${kayit ? kayit.tarih : bugunISO()}"></div>
        <div class="alan genis"><label>Açıklama</label>
          <input id="hAck" value="${kayit ? KACT(kayit.aciklama || "") : ""}" placeholder="Örn: haftalık market"></div>
        <div class="alan genis"><label>Kategori (renkli etiketlerden seç)</label>
          <div class="cipSar" id="hCip">${katListe.map((k) => `<span class="cip ${k === secili ? "aktif" : ""}" data-kat="${KACT(k)}">
            <i style="background:${kategoriRengi(k)}"></i>${KACT(k)}</span>`).join("")}</div></div>
      </div>`, [
      { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
      { ad: "Kaydet", sinif: "birincil", tikla: kaydet },
    ]);
    let tur = t, kat = secili;
    $$("[data-tur]").forEach((b) => (b.onclick = () => { tur = b.dataset.tur; modalKapat(); harcamaFormu(kayit ? { ...kayit, tur } : null); }));
    $$("#hCip .cip").forEach((c) => (c.onclick = () => { kat = c.dataset.kat; $$("#hCip .cip").forEach((x) => x.classList.toggle("aktif", x === c)); }));
    window.__harcamaSec = () => ({ tur, kat });
  };
  const kaydet = async () => {
    const { tur, kat } = window.__harcamaSec();
    const tutar = Number($("#hTutar").value || 0);
    if (!tutar) return bildir("Tutar gir.", true);
    const govde = {
      tarih: $("#hTarih").value, tur, kategori: kat,
      aciklama: $("#hAck").value || (tur === "gelir" ? "Gelir" : "Harcama"), tutar,
      defter: "sade", id: kayit ? kayit.id : undefined,
    };
    await api("/api/gelir-gider/kaydet", govde);
    modalKapat();
    bildir(kayit ? "Kayıt güncellendi" : (tur === "gelir" ? "Gelir eklendi" : "Gider eklendi"));
    ekranCiz("harcama");
  };
  ciz();
}

EKRANLAR.harcama = async () => {
  const d = await api("/api/harcama-ozet?gun=30");
  DURUM.harcama = d;
  const katListe = harcamaTur === "gelir" ? HARCAMA_GELIR : HARCAMA_GIDER;
  if (!katListe.includes(harcamaKat)) harcamaKat = katListe[0];
  const liste = (d.kayit || []).filter((k) => harcamaFiltre === "hepsi" || k.tur === harcamaFiltre);
  const net = d.donem_gelir - d.donem_gider;
  const katlar = (d.kategoriler || []).filter((k) => harcamaFiltre === "hepsi" || k.tur === harcamaFiltre);

  $("#icerik").innerHTML = `
    <div class="izgara k4" style="margin-bottom:13px">
      ${kartSayac("Bugünkü Gelir", d.bugun_gelir, "yesil", "sade defter (kurumsal değil)", "yesil")}
      ${kartSayac("Bugünkü Gider", d.bugun_gider, "kirmizi", "bugünkü harcamalar", "kirmizi")}
      ${kartSayac("Bu Ay Gelir", d.ay_gelir, "yesil", "ayın 1'inden bugüne", "yesil")}
      ${kartSayac("Bu Ay Gider", d.ay_gider, "pembe", "ayın 1'inden bugüne", "pembe")}
    </div>
    <div class="izgara k4" style="margin-bottom:13px">
      ${kartSayac("30 Günlük Net", net, net >= 0 ? "yesil" : "kirmizi", "gelir − gider", net >= 0 ? "yesil" : "kirmizi")}
      ${kartSayac("30 Gün Gelir", d.donem_gelir, "turkuaz", "", "turkuaz")}
      ${kartSayac("30 Gün Gider", d.donem_gider, "altin", "", "altin")}
      <div class="kart"><div class="kartEtiket">Kayıt Sayısı</div>
        <div class="kartDeger turkuaz" data-sayac="0">0</div>
        <div class="kartAltYazi">sade defterde toplam ${d.kayit_sayisi} kayıt</div></div>
    </div>

    <div class="kart" style="margin-bottom:13px">
      <div class="kartUst"><h3>Hızlı Kayıt · ${harcamaTur === "gelir" ? "GELİR EKLE" : "GİDER EKLE"}</h3>
        <span class="damga turkuaz">tek tıkla deftere işle</span></div>
      <div class="hizliForm">
        <div class="alan" style="margin:0"><label>Tür</label>
          <div class="turSec">
            <button type="button" class="turDugme gelir ${harcamaTur === "gelir" ? "aktif" : ""}" id="hizliGelir">▲ GELİR EKLE</button>
            <button type="button" class="turDugme gider ${harcamaTur === "gider" ? "aktif" : ""}" id="hizliGider">▼ GİDER EKLE</button>
          </div></div>
        <div class="alan" style="margin:0"><label>Tutar (₺)</label><input id="hizliTutar" type="number" step="0.01" placeholder="0,00"></div>
        <div class="alan" style="margin:0"><label>Tarih</label><input id="hizliTarih" type="date" value="${bugunISO()}"></div>
        <div class="alan" style="margin:0"><label>Açıklama</label><input id="hizliAck" placeholder="isteğe bağlı"></div>
        <div class="alan" style="margin:0"><label>&nbsp;</label>
          <button class="dugme birincil tam" id="hizliKaydet">DEFTERE EKLE</button></div>
      </div>
      <div style="margin-top:10px"><label class="kartEtiket">Kategori</label>
        <div class="cipSar" id="hizliCip">${katListe.map((k) => `<span class="cip ${k === harcamaKat ? "aktif" : ""}" data-kat="${KACT(k)}">
          <i style="background:${kategoriRengi(k)}"></i>${KACT(k)}</span>`).join("")}</div></div>
    </div>

    <div class="izgara k3" style="margin-bottom:13px">
      <div class="kart" style="grid-column:span 2">
        <div class="kartUst"><h3>Son 30 Gün · Gelir / Gider</h3>
          <span class="kartNot">yeşil = gelir · pembe = gider</span></div>
        ${miniCubuk(d.seri)}</div>
      <div class="kart"><div class="kartUst"><h3>Kategori Dağılımı</h3></div>
        ${halkaGrafik(katlar.map((k) => ({ ad: k.ad + " (" + (k.tur === "gelir" ? "+" : "−") + ")", tutar: k.tutar })))}</div>
    </div>

    <div class="sekmeler" style="margin-bottom:10px">
      ${[["hepsi", "Tümü (" + (d.kayit || []).length + ")"], ["gelir", "Yalnızca Gelir"], ["gider", "Yalnızca Gider"]]
      .map(([id, ad]) => `<button class="sekme ${harcamaFiltre === id ? "aktif" : ""}" data-hf="${id}">${ad}</button>`).join("")}
      <button class="dugme kucuk" id="harcamaYeni" style="margin-left:auto">+ Yeni Kayıt</button>
      <button class="dugme kucuk" id="harcamaWord">Word</button>
      <button class="dugme kucuk" id="harcamaExcel">Excel</button>
    </div>

    ${tablo(["Tarih", "Tür", "Kategori", "Açıklama", "Tutar", "İşlem"],
    liste.slice(0, 150).map((k) => [
      tarihKisa(k.tarih),
      { hucre: `<span class="damga ${k.tur === "gelir" ? "yesil" : "kirmizi"}">${k.tur === "gelir" ? "▲ GELİR" : "▼ GİDER"}</span>` },
      { hucre: `<span class="satirRenk" style="background:${kategoriRengi(k.kategori)}"></span>${KACT(k.kategori)}` },
      KACT(k.aciklama),
      { hucre: `<b class="${k.tur === "gelir" ? "paraPoz" : "paraNeg"}">${k.tur === "gelir" ? "+" : "−"}${para(k.tutar)}</b>`, sinif: "para" },
      { hucre: `<button class="dugme kucuk" data-har-duzenle="${k.id}">Düzenle</button>
                <button class="dugme kucuk kirmizi" data-har-sil="${k.id}">Sil</button>` },
    ]), {
      baslik: "Sade Harcama Defteri", yukseklik: "42vh", sagSutun: [4],
      toplamlar: [["Kayıt", liste.length], ["Gelir", para(liste.filter((k) => k.tur === "gelir").reduce((t, k) => t + k.tutar, 0))],
      ["Gider", para(liste.filter((k) => k.tur === "gider").reduce((t, k) => t + k.tutar, 0))],
      ["Net", para(liste.filter((k) => k.tur === "gelir").reduce((t, k) => t + k.tutar, 0) - liste.filter((k) => k.tur === "gider").reduce((t, k) => t + k.tutar, 0))]],
    })}`;

  $$("[data-hf]").forEach((b) => (b.onclick = () => { harcamaFiltre = b.dataset.hf; ekranCiz("harcama"); }));
  $("#hizliGelir").onclick = () => { harcamaTur = "gelir"; harcamaKat = "Maaş"; ekranCiz("harcama"); };
  $("#hizliGider").onclick = () => { harcamaTur = "gider"; harcamaKat = "Market"; ekranCiz("harcama"); };
  $$("#hizliCip .cip").forEach((c) => (c.onclick = () => {
    harcamaKat = c.dataset.kat;
    $$("#hizliCip .cip").forEach((x) => x.classList.toggle("aktif", x === c));
  }));
  const hizliKaydet = async () => {
    const tutar = Number($("#hizliTutar").value || 0);
    if (!tutar) return bildir("Tutar yaz, sonra deftere ekle.", true);
    await api("/api/gelir-gider/kaydet", {
      tarih: $("#hizliTarih").value, tur: harcamaTur, kategori: harcamaKat,
      aciklama: $("#hizliAck").value || (harcamaTur === "gelir" ? "Gelir" : "Harcama"),
      tutar, defter: "sade",
    });
    bildir((harcamaTur === "gelir" ? "Gelir" : "Gider") + " deftere eklendi · " + para(tutar));
    ekranCiz("harcama");
  };
  $("#hizliKaydet").onclick = hizliKaydet;
  $("#hizliTutar").onkeydown = (e) => { if (e.key === "Enter") hizliKaydet(); };
  $("#harcamaYeni").onclick = () => harcamaFormu(null);
  $("#harcamaWord").onclick = () => indir("/api/disa-aktar?kaynak=harcama&tur=docx");
  $("#harcamaExcel").onclick = () => indir("/api/disa-aktar?kaynak=harcama&tur=xlsx");
  $$("[data-har-duzenle]").forEach((b) => (b.onclick = () => {
    const k = (d.kayit || []).find((x) => x.id === Number(b.dataset.harDuzenle));
    harcamaFormu(k);
  }));
  $$("[data-har-sil]").forEach((b) => (b.onclick = () => {
    const k = (d.kayit || []).find((x) => x.id === Number(b.dataset.harSil));
    sil("gelir_gider", k.id, (k.tur === "gelir" ? "Gelir" : "Gider") + " · " + para(k.tutar) + " · " + k.kategori, () => ekranCiz("harcama"));
  }));
};

/* ---------------------------------------------------------- 4-5) GELİR / GİDER */
function gelirGiderEkrani(tur) {
  return async () => {
    const d = await api(`/api/gelir-gider?tur=${tur}&defter=kurumsal`);
    const h = await api("/api/hesap");
    const duzenle = (k) => {
      const aln2 = [
        { ad: "Tarih", anahtar: "tarih", tur: "date" },
        { ad: "Kategori", anahtar: "kategori", tur: "sec", secenekler: katSecenekler },
        { ad: "Açıklama", anahtar: "aciklama", genis: true },
        { ad: "Tutar (₺)", anahtar: "tutar", tur: "number" },
        { ad: "Kasa / Banka", anahtar: "hesap_id", tur: "sec", secenekler: h.kayit.map((x) => x.id) },
        { ad: "Evrak No", anahtar: "evrak_no" },
      ];
      modalAc("Kaydı Düzenle", alanlar(aln2, { ...k, hesap_id: k.hesap_id || (h.kayit[0] && h.kayit[0].id) }), [
        { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
        { ad: "Kaydet", sinif: "birincil", tikla: async () => {
          const g = alanTopla();
          g.id = k.id; g.tur = tur; g.defter = "kurumsal"; g.hesap_id = Number(g.hesap_id);
          await api("/api/gelir-gider/kaydet", g);
          modalKapat(); bildir("Kayıt güncellendi"); ekranCiz(tur);
        } },
      ]);
    };
    const katSecenekler = tur === "gelir"
      ? ["Kuaför Hizmet", "Ürün Satışı", "Bakım & Boya", "Gelin Paketi", "Diğer Gelir"]
      : ["Personel", "Kira", "Elektrik & Su", "Malzeme Alımı", "Vergi & Harç", "Reklam", "İnternet & Telefon", "Diğer Gider"];
    const toplam = d.kayit.reduce((t, x) => t + (x.tutar || 0), 0);
    const katToplam = {};
    d.kayit.forEach((x) => { katToplam[x.kategori || "Diğer"] = (katToplam[x.kategori || "Diğer"] || 0) + (x.tutar || 0); });
    const kategoriler = Object.entries(katToplam).sort((a, b) => b[1] - a[1]).map(([ad, tutar]) => ({ ad, tutar }));
    $("#icerik").innerHTML = `
      <div class="izgara k3" style="margin-bottom:12px">
        <div class="kart ${tur === "gelir" ? "yesil" : "pembe"}"><div class="kartEtiket">Toplam ${tur === "gelir" ? "Gelir" : "Gider"}</div>
          <div class="kartDeger ${tur === "gelir" ? "yesil" : "pembe"}">${para(toplam)}</div>
          <div class="kartAltYazi">${d.kayit.length} kayıt</div></div>
        <div class="kart"><div class="kartEtiket">En Büyük Kalem</div>
          <div class="kartDeger turkuaz">${para(kategoriler[0] ? kategoriler[0].tutar : 0)}</div>
          <div class="kartAltYazi">${KACT(kategoriler[0] ? kategoriler[0].ad : "—")}</div></div>
        <div class="kart altin"><div class="kartEtiket">Ortalama İşlem</div>
          <div class="kartDeger altin">${para(d.kayit.length ? toplam / d.kayit.length : 0)}</div>
          <div class="kartAltYazi">kayıt başına</div></div>
      </div>
      <div class="izgara k2" style="margin-bottom:12px">
        <div class="kart"><div class="kartUst"><h3>Kategori Dağılımı</h3></div>${halkaGrafik(kategoriler)}</div>
        <div class="kart"><div class="kartUst"><h3>${tur === "gelir" ? "Gelir" : "Gider"} Defteri</h3>
          <span class="kartNot">son ${Math.min(60, d.kayit.length)} kayıt</span></div>
          <table><thead><tr><th>Tarih</th><th>Kategori</th><th>Açıklama</th><th class="sayi">Tutar</th><th>Hesap</th><th class="sayi">İşlem</th></tr></thead><tbody>
          ${d.kayit.slice(0, 60).map((x) => `<tr><td>${tarihKisa(x.tarih)}</td>
            <td><span class="satirRenk" style="background:${kategoriRengi(x.kategori)}"></span>${KACT(x.kategori)}</td>
            <td>${KACT(x.aciklama)}</td><td class="para ${tur === "gelir" ? "paraPoz" : "paraNeg"}">${para(x.tutar)}</td>
            <td>${KACT(x.hesap || "—")}</td>
            <td class="sayi"><button class="dugme kucuk" data-gg-duzenle="${x.id}">Düzenle</button>
            <button class="dugme kucuk kirmizi" data-gg-sil="${x.id}">Sil</button></td></tr>`).join("")}
          </tbody></table></div>
      </div>
      <div style="display:flex;gap:9px;flex-wrap:wrap">
        <button class="dugme birincil" id="ggYeni">+ Yeni ${tur === "gelir" ? "Gelir" : "Gider"}</button>
        <button class="dugme" id="ggWord">Word</button><button class="dugme" id="ggExcel">Excel</button>
      </div>`;
    const katOn = tur === "gelir"
      ? ["Kuaför Hizmet", "Ürün Satışı", "Bakım & Boya", "Gelin Paketi", "Diğer Gelir"]
      : ["Personel", "Kira", "Elektrik & Su", "Malzeme Alımı", "Vergi & Harç", "Reklam", "İnternet & Telefon", "Diğer Gider"];
    const aln = [
      { ad: "Tarih", anahtar: "tarih", tur: "date", varsayilan: bugunISO() },
      { ad: "Kategori", anahtar: "kategori", tur: "sec", secenekler: katOn },
      { ad: "Açıklama", anahtar: "aciklama", genis: true },
      { ad: "Tutar (₺)", anahtar: "tutar", tur: "number" },
      { ad: "Kasa / Banka", anahtar: "hesap_id", tur: "sec", secenekler: h.kayit.map((x) => x.id) },
      { ad: "Evrak No", anahtar: "evrak_no" },
    ];
    $("#ggYeni").onclick = () => modalAc(`Yeni ${tur === "gelir" ? "Gelir" : "Gider"} Kaydı`,
      alanlar(aln, { tarih: bugunISO(), hesap_id: h.kayit[0] && h.kayit[0].id }), [
      { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
      { ad: "Kaydet", sinif: "birincil", tikla: async () => {
        const g = alanTopla();
        if (!g.tutar) return bildir("Tutar gir.", true);
        g.tur = tur; g.hesap_id = Number(g.hesap_id);
        await api("/api/gelir-gider/kaydet", g);
        modalKapat(); bildir("Kayıt eklendi · kasa hareketine de işlendi"); ekranCiz(tur);
      } },
    ]);
    $("#ggWord").onclick = () => indir(`/api/disa-aktar?kaynak=gelir-gider&tur=docx`);
    $("#ggExcel").onclick = () => indir(`/api/disa-aktar?kaynak=gelir-gider&tur=xlsx`);
    $$("[data-gg-duzenle]").forEach((b) => (b.onclick = () => {
      const k = d.kayit.find((x) => x.id === Number(b.dataset.ggDuzenle));
      if (k) duzenle(k);
    }));
    $$("[data-gg-sil]").forEach((b) => (b.onclick = () => {
      const k = d.kayit.find((x) => x.id === Number(b.dataset.ggSil));
      if (k) sil("gelir_gider", k.id, k.kategori + " · " + para(k.tutar) + " · " + tarihKisa(k.tarih), () => ekranCiz(tur));
    }));
  };
}
EKRANLAR.gelir = gelirGiderEkrani("gelir");
EKRANLAR.gider = gelirGiderEkrani("gider");

/* ---------------------------------------------------------- 6) KASA & BANKALAR */
let kasaSekme = 0;
EKRANLAR.kasa = async () => {
  const d = await api("/api/hesap");
  DURUM.hesaplar = d.kayit;
  if (!DURUM.hesap_id && d.kayit.length) DURUM.hesap_id = d.kayit[0].id;
  const sekmeler = ["Hesaplar", "Hareketler", "Gün Sonu"];
  $("#icerik").innerHTML = `
    <div class="izgara k3" style="margin-bottom:12px">
      <div class="kart altin"><div class="kartEtiket">Kasa Toplamı</div><div class="kartDeger altin">${para(d.kasa)}</div></div>
      <div class="kart turkuaz"><div class="kartEtiket">Banka Toplamı</div><div class="kartDeger turkuaz">${para(d.banka)}</div></div>
      <div class="kart yesil"><div class="kartEtiket">Genel Toplam</div><div class="kartDeger yesil">${para(d.kasa + d.banka)}</div></div>
    </div>
    <div class="sekmeler">${sekmeler.map((s, i) => `<button class="sekme ${i === kasaSekme ? "aktif" : ""}" data-ks="${i}">${s}</button>`).join("")}</div>
    <div id="kasaIcerik"></div>`;
  $$("[data-ks]").forEach((b) => (b.onclick = () => { kasaSekme = Number(b.dataset.ks); ekranCiz("kasa"); }));
  const k = $("#kasaIcerik");
  if (kasaSekme === 0) {
    k.innerHTML = `<div class="izgara k3">${d.kayit.map((h) => `
      <div class="kart ${h.tur === "Banka" ? "turkuaz" : "altin"}">
        <div class="kartUst"><h3>${KACT(h.ad)}</h3><span class="damga ${h.tur === "Banka" ? "turkuaz" : "altin"}">${KACT(h.tur)}</span></div>
        <div class="kartDeger ${h.bakiye < 0 ? "kirmizi" : "yesil"}">${para(h.bakiye)}</div>
        <div class="kartAltYazi">${KACT(h.banka || "Kasa")} ${h.iban ? "· " + KACT(h.iban) : ""}</div>
        <div style="display:flex;gap:7px;margin-top:10px">
          <button class="dugme kucuk" data-hesap-sec="${h.id}">Hareketler</button>
          <button class="dugme kucuk" data-hesap-duzenle="${h.id}">Düzenle</button>
          <button class="dugme kucuk kirmizi" data-hesap-sil="${h.id}">Sil</button></div>
      </div>`).join("")}</div>
      <div style="margin-top:12px;display:flex;gap:9px">
        <button class="dugme birincil" id="hesapYeni">+ Yeni Kasa / Banka Hesabı</button>
        <button class="dugme" id="hesapWord">Word</button><button class="dugme" id="hesapExcel">Excel</button>
      </div>`;
    $$("[data-hesap-sec]").forEach((b) => (b.onclick = () => { DURUM.hesap_id = Number(b.dataset.hesapSec); kasaSekme = 1; ekranCiz("kasa"); }));
    $$("[data-hesap-duzenle]").forEach((b) => (b.onclick = () => hesapForm(d.kayit.find((x) => x.id === Number(b.dataset.hesapDuzenle)))));
    $$("[data-hesap-sil]").forEach((b) => (b.onclick = () => { const h = d.kayit.find((x) => x.id === Number(b.dataset.hesapSil)); sil("hesap", h.id, h.ad, () => ekranCiz("kasa")); }));
    $("#hesapYeni").onclick = () => hesapForm(null);
    $("#hesapWord").onclick = () => indir("/api/disa-aktar?kaynak=hesap&tur=docx");
    $("#hesapExcel").onclick = () => indir("/api/disa-aktar?kaynak=hesap&tur=xlsx");
  } else if (kasaSekme === 1) {
    const hz = await api(`/api/kasa-hareket?hesap_id=${DURUM.hesap_id}`);
    const gir = hz.kayit.filter((x) => x.tur === "giriş").reduce((t, x) => t + x.tutar, 0);
    const cik = hz.kayit.filter((x) => x.tur === "çıkış").reduce((t, x) => t + x.tutar, 0);
    k.innerHTML = `<div class="alan" style="max-width:340px"><label>Hesap Seç</label>
      <select id="khHesap">${d.kayit.map((h) => `<option value="${h.id}" ${h.id === DURUM.hesap_id ? "selected" : ""}>${KACT(h.ad)} — ${para(h.bakiye)}</option>`).join("")}</select></div>`
      + tablo(["Tarih", "Tür", "Tutar", "Açıklama", "Kategori", "Evrak", "İşlem"],
        hz.kayit.map((x) => [tarihKisa(x.tarih), x.tur, { hucre: para(x.tutar), sinif: "para " + (x.tur === "giriş" ? "paraPoz" : "paraNeg") }, x.aciklama, x.kategori, x.evrak_no,
        { hucre: `<button class="dugme kucuk" data-kh-duzenle="${x.id}">Düzenle</button>
                  <button class="dugme kucuk kirmizi" data-kh-sil="${x.id}">Sil</button>` }]),
        { baslik: "Kasa Hareketleri", yukseklik: "48vh", sagSutun: [2],
          toplamlar: [["Giriş", para(gir)], ["Çıkış", para(cik)], ["Net", para(gir - cik)]] })
      + `<div style="margin-top:12px;display:flex;gap:9px"><button class="dugme birincil" id="khYeni">+ Hareket Ekle</button>
         <button class="dugme" id="khExcel">Excel</button></div>`;
    const khForm = (kayit) => modalAc(kayit ? "Kasa Hareketini Düzenle" : "Kasa Hareketi Ekle", alanlar([
      { ad: "Tarih", anahtar: "tarih", tur: "date" },
      { ad: "Tür", anahtar: "tur", tur: "sec", secenekler: ["giriş", "çıkış"] },
      { ad: "Tutar (₺)", anahtar: "tutar", tur: "number" },
      { ad: "Açıklama", anahtar: "aciklama", genis: true },
      { ad: "Kategori", anahtar: "kategori" }, { ad: "Evrak No", anahtar: "evrak_no" },
    ], kayit || { tarih: bugunISO(), tur: "giriş" }), [
      { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
      { ad: "Kaydet", sinif: "birincil", tikla: async () => {
        const g = alanTopla();
        g.hesap_id = kayit ? kayit.hesap_id : DURUM.hesap_id;
        if (kayit) g.id = kayit.id;
        await api("/api/kasa-hareket/kaydet", g); modalKapat(); bildir("Hareket kaydedildi"); ekranCiz("kasa");
      } },
    ]);
    $("#khHesap").onchange = () => { DURUM.hesap_id = Number($("#khHesap").value); ekranCiz("kasa"); };
    $("#khYeni").onclick = () => khForm(null);
    $$("[data-kh-duzenle]").forEach((b) => (b.onclick = () => {
      const x = hz.kayit.find((y) => y.id === Number(b.dataset.khDuzenle));
      if (x) khForm(x);
    }));
    $$("[data-kh-sil]").forEach((b) => (b.onclick = () => {
      const x = hz.kayit.find((y) => y.id === Number(b.dataset.khSil));
      if (x) sil("kasa_hareket", x.id, x.tur + " · " + para(x.tutar) + " · " + (x.aciklama || ""), () => ekranCiz("kasa"));
    }));
    $("#khExcel").onclick = () => indir("/api/disa-aktar?kaynak=kasa-hareket&tur=xlsx");
  } else {
    const h = d.kayit.find((x) => x.id === DURUM.hesap_id) || d.kayit[0];
    const hz = await api(`/api/kasa-hareket?hesap_id=${h.id}`);
    const bug = hz.kayit.filter((x) => x.tarih === bugunISO());
    const gir = bug.filter((x) => x.tur === "giriş").reduce((t, x) => t + x.tutar, 0);
    const cik = bug.filter((x) => x.tur === "çıkış").reduce((t, x) => t + x.tutar, 0);
    k.innerHTML = `<div class="izgara k2">
      <div class="kart altin"><div class="kartEtiket">Bugünün Kasası · ${KACT(h.ad)}</div>
        <div class="kartDeger altin">${para(h.acilis + gir - cik)}</div>
        <div class="kartAltYazi">Açılış: ${para(h.acilis)}</div>
        <div style="margin-top:12px">
          <div class="halkaSatir"><span>Bugünkü giriş</span><b class="paraPoz">${para(gir)}</b></div>
          <div class="halkaSatir"><span>Bugünkü çıkış</span><b class="paraNeg">${para(cik)}</b></div>
          <div class="halkaSatir"><span>Net</span><b>${para(gir - cik)}</b></div>
          <div class="halkaSatir"><span>Hareket sayısı</span><b>${bug.length}</b></div>
        </div></div>
      <div class="kart"><div class="kartUst"><h3>Bugünün Hareketleri</h3></div>
        <table><thead><tr><th>Saat</th><th>Tür</th><th class="sayi">Tutar</th><th>Açıklama</th></tr></thead><tbody>
        ${bug.map((x) => `<tr><td>${KACT((x.olusturma || "").slice(11, 16))}</td><td>${x.tur}</td>
          <td class="para ${x.tur === "giriş" ? "paraPoz" : "paraNeg"}">${para(x.tutar)}</td><td>${KACT(x.aciklama)}</td></tr>`).join("")
      || '<tr><td colspan="4"><div class="bos">Bugün hareket yok</div></td></tr>'}
        </tbody></table></div>
    </div>`;
  }
};

const HESAP_ALANLAR = [
  { ad: "Hesap Adı", anahtar: "ad", genis: true },
  { ad: "Tür", anahtar: "tur", tur: "sec", secenekler: ["Kasa", "Banka"], varsayilan: "Kasa" },
  { ad: "Banka", anahtar: "banka" }, { ad: "Şube", anahtar: "sube" },
  { ad: "IBAN", anahtar: "iban", genis: true },
  { ad: "Açılış Bakiyesi", anahtar: "acilis", tur: "number" },
];
function hesapForm(h) {
  modalAc(h ? "Hesap Düzenle" : "Yeni Kasa / Banka Hesabı", alanlar(HESAP_ALANLAR, h), [
    { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
    { ad: "Kaydet", sinif: "birincil", tikla: async () => {
      const g = alanTopla(); if (h) g.id = h.id;
      await api("/api/hesap/kaydet", g); modalKapat(); bildir("Hesap kaydedildi"); ekranCiz("kasa");
    } },
  ]);
}

/* ---------------------------------------------------------- 7) FATURALAR */
let faturaSekme = "Satış";
EKRANLAR.fatura = async () => {
  const d = await api("/api/fatura");
  const c = await api("/api/cari");
  const satis = d.kayit.filter((x) => x.tur === "Satış");
  const alis = d.kayit.filter((x) => x.tur === "Alış");
  $("#icerik").innerHTML = `
    <div class="izgara k4" style="margin-bottom:12px">
      <div class="kart yesil"><div class="kartEtiket">Satış Faturaları</div>
        <div class="kartDeger yesil">${para(satis.reduce((t, x) => t + x.toplam, 0))}</div><div class="kartAltYazi">${satis.length} fatura</div></div>
      <div class="kart pembe"><div class="kartEtiket">Alış Faturaları</div>
        <div class="kartDeger pembe">${para(alis.reduce((t, x) => t + x.toplam, 0))}</div><div class="kartAltYazi">${alis.length} fatura</div></div>
      <div class="kart altin"><div class="kartEtiket">Tahsil Edilen</div>
        <div class="kartDeger altin">${para(d.kayit.reduce((t, x) => t + x.tahsil, 0))}</div></div>
      <div class="kart kirmizi"><div class="kartEtiket">Bekleyen Bakiye</div>
        <div class="kartDeger kirmizi">${para(d.kayit.reduce((t, x) => t + (x.toplam - x.tahsil), 0))}</div></div>
    </div>
    <div class="sekmeler">${["Satış", "Alış", "Tümü"].map((s) => `<button class="sekme ${s === faturaSekme ? "aktif" : ""}" data-fs="${s}">${s}</button>`).join("")}</div>
    <div id="faturaListe"></div>
    <div style="margin-top:12px;display:flex;gap:9px;flex-wrap:wrap">
      <button class="dugme birincil" id="fatYeni">+ Yeni Fatura</button>
      <button class="dugme" id="fatWord">Word</button><button class="dugme" id="fatExcel">Excel</button></div>`;
  const goster = faturaSekme === "Tümü" ? d.kayit : d.kayit.filter((x) => x.tur === faturaSekme);
  $("#faturaListe").innerHTML = tablo(["No", "Tür", "Cari", "Tarih", "Vade", "Matrah", "KDV", "Toplam", "Ödenen", "Durum", "İşlem"],
    goster.map((x) => [x.no, x.tur, x.unvan, tarihKisa(x.tarih), tarihKisa(x.vade),
    { hucre: para(x.ara_toplam), sinif: "para" }, { hucre: para(x.kdv), sinif: "para" },
    { hucre: "<b>" + para(x.toplam) + "</b>", sinif: "para" }, { hucre: para(x.tahsil), sinif: "para paraPoz" },
    { hucre: `<span class="damga ${x.durum === "Ödendi" ? "yesil" : x.durum === "Kısmi" ? "altin" : "kirmizi"}">${x.durum}</span>` },
    { hucre: `<button class="dugme kucuk" data-fat-gor="${x.id}">Gör</button> <button class="dugme kucuk kirmizi" data-fat-sil="${x.id}">Sil</button>` }]),
    { baslik: "Fatura Listesi", yukseklik: "46vh", sagSutun: [5, 6, 7, 8] });
  $$("[data-fs]").forEach((b) => (b.onclick = () => { faturaSekme = b.dataset.fs; ekranCiz("fatura"); }));
  $$("[data-fat-gor]").forEach((b) => (b.onclick = () => faturaGor(Number(b.dataset.fatGor))));
  $$("[data-fat-sil]").forEach((b) => (b.onclick = () => sil("fatura", Number(b.dataset.fatSil), "fatura", () => ekranCiz("fatura"))));
  $("#fatYeni").onclick = () => faturaForm(null, c.kayit);
  $("#fatWord").onclick = () => indir("/api/disa-aktar?kaynak=fatura&tur=docx");
  $("#fatExcel").onclick = () => indir("/api/disa-aktar?kaynak=fatura&tur=xlsx");
};

async function faturaGor(id) {
  const d = await api("/api/fatura-detay?id=" + id);
  const f = d.fatura;
  if (!f) return bildir("Fatura bulunamadı", true);
  modalAc(`Fatura ${f.no} · ${f.tur}`, `
    <div class="izgara k2" style="margin-bottom:12px">
      <div><div class="halkaSatir"><span>Cari</span><b>${KACT(f.unvan || "")}</b></div>
        <div class="halkaSatir"><span>Tarih</span><b>${tarihKisa(f.tarih)}</b></div>
        <div class="halkaSatir"><span>Vade</span><b>${tarihKisa(f.vade)}</b></div></div>
      <div><div class="halkaSatir"><span>Matrah</span><b>${para(f.ara_toplam)}</b></div>
        <div class="halkaSatir"><span>KDV</span><b>${para(f.kdv)}</b></div>
        <div class="halkaSatir"><span>Toplam</span><b>${para(f.toplam)}</b></div></div>
    </div>
    ${tablo(["Açıklama", "Miktar", "Birim", "Birim Fiyat", "KDV %", "Tutar"],
    d.kalem.map((k) => [k.aciklama, sayi(k.miktar), k.birim, { hucre: para(k.birim_fiyat), sinif: "para" }, sayi(k.kdv_orani), { hucre: para(k.tutar), sinif: "para" }]),
    { baslik: "Fatura Kalemleri", sagSutun: [3, 5], toplamlar: [["TOPLAM", para(f.toplam)]] })}`,
    [{ ad: "Kapat", sinif: "birincil", tikla: modalKapat }]);
}

async function faturaForm(f, cariler) {
  const kalemler = f ? (await api("/api/fatura-detay?id=" + f.id)).kalem : [{ aciklama: "", miktar: 1, birim: "Adet", birim_fiyat: 0, kdv_orani: 20 }];
  const ciz = () => {
    modalAc(f ? "Fatura Düzenle" : "Yeni Fatura", `
      <div class="formIzgara">
        <div class="alan"><label>Fatura No</label><input id="fNo" value="${KACT(f ? f.no : "")}" placeholder="boşsa otomatik"></div>
        <div class="alan"><label>Tür</label><select id="fTur">${["Satış", "Alış"].map((t) => `<option ${f && f.tur === t ? "selected" : ""}>${t}</option>`).join("")}</select></div>
        <div class="alan genis"><label>Cari</label><select id="fCari">${cariler.map((c) => `<option value="${c.id}" ${f && f.cari_id === c.id ? "selected" : ""}>${KACT(c.unvan)}</option>`).join("")}</select></div>
        <div class="alan"><label>Tarih</label><input id="fTarih" type="date" value="${f ? f.tarih : bugunISO()}"></div>
        <div class="alan"><label>Vade</label><input id="fVade" type="date" value="${f ? f.vade : bugunISO()}"></div>
        <div class="alan"><label>Durum</label><select id="fDurum">${["Bekliyor", "Kısmi", "Ödendi"].map((t) => `<option ${f && f.durum === t ? "selected" : ""}>${t}</option>`).join("")}</select></div>
        <div class="alan"><label>İskonto (₺)</label><input id="fIsk" type="number" step="0.01" value="${f ? f.iskonto : 0}"></div>
        <div class="alan genis"><label>Açıklama</label><input id="fAck" value="${KACT(f ? f.aciklama : "")}"></div>
      </div>
      <div class="kartUst" style="margin-top:14px"><h3>Fatura Kalemleri</h3>
        <button class="dugme kucuk" id="kalemEkle">+ Kalem</button></div>
      <div id="kalemler"></div>
      <div class="tabloToplam" id="fToplam"></div>`, [
      { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
      { ad: "Kaydet", sinif: "birincil", tikla: kaydet },
    ]);
    kalemCiz();
  };
  const kalemCiz = () => {
    $("#kalemler").innerHTML = kalemler.map((k, i) => `
      <div class="kalemSatir" data-kalem="${i}">
        <input data-k="aciklama" value="${KACT(k.aciklama)}" placeholder="Açıklama">
        <input data-k="miktar" type="number" step="0.01" value="${k.miktar}" placeholder="Miktar" title="Miktar">
        <input data-k="birim_fiyat" type="number" step="0.01" value="${k.birim_fiyat}" placeholder="Birim fiyat" title="Birim fiyat">
        <input data-k="kdv_orani" type="number" step="1" value="${k.kdv_orani}" placeholder="KDV %" title="KDV %">
        <button class="dugme kucuk kirmizi" data-k-sil="${i}">Sil</button>
      </div>`).join("");
    $$("[data-k-sil]").forEach((b) => (b.onclick = () => { kalemler.splice(Number(b.dataset.kSil), 1); kalemCiz(); }));
    toplamCiz();
  };
  const toplamCiz = () => {
    $$("[data-kalem]").forEach((satir) => {
      const i = Number(satir.dataset.kalem);
      $$("[data-k]", satir).forEach((e) => (e.onchange = () => {
        kalemler[i][e.dataset.k] = e.type === "number" ? Number(e.value || 0) : e.value;
        toplamCiz();
      }));
    });
    let ara = 0, kdv = 0;
    kalemler.forEach((k) => { const t = (k.miktar || 0) * (k.birim_fiyat || 0); ara += t; kdv += t * (k.kdv_orani || 0) / 100; });
    const isk = Number(($("#fIsk") && $("#fIsk").value) || 0);
    $("#fToplam").innerHTML = `<span>Matrah: <b>${para(ara)}</b></span><span>KDV: <b>${para(kdv)}</b></span>
      <span>İskonto: <b>${para(isk)}</b></span><span>TOPLAM: <b>${para(ara - isk + kdv)}</b></span>`;
  };
  const kaydet = async () => {
    const govde = {
      id: f ? f.id : undefined, no: $("#fNo").value, tur: $("#fTur").value, cari_id: Number($("#fCari").value),
      tarih: $("#fTarih").value, vade: $("#fVade").value, aciklama: $("#fAck").value,
      durum: $("#fDurum").value, iskonto: Number($("#fIsk").value || 0), kalem: kalemler,
    };
    govde.tahsil = govde.durum === "Ödendi" ? null : 0;
    const r = await api("/api/fatura/kaydet", govde);
    modalKapat();
    bildir(`Fatura kaydedildi · ${para(r.toplam)}`);
    ekranCiz("fatura");
  };
  ciz();
  $("#kalemEkle").onclick = () => { kalemler.push({ aciklama: "", miktar: 1, birim: "Adet", birim_fiyat: 0, kdv_orani: 20 }); kalemCiz(); };
  if ($("#fIsk")) $("#fIsk").onchange = toplamCiz;
}

/* ---------------------------------------------------------- 8) STOK */
EKRANLAR.stok = async () => {
  const d = await api("/api/stok");
  const kritik = d.kayit.filter((x) => x.miktar <= x.kritik);
  $("#icerik").innerHTML = `
    <div class="izgara k4" style="margin-bottom:12px">
      <div class="kart turkuaz"><div class="kartEtiket">Ürün Çeşidi</div><div class="kartDeger turkuaz">${d.kayit.length}</div></div>
      <div class="kart altin"><div class="kartEtiket">Stok Değeri (alış)</div><div class="kartDeger altin">${para(d.deger)}</div></div>
      <div class="kart kirmizi"><div class="kartEtiket">Kritik Seviye</div><div class="kartDeger kirmizi">${kritik.length}</div>
        <div class="kartAltYazi">${kritik.map((k) => KACT(k.ad)).slice(0, 2).join(", ") || "uyarı yok"}</div></div>
      <div class="kart yesil"><div class="kartEtiket">Satış Değeri</div>
        <div class="kartDeger yesil">${para(d.kayit.reduce((t, x) => t + x.miktar * x.satis, 0))}</div></div>
    </div>
    ${tablo(["Kod", "Ürün", "Kategori", "Birim", "Miktar", "Kritik", "Alış", "Satış", "Stok Değeri", "Durum", "İşlem"],
    d.kayit.map((x) => [x.kod, x.ad, x.kategori, x.birim, { hucre: sayi(x.miktar), sinif: "para" }, sayi(x.kritik),
    { hucre: para(x.alis), sinif: "para" }, { hucre: para(x.satis), sinif: "para" },
    { hucre: para(x.miktar * x.alis), sinif: "para" },
    { hucre: x.miktar <= x.kritik ? '<span class="damga kirmizi">Kritik</span>' : '<span class="damga yesil">Yeterli</span>' },
    { hucre: `<button class="dugme kucuk" data-stok-duzenle="${x.id}">Düzenle</button> <button class="dugme kucuk kirmizi" data-stok-sil="${x.id}">Sil</button>` }]),
    { baslik: "Stok Listesi", yukseklik: "46vh", sagSutun: [4, 5, 6, 7, 8],
      toplamlar: [["Toplam Stok Değeri", para(d.deger)]] })}
    <div style="margin-top:12px;display:flex;gap:9px">
      <button class="dugme birincil" id="stokYeni">+ Yeni Ürün</button>
      <button class="dugme" id="stokWord">Word</button><button class="dugme" id="stokExcel">Excel</button></div>`;
  const aln = [
    { ad: "Ürün Kodu", anahtar: "kod" }, { ad: "Ürün Adı", anahtar: "ad", genis: true },
    { ad: "Kategori", anahtar: "kategori" },
    { ad: "Birim", anahtar: "birim", tur: "sec", secenekler: ["Adet", "Litre", "Koli", "Paket", "Rulo", "Kg", "Metre"] },
    { ad: "Miktar", anahtar: "miktar", tur: "number" }, { ad: "Kritik Seviye", anahtar: "kritik", tur: "number" },
    { ad: "Alış Fiyatı", anahtar: "alis", tur: "number" }, { ad: "Satış Fiyatı", anahtar: "satis", tur: "number" },
    { ad: "KDV %", anahtar: "kdv", tur: "number", varsayilan: 20 },
  ];
  $("#stokYeni").onclick = () => modalAc("Yeni Ürün", alanlar(aln, { birim: "Adet", kdv: 20 }), [
    { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
    { ad: "Kaydet", sinif: "birincil", tikla: async () => { const g = alanTopla(); await api("/api/stok/kaydet", g); modalKapat(); bildir("Ürün kaydedildi"); ekranCiz("stok"); } },
  ]);
  $$("[data-stok-duzenle]").forEach((b) => (b.onclick = () => {
    const x = d.kayit.find((y) => y.id === Number(b.dataset.stokDuzenle));
    modalAc("Ürünü Düzenle", alanlar(aln, x), [
      { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
      { ad: "Kaydet", sinif: "birincil", tikla: async () => { const g = alanTopla(); g.id = x.id; await api("/api/stok/kaydet", g); modalKapat(); bildir("Ürün güncellendi"); ekranCiz("stok"); } },
    ]);
  }));
  $$("[data-stok-sil]").forEach((b) => (b.onclick = () => sil("stok", Number(b.dataset.stokSil), "ürün", () => ekranCiz("stok"))));
  $("#stokWord").onclick = () => indir("/api/disa-aktar?kaynak=stok&tur=docx");
  $("#stokExcel").onclick = () => indir("/api/disa-aktar?kaynak=stok&tur=xlsx");
};

/* ---------------------------------------------------------- 9) PERSONEL */
EKRANLAR.personel = async () => {
  const d = await api("/api/personel");
  const toplam = d.kayit.reduce((t, x) => t + (x.maas || 0), 0);
  const sgk = toplam * 0.2275, stopaj = toplam * 0.15;
  $("#icerik").innerHTML = `
    <div class="izgara k4" style="margin-bottom:12px">
      <div class="kart turkuaz"><div class="kartEtiket">Personel</div><div class="kartDeger turkuaz">${d.kayit.length}</div>
        <div class="kartAltYazi">${d.kayit.filter((x) => x.durum === "Aktif").length} aktif</div></div>
      <div class="kart altin"><div class="kartEtiket">Aylık Maaş Yükü</div><div class="kartDeger altin">${para(toplam)}</div></div>
      <div class="kart pembe"><div class="kartEtiket">Tahmini SGK (%22,75)</div><div class="kartDeger pembe">${para(sgk)}</div></div>
      <div class="kart yesil"><div class="kartEtiket">Tahmini Stopaj (%15)</div><div class="kartDeger yesil">${para(stopaj)}</div></div>
    </div>
    ${tablo(["Ad Soyad", "Görev", "Telefon", "E-posta", "Maaş", "İşe Giriş", "Durum", "İşlem"],
    d.kayit.map((x) => [x.ad, x.gorev, x.telefon, x.email, { hucre: para(x.maas), sinif: "para" }, tarihKisa(x.giris_tarihi),
    { hucre: `<span class="damga ${x.durum === "Aktif" ? "yesil" : "altin"}">${KACT(x.durum)}</span>` },
    { hucre: `<button class="dugme kucuk" data-per-duzenle="${x.id}">Düzenle</button> <button class="dugme kucuk kirmizi" data-per-sil="${x.id}">Sil</button>` }]),
    { baslik: "Personel Listesi", yukseklik: "40vh", sagSutun: [4], toplamlar: [["Maaş Toplamı", para(toplam)], ["SGK + Stopaj", para(sgk + stopaj)], ["İşveren Maliyeti", para(toplam + sgk)]] })}
    <div class="kart" style="margin-top:12px"><div class="kartUst"><h3>Bordro Özeti (ön izleme)</h3>
      <span class="kartNot">gerçek bordro için muhasebe müşavirine danışılır</span></div>
      <div class="izgara k3">${d.kayit.map((x) => `<div class="kart"><div class="kartEtiket">${KACT(x.gorev)}</div>
        <div class="kartDeger turkuaz" style="font-size:19px">${KACT(x.ad)}</div>
        <div class="halkaSatir"><span>Brüt maaş</span><b>${para(x.maas)}</b></div>
        <div class="halkaSatir"><span>SGK işveren payı</span><b>${para(x.maas * 0.2275)}</b></div>
        <div class="halkaSatir"><span>Toplam maliyet</span><b class="paraPoz">${para(x.maas * 1.2275)}</b></div></div>`).join("")}</div></div>
    <div style="margin-top:12px;display:flex;gap:9px">
      <button class="dugme birincil" id="perYeni">+ Yeni Personel</button>
      <button class="dugme" id="perWord">Word</button><button class="dugme" id="perExcel">Excel</button>
      <button class="dugme altinDugme" id="perPdf">PDF</button></div>
    <div id="puaYer" style="margin-top:12px"></div>`;
  const aln = [
    { ad: "Ad Soyad", anahtar: "ad", genis: true }, { ad: "Görev", anahtar: "gorev" },
    { ad: "Telefon", anahtar: "telefon" }, { ad: "E-posta", anahtar: "email" },
    { ad: "Maaş (₺)", anahtar: "maas", tur: "number" },
    { ad: "İşe Giriş", anahtar: "giris_tarihi", tur: "date" },
    { ad: "Durum", anahtar: "durum", tur: "sec", secenekler: ["Aktif", "İzinli", "Ayrıldı"], varsayilan: "Aktif" },
    { ad: "Notlar", anahtar: "notlar", tur: "coklu", genis: true },
  ];
  $("#perYeni").onclick = () => modalAc("Yeni Personel", alanlar(aln), [
    { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
    { ad: "Kaydet", sinif: "birincil", tikla: async () => { const g = alanTopla(); await api("/api/personel/kaydet", g); modalKapat(); bildir("Personel kaydedildi"); ekranCiz("personel"); } },
  ]);
  $$("[data-per-duzenle]").forEach((b) => (b.onclick = () => {
    const x = d.kayit.find((y) => y.id === Number(b.dataset.perDuzenle));
    modalAc("Personeli Düzenle", alanlar(aln, x), [
      { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
      { ad: "Kaydet", sinif: "birincil", tikla: async () => { const g = alanTopla(); g.id = x.id; await api("/api/personel/kaydet", g); modalKapat(); bildir("Güncellendi"); ekranCiz("personel"); } },
    ]);
  }));
  $$("[data-per-sil]").forEach((b) => (b.onclick = () => sil("personel", Number(b.dataset.perSil), "personel", () => ekranCiz("personel"))));
  $("#perWord").onclick = () => indir("/api/disa-aktar?kaynak=personel&tur=docx");
  $("#perExcel").onclick = () => indir("/api/disa-aktar?kaynak=personel&tur=xlsx");
  $("#perPdf").onclick = () => indir("/api/pdf?kaynak=personel");
  try {
    const p = await api("/api/puantaj");
    DURUM.puantaj = p.kayit || [];
    $("#puaYer").innerHTML = await puantajKarti();
    puantajBagla();
  } catch (e) { $("#puaYer").innerHTML = '<div class="bos">Puantaj yüklenemedi: ' + KACT(e.message) + "</div>"; }
};

/* ---------------------------------------------------------- 10) RAPORLAR */
const RAPORLAR = [
  ["gelir-gider", "Gelir-Gider Raporu", "Kategori kategori gelir ve gider dökümü"],
  ["kar-zarar", "Kâr / Zarar Tablosu", "12 aylık gelir, gider ve net kâr"],
  ["vadesi-gecen", "Vadesi Geçen Faturalar", "Ödeme tarihi geçmiş alacaklar"],
  ["cari-ekstre", "Cari Ekstre Özeti", "Tüm cariler ve bakiyeleri"],
  ["kdv", "KDV Raporu", "Satış ve alış KDV dökümü"],
  ["tahsilat", "Tahsilat Raporu", "Cari tahsilat hareketleri"],
  ["kasa", "Kasa & Banka Durumu", "Hesap bazlı bakiye"],
  ["stok", "Stok Değer Raporu", "Miktar, alış, satış, değer"],
  ["personel", "Personel Performans", "Görev, maaş, işe giriş"],
  ["gorusme", "Görüşme Raporu", "Müşteri görüşme geçmişi"],
];
function kullaniciForm(kayit, roller) {
  const rl = roller || { yonetici: "Yönetici", kasiyer: "Kasiyer", misafir: "Misafir" };
  const aln = [
    { ad: "Kullanıcı Adı", anahtar: "ad" },
    { ad: "Rol", anahtar: "rol", tur: "sec", secenekler: Object.keys(rl) },
    { ad: kayit ? "Yeni Şifre (boş = değişmesin)" : "Şifre", anahtar: "sifre" },
    { ad: "Aktif (1/0)", anahtar: "aktif", tur: "sayi", varsayilan: 1 },
  ];
  modalAc(kayit ? "Kullanıcıyı Düzenle" : "Yeni Kullanıcı", alanlar(aln, kayit ? { ad: kayit.ad, rol: kayit.rol, aktif: kayit.aktif } : { rol: "kasiyer", aktif: 1 }), [
    { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
    { ad: "Kaydet", sinif: "birincil", tikla: async () => {
      const g = alanTopla();
      if (kayit) g.ad = kayit.ad;
      await api("/api/kullanici/kaydet", g);
      modalKapat(); bildir("Kullanıcı kaydedildi"); ekranCiz("ayarlar");
    } },
  ]);
}

/* ---- ek raporlar (KDV özeti · anomali · nakit akışı · yıl karnesi) ---- */
const OZEL_RAPORLAR = [
  ["kdv-ozet", "KDV Özeti", "Bu ayın hesaplanan / indirilecek / ödenecek KDV'si"],
  ["anomali", "Harcama Anomalisi", "Geçen aya göre fırlayan kategoriler"],
  ["nakit-akis", "Nakit Akışı Tahmini", "Önümüzdeki ayların kasa projeksiyonu"],
  ["karne", "Yıl Sonu Karnesi", "Yılın toplamı ve en büyük kalemleri"],
];
async function ozelRaporCiz(id) {
  const k = $("#ozelRapor");
  k.innerHTML = '<div class="bos">Hazırlanıyor…</div>';
  const d = await api("/api/" + id);
  if (id === "kdv-ozet") {
    const kartlar = [["Hesaplanan KDV", d.hesaplanan_kdv, "turkuaz"], ["İndirilecek KDV", d.indirilecek_kdv, "pembe"],
      ["Devreden", d.sonraki_devreden, "altin"], ["Ödenecek", d.odenecek, d.odenecek > 0 ? "kirmizi" : "yesil"]];
    const html = kartlar.map(function (t) {
      return '<div class="kart ' + t[2] + '"><div class="kartEtiket">' + KACT(t[0]) +
        '</div><div class="kartDeger ' + t[2] + '" data-sayac="' + t[1] + '">' + para(t[1]) + "</div></div>";
    }).join("");
    k.innerHTML = '<div class="izgara k4">' + html + "</div><div class=\"kartAltYazi\" style=\"margin-top:10px\">Dönem: " +
      d.bas + " → " + d.bit + " · satış faturası " + d.satis_fatura + " · alış faturası " + d.alis_fatura +
      '. Bu bir <b>ön özet</b>tir; beyanname yerine geçmez — mali müşavirle teyit et.</div>';
  } else if (id === "anomali") {
    const r = d.kayit || [];
    k.innerHTML = tablo(["Kategori", "Bu Ay", "Geçen Ay", "Fark %", "Adet", "Seviye"],
      r.map((x) => [x.kategori, { hucre: para(x.bu_ay), sinif: "para" }, { hucre: para(x.gecen_ay), sinif: "para" },
        { hucre: "%" + sayi(x.fark_yuzde), sinif: "para" }, x.adet,
        { hucre: `<span class="damgaYeni ${x.seviye === "yüksek" ? "kirmizi" : "altin"}">${KACT(x.seviye)}</span>` }]),
      { baslik: "Geçen aya göre artış (son 2 ay)", yukseklik: "40vh", sagSutun: [1, 2, 3] }) +
      (r.length ? "" : '<div class="bos">Belirgin artış yok — harcamalar dengeli.</div>');
  } else if (id === "nakit-akis") {
    const s = d.seri || [];
    const enb = Math.max(...s.map((x) => Math.abs(x.kasa_sonu)), 1);
    k.innerHTML = `<div class="kartAltYazi" style="margin-bottom:10px">Başlangıç kasası: <b>${para(d.baslangic_kasa)}</b> — sabit gelir/gider, çek-senet ve fatura tahsilatlarına göre tahmin.</div>
      <div class="grafikSatir">${s.map((x) => `<div class="cubukKutu">
        <div class="cubuk ${x.net >= 0 ? "yesil" : "kirmizi"}" style="height:${Math.max(3, Math.abs(x.net) / enb * 100)}%" title="net ${para(x.net)}"></div>
        <div class="ekBilgi">${KACT(x.ad)}</div><div class="ekBilgi">${para(x.kasa_sonu, true)}</div></div>`).join("")}</div>
      ${tablo(["Ay", "Gelir", "Gider", "Çek (verilen)", "Çek (alınan)", "Net", "Kasa Sonu"],
      s.map((x) => [KACT(x.ad), { hucre: para(x.gelir), sinif: "para" }, { hucre: para(x.gider), sinif: "para" },
        { hucre: para(x.cek_verilen), sinif: "para" }, { hucre: para(x.cek_alinan), sinif: "para" },
        { hucre: para(x.net), sinif: x.net >= 0 ? "paraPoz" : "paraNeg" }, { hucre: para(x.kasa_sonu), sinif: "para" }]),
      { baslik: "Ay ay tahmin", yukseklik: "38vh", sagSutun: [1, 2, 3, 4, 5, 6] })}`;
  } else {
    const y = d;
    k.innerHTML = `<div class="izgara k4">
      ${[["Toplam Gelir", y.gelir, "yesil"], ["Toplam Gider", y.gider, "kirmizi"],
        ["Net Kâr", y.net, y.net >= 0 ? "turkuaz" : "kirmizi"], ["Kayıt Sayısı", y.kayit, "altin"]]
        .map(([ad, v, r]) => `<div class="kart ${r}"><div class="kartEtiket">${ad}</div>
        <div class="kartDeger ${r}" data-sayac="${v}">${typeof v === "number" && v > 1000 ? para(v) : sayi(v)}</div></div>`).join("")}</div>
      <div class="kart" style="margin-top:12px"><div class="kartUst"><h3>En Büyük Kalemler</h3><span class="kartNot">${y.yil || new Date().getFullYear()}</span></div>
        ${(y.en_buyuk || []).map((x) => `<div class="halkaSatir"><span>${KACT(x.kategori || x.ad)}</span><b>${para(x.tutar)}</b></div>`).join("") || '<div class="bos">Veri yok.</div>'}</div>`;
  }
}
EKRANLAR.rapor = async () => {
  const d = await api("/api/rapor?tur=" + DURUM.rapor_tur);
  $("#icerik").innerHTML = `
    <div class="izgara k3" style="margin-bottom:12px">
      ${RAPORLAR.map(([id, ad, aciklama]) => `
        <div class="kart ${id === DURUM.rapor_tur ? "turkuaz" : ""}" data-rapor="${id}" style="cursor:pointer">
          <div class="kartEtiket">${id === DURUM.rapor_tur ? "SEÇİLİ RAPOR" : "RAPOR"}</div>
          <div class="kartDeger turkuaz" style="font-size:17px">${KACT(ad)}</div>
          <div class="kartAltYazi">${KACT(aciklama)}</div></div>`).join("")}
    </div>
    <div id="raporTablo"></div>
    <div style="margin-top:12px;display:flex;gap:9px;flex-wrap:wrap">
      <button class="dugme birincil" id="rapExcel">Excel'e Aktar</button>
      <button class="dugme altin" id="rapWord">Word'e Aktar</button>
      <button class="dugme altinDugme" id="rapPdf">PDF Olarak Kaydet</button>
      <span class="kartNot" style="align-self:center">Seçili rapor: <b>${KACT(RAPORLAR.find((r) => r[0] === DURUM.rapor_tur)[1])}</b></span>
    </div>
    <div class="kart" style="margin-top:16px"><div class="kartUst"><h3>Akıllı Raporlar</h3>
      <span class="kartNot">defteri yorumlayan ek analizler</span></div>
      <div class="tusSatir">${OZEL_RAPORLAR.map(([id, ad, ac]) => `
        <button class="dugme ${DURUM.ozel_rapor === id ? "birincil" : ""}" data-ozel="${id}" title="${KACT(ac)}">${KACT(ad)}</button>`).join("")}</div>
      <div id="ozelRapor" style="margin-top:13px"></div></div>`;
  $("#raporTablo").innerHTML = tablo(d.basliklar, d.satirlar, {
    baslik: RAPORLAR.find((r) => r[0] === DURUM.rapor_tur)[1], yukseklik: "48vh", sagSutun: [2, 3, 4, 5, 6, 7],
    toplamlar: [["TOPLAM", para(d.toplam)]],
  });
  $$("[data-rapor]").forEach((k) => (k.onclick = async () => { DURUM.rapor_tur = k.dataset.rapor; ekranCiz("rapor"); }));
  $$("[data-ozel]").forEach((b) => (b.onclick = async () => {
    DURUM.ozel_rapor = b.dataset.ozel;
    $$("[data-ozel]").forEach((x) => x.classList.toggle("birincil", x.dataset.ozel === DURUM.ozel_rapor));
    try { await ozelRaporCiz(DURUM.ozel_rapor); } catch (e) { $("#ozelRapor").innerHTML = `<div class="bos">${KACT(e.message)}</div>`; }
  }));
  if (DURUM.ozel_rapor) { try { await ozelRaporCiz(DURUM.ozel_rapor); } catch (e) { /* geç */ } }
  $("#rapExcel").onclick = () => indir(`/api/disa-aktar?kaynak=rapor&rapor=${DURUM.rapor_tur}&tur=xlsx`);
  $("#rapWord").onclick = () => indir(`/api/disa-aktar?kaynak=rapor&rapor=${DURUM.rapor_tur}&tur=docx`);
  $("#rapPdf").onclick = () => { bildir("PDF hazırlanıyor — Word açılıp kapanabilir…"); indir(`/api/pdf?kaynak=rapor&rapor=${DURUM.rapor_tur}`); };
};

/* ---------------------------------------------------------- 11) ÇIKTILAR */
EKRANLAR.cikti = async () => {
  const d = await api("/api/ciktilar");
  $("#icerik").innerHTML = `
    <div class="izgara k4" style="margin-bottom:12px">
      <div class="kart turkuaz"><div class="kartEtiket">Üretilen Belge</div><div class="kartDeger turkuaz">${d.kayit.length}</div></div>
      <div class="kart altin"><div class="kartEtiket">Toplam Boyut</div>
        <div class="kartDeger altin">${sayi(d.kayit.reduce((t, x) => t + x.boyut, 0) / 1024)}</div>
        <div class="kartAltYazi">KB</div></div>
      <div class="kart"><div class="kartEtiket">Word (.docx)</div><div class="kartDeger pembe">${d.kayit.filter((x) => x.ad.endsWith(".docx")).length}</div></div>
      <div class="kart"><div class="kartEtiket">Excel (.xlsx)</div><div class="kartDeger yesil">${d.kayit.filter((x) => x.ad.endsWith(".xlsx")).length}</div></div>
    </div>
    ${tablo(["Dosya", "Tür", "Boyut", "Zaman", "İşlem"],
    d.kayit.map((x) => [x.ad, x.ad.endsWith(".docx") ? "Word" : "Excel", { hucre: (x.boyut / 1024).toFixed(1) + " KB", sinif: "para" }, x.zaman,
    { hucre: `<button class="dugme kucuk" data-indir="${KACT(x.ad)}">İndir</button>` }]),
    { baslik: "Üretilen Belgeler", yukseklik: "50vh", sagSutun: [2] })}
    <div style="margin-top:12px" class="kartNot">Klasör: <b>${KACT(d.klasor)}</b> — buradaki dosyaları Windows'ta da açabilirsin.</div>`;
  $$("[data-indir]").forEach((b) => (b.onclick = () => indir("/cikti/" + encodeURIComponent(b.dataset.indir))));
};

/* ---------------------------------------------------------- 12) AYARLAR */
let ayarSekme = 0;
EKRANLAR.ayarlar = async () => {
  const d = await api("/api/durum");
  const y = await api("/api/yedek/listele");
  const l = await api("/api/log");
  const sekmeler = ["Firma Bilgisi", "Kullanıcılar & Roller", "Ağ & Güvenlik", "Yedekleme", "Otomasyon", "Denetim Kaydı"];
  $("#icerik").innerHTML = `
    <div class="izgara k4" style="margin-bottom:12px">
      <div class="kart turkuaz"><div class="kartEtiket">Sürüm</div><div class="kartDeger turkuaz">v${d.surum}</div>
        <div class="kartAltYazi">port ${d.port}</div></div>
      <div class="kart altin"><div class="kartEtiket">Veritabanı</div><div class="kartDeger altin">${(d.db_boyut / 1024).toFixed(0)} KB</div>
        <div class="kartAltYazi">${KACT(d.db)}</div></div>
      <div class="kart yesil"><div class="kartEtiket">Kayıt Sayısı</div>
        <div class="kartDeger yesil">${Object.values(d.sayilar).reduce((a, b) => a + b, 0)}</div>
        <div class="kartAltYazi">${Object.keys(d.sayilar).length} tablo</div></div>
      <div class="kart pembe"><div class="kartEtiket">Yedek Sayısı</div><div class="kartDeger pembe">${y.kayit.length}</div></div>
    </div>
    <div class="sekmeler">${sekmeler.map((s, i) => `<button class="sekme ${i === ayarSekme ? "aktif" : ""}" data-as="${i}">${s}</button>`).join("")}</div>
    <div id="ayarIcerik"></div>`;
  $$("[data-as]").forEach((b) => (b.onclick = () => { ayarSekme = Number(b.dataset.as); ekranCiz("ayarlar"); }));
  const k = $("#ayarIcerik");
  if (ayarSekme === 0) {
    k.innerHTML = `<div class="izgara k2">
      <div class="kart"><div class="kartUst"><h3>Firma Bilgisi</h3></div>
        <div class="formIzgara">
          <div class="alan genis"><label>Firma Ünvanı</label><input id="aFirma" value="${KACT(d.ayar.firma)}"></div>
          <div class="alan"><label>KDV Oranı (%)</label><input id="aKdv" type="number" value="${d.ayar.kdv}"></div>
          <div class="alan"><label>Para Birimi</label><select id="aPara">${["TRY", "USD", "EUR"].map((p) => `<option ${p === d.ayar.para ? "selected" : ""}>${p}</option>`).join("")}</select></div>
        </div>
        <button class="dugme birincil" id="ayarKaydet" style="margin-top:12px">Ayarları Kaydet</button></div>
      <div class="kart"><div class="kartUst"><h3>Görünüm Teması · ${TEMALAR.length} renk</h3><span class="kartNot">anında uygulanır, seçim hatırlanır</span></div>
        <div class="paletSatir" id="ayarPalet">${PALETLER.map(([id, ad]) => `
          <button class="paletDugme ${(JSON.parse(localStorage.getItem("ustad_ayar") || "{}").palet || "tatli") === id ? "aktif" : ""}"
            data-palet="${id}" title="${ad} renk paleti"></button>`).join("")}</div>
        <div class="kartAltYazi" style="text-align:center;margin-bottom:12px">Renk paleti — tema seçiminden bağımsız, 6 renk ailesi (${PALETLER.map((p) => p[1]).join(" · ")})</div>
        <div class="izgara k3" style="grid-template-columns:repeat(auto-fit,minmax(calc(160px * var(--olcek)),1fr))">
          ${TEMALAR.map(([id, ad, ac]) => `
            <div class="kart ${document.documentElement.dataset.tema === id ? "turkuaz" : ""}" data-tema-sec="${id}" style="cursor:pointer">
              <div class="kartDeger turkuaz" style="font-size:16px">${ad}</div>
              <div class="kartAltYazi">${ac}</div></div>`).join("")}
        </div>
        <div class="kartAltYazi" style="margin-top:12px">Yazılar 4K/5K'da keskin kalsın diye punto ve boşluklar ekranla birlikte ölçeklenir (1920 → 1.0 · 2400 → 1.2 · 3200 → 1.35 · 4K → 1.5 · 5K → 1.75).</div></div>
    </div>`;
    $$("[data-tema-sec]").forEach((b) => (b.onclick = () => { temaAyarla(b.dataset.temaSec); ekranCiz("ayarlar"); }));
    $$("#ayarPalet .paletDugme").forEach((b) => (b.onclick = () => { paletAyarla(b.dataset.palet); ekranCiz("ayarlar"); }));
    $("#ayarKaydet").onclick = async () => {
      await api("/api/ayar", { firma: $("#aFirma").value, kdv: Number($("#aKdv").value), para: $("#aPara").value });
      $("#yanFirmaAd").textContent = "ÜSTAD MUHASEBE";
      const altY = $("#yanFirmaAlt");
      if (altY) altY.textContent = "TAM TEŞKİLAT · " + ($("#aFirma").value || "ÜSTAD SALON KENAN");
      bildir("Ayarlar kaydedildi");
    };
  } else if (ayarSekme === 1) {
    const ku = await api("/api/kullanici");
    k.innerHTML = `<div class="izgara k2">
      <div class="kart"><div class="kartUst"><h3>Kullanıcılar ve Roller</h3>
        <span class="kartNot">${ku.kayit.length} kullanıcı</span></div>
        ${tablo(["Kullanıcı", "Rol", "Durum", "Son Giriş", "İşlem"],
    ku.kayit.map((x) => [x.ad, KACT(x.rol_ad),
      { hucre: `<span class="damgaYeni ${x.aktif ? "yesil" : "gri"}">${x.aktif ? "aktif" : "kapalı"}</span>` },
      x.son_giris || "—",
      { hucre: `<div class="islemHucre"><button class="dugme kucuk" data-kul-dz="${x.id}">Düzenle</button>
        ${x.rol === "yonetici" ? '<span class="ekBilgi">son yönetici korunur</span>' :
          `<button class="dugme kucuk ${x.aktif ? "kirmizi" : "yesilDugme"}" data-kul-akt="${x.id}">${x.aktif ? "Kapat" : "Aç"}</button>`}</div>` }]),
    { baslik: "Yetkili Kullanıcılar", yukseklik: "38vh" })}
        <div class="tusSatir"><button class="dugme birincil" id="kulYeni">+ Kullanıcı Ekle</button>
          <button class="dugme" id="kulExcel">Excel</button></div></div>
      <div class="kart"><div class="kartUst"><h3>Rollerin Yetkileri</h3><span class="kartNot">sunucu tarafında uygulanır</span></div>
        <div class="halkaSatir"><span><b>Yönetici</b> — her şey: kayıt, silme, ayar, yedek geri alma, kullanıcı yönetimi</span></div>
        <div class="halkaSatir"><span><b>Kasiyer</b> — kasa hareketi, fatura ve gelir/gider kaydı girebilir; <b>silemez</b>, ayar değiştiremez</span></div>
        <div class="halkaSatir"><span><b>Misafir</b> — yalnızca okuma ve rapor; hiçbir kayıt giremez</span></div>
        <div class="kartAltYazi" style="margin-top:10px">Şifreler sunucuda <b>PBKDF2 (100.000 tur + rastgele tuz)</b> ile saklanır; şifrenin kendisi hiçbir yerde düz yazılmaz.
        Girişte sunucu bir <b>oturum jetonu</b> verir, panel her istekte onu gönderir.</div></div>
    </div>`;
    $("#kulYeni").onclick = () => kullaniciForm(null, ku.roller);
    $$("[data-kul-dz]").forEach((b) => (b.onclick = () => kullaniciForm(ku.kayit.find((x) => x.id === Number(b.dataset.kulDz)), ku.roller)));
    $$("[data-kul-akt]").forEach((b) => (b.onclick = async () => {
      const x = ku.kayit.find((y) => y.id === Number(b.dataset.kulAkt));
      await api("/api/kullanici/kaydet", { ad: x.ad, rol: x.rol, aktif: x.aktif ? 0 : 1 });
      bildir(x.aktif ? "Kullanıcı kapatıldı" : "Kullanıcı açıldı"); ekranCiz("ayarlar");
    }));
    $("#kulExcel").onclick = () => indir("/api/disa-aktar?kaynak=kullanicilar&tur=xlsx");
  } else if (ayarSekme === 2) {
    const a = await api("/api/lan");
    const e = await api("/api/ek-ayar");
    k.innerHTML = `<div class="izgara k2">
      <div class="kart"><div class="kartUst"><h3>Yerel Ağ (telefondan girme)</h3>
        <span class="damgaYeni ${a.acik ? "yesil" : "gri"}">${a.acik ? "açık" : "kapalı"}</span></div>
        <div class="kartAltYazi">Açıkken aynı WiFi'deki telefon/tablet tarayıcısından şu adresle panele girilir. Kapalıyken program yalnız bu bilgisayardan açılır — daha güvenli.</div>
        <div class="kartDeger turkuaz" style="font-size:calc(17px * var(--olcek));margin:12px 0">${KACT(a.telefon)}</div>
        <div class="kartAltYazi">Bilgisayarın adresleri: ${a.adresler.join(" · ") || "—"} · port ${a.port}</div>
        <div class="tusSatir"><button class="dugme ${a.acik ? "kirmizi" : "birincil"}" id="lanDegis">${a.acik ? "Ağı Kapat" : "Ağı Aç"}</button></div>
        <div class="kartAltYazi" style="margin-top:10px">Not: Bu düğme tercihi kaydeder. Ağ adresine bağlanmak için programı <b>AG-AC.bat</b> ile (veya ilk açılışta ağ seçeneğiyle) başlatmak gerekir.</div></div>
      <div class="kart"><div class="kartUst"><h3>Güvenlik Özeti</h3></div>
        <div class="halkaSatir"><span>Giriş doğrulaması</span><b class="paraPoz">Sunucuda PBKDF2</b></div>
        <div class="halkaSatir"><span>Oturum</span><b class="paraPoz">Rastgele jeton (her istekte denetlenir)</b></div>
        <div class="halkaSatir"><span>Rol denetimi</span><b class="paraPoz">Her yazma ucu için ayrı</b></div>
        <div class="halkaSatir"><span>Denetim kaydı</span><b class="paraPoz">Tüm işlemler loglanır</b></div>
        <div class="halkaSatir"><span>Yedek</span><b class="paraPoz">Elle + otomatik (günlük)</b></div>
        <div class="kartAltYazi" style="margin-top:10px">Dürüst sınır: yerel ağda çalışan program HTTP kullanır; aynı ağdaki ileri düzey biri trafiği izleyebilir.
        Bu yüzden varsayılan <b>kapalı</b>; dışarıdan erişim gerekiyorsa VPN kullan.</div></div>
    </div>`;
    $("#lanDegis").onclick = async () => { await api("/api/lan", { acik: !a.acik }); bildir("Kaydedildi"); ekranCiz("ayarlar"); };
  } else if (ayarSekme === 3) {
    k.innerHTML = `<div class="kart"><div class="kartUst"><h3>Şifreli Yedekleme</h3>
      <button class="dugme birincil" id="yedekAl">Şimdi Yedek Al</button></div>
      <div class="kartAltYazi">Yedek: veritabanının tam kopyası · Klasör: <b>${KACT(y.klasor)}</b></div>
      <div style="margin-top:12px">${tablo(["Yedek Dosyası", "Boyut", "Zaman", "İşlem"],
      y.kayit.map((x) => [x.ad, { hucre: (x.boyut / 1024).toFixed(1) + " KB", sinif: "para" }, x.zaman,
      { hucre: `<button class="dugme kucuk kirmizi" data-yedek-geri="${KACT(x.ad)}">Geri Yükle</button>` }]),
      { baslik: "Yedekler", yukseklik: "34vh", sagSutun: [1] })}</div></div>`;
    $("#yedekAl").onclick = async () => { const r = await api("/api/yedek/al", {}); bildir(`Yedek alındı: ${r.ad}`); ekranCiz("ayarlar"); };
    $$("[data-yedek-geri]").forEach((b) => (b.onclick = () => {
      const ad = b.dataset.yedekGeri;
      modalAc("Yedeği Geri Yükle", `<p>“${KACT(ad)}” yedeği geri yüklenecek. Mevcut veritabanı <b>.onceki</b> olarak saklanır.</p>`, [
        { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
        { ad: "Geri Yükle", sinif: "kirmizi", tikla: async () => { await api("/api/yedek/geri", { ad }); modalKapat(); bildir("Yedek geri yüklendi"); ekranCiz("ayarlar"); } },
      ]);
    }));
  } else if (ayarSekme === 4) {
    const e = await api("/api/ek-ayar");
    const yo = await api("/api/yedek/oto");
    const ai = await api("/api/ai/durum");
    k.innerHTML = `<div class="izgara k2">
      <div class="kart"><div class="kartUst"><h3>Otomatik Yedek</h3>
        <span class="damgaYeni ${e.ayar.oto_yedek ? "yesil" : "gri"}">${e.ayar.oto_yedek ? "açık" : "kapalı"}</span></div>
        <div class="kartAltYazi">Günde bir kez belirlenen saatte veritabanının kopyası alınır. Böylece “yanlış sildim” durumunda geri dönülebilir.</div>
        <div class="formIzgara" style="margin-top:12px">
          <div class="alan"><label>Kapalı / Açık</label><select id="otoAcik"><option value="1" ${e.ayar.oto_yedek ? "selected" : ""}>Açık</option><option value="0" ${!e.ayar.oto_yedek ? "selected" : ""}>Kapalı</option></select></div>
          <div class="alan"><label>Saat</label><input id="otoSaat" type="number" min="0" max="23" value="${e.ayar.oto_yedek_saat || 20}"></div>
        </div>
        <div class="tusSatir"><button class="dugme birincil" id="otoKaydet">Kaydet</button></div>
        <div class="kartAltYazi" style="margin-top:10px">Son yedekler: ${(yo.yedekler || []).slice(-3).map((x) => KACT(x.ad || x)).join(" · ") || "—"}</div></div>
      <div class="kart"><div class="kartUst"><h3>Mali Müşavir Paketi</h3>
        <span class="damgaYeni altin">tek dosya · ZIP</span></div>
        <div class="kartAltYazi">Ayın tüm defterlerini (cari, fatura, gelir-gider, sade defter, kasa, stok, personel, puantaj, çek-senet, KDV)
        <b>CSV + özet metin</b> olarak tek ZIP'te toplar. Muhasebeciye e-posta ile gönderilebilir.</div>
        <div class="formIzgara" style="margin-top:12px">
          <div class="alan"><label>Başlangıç</label><input id="mpBas" type="date" value="${bugunISO().slice(0, 8)}01"></div>
          <div class="alan"><label>Bitiş</label><input id="mpBit" type="date" value="${bugunISO()}"></div>
        </div>
        <div class="tusSatir"><button class="dugme birincil" id="mpIndir">Paketi İndir</button></div>
        <div class="kartAltYazi" style="margin-top:10px">Paket yalnız senin bilgisayarında üretilir; hiçbir yere yüklenmez.</div></div>
      <div class="kart"><div class="kartUst"><h3>KDV Devreden</h3></div>
        <div class="kartAltYazi">Önceki dönemden devreden KDV varsa yaz; KDV özeti hesabı buna göre yapılır.</div>
        <div class="formIzgara" style="margin-top:10px"><div class="alan genis"><label>Devreden KDV (₺)</label><input id="kdvDev" type="number" step="0.01" value="0"></div></div>
        <div class="tusSatir"><button class="dugme birincil" id="kdvDevKaydet">Kaydet</button></div></div>
      <div class="kart"><div class="kartUst"><h3>Muhasebe Asistanı</h3>
        <span class="damgaYeni ${ai.anahtar ? "yesil" : "kirmizi"}">${ai.anahtar ? "hazır" : "anahtar yok"}</span></div>
        <div class="kartAltYazi">Asistan kendi defterindeki gerçek sayılarla cevap verir. Anahtarı “Asistan” ekranından gir.
        Anahtar yoksa program tam çalışır; yalnız asistan kapalı kalır.</div>
        <div class="tusSatir"><button class="dugme" id="aiGit">Asistan Ekranına Git</button></div></div>
      <div class="kart"><div class="kartUst"><h3>Tekrarlayan Kayıtlar</h3></div>
        <div class="kartAltYazi">Program her açılışta vadesi gelmiş kira/maaş/abonelik kayıtlarını kendiliğinden deftere işler.
        Kaydı görmek veya elle çalıştırmak için “Tekrarlayan” ekranını aç.</div>
        <div class="tusSatir"><button class="dugme" id="tekGit">Tekrarlayan Ekranına Git</button></div></div>
    </div>`;
    $("#otoKaydet").onclick = async () => {
      await api("/api/yedek-oto", { acik: $("#otoAcik").value === "1", saat: Number($("#otoSaat").value) });
      bildir("Otomatik yedek ayarı kaydedildi"); ekranCiz("ayarlar");
    };
    $("#mpIndir").onclick = () => indir(`/api/musavir-paketi?bas=${$("#mpBas").value}&bit=${$("#mpBit").value}`);
    $("#kdvDevKaydet").onclick = async () => {
      await api("/api/kdv-devreden", { tutar: Number($("#kdvDev").value) });
      bildir("Devreden KDV kaydedildi");
    };
    $("#aiGit").onclick = () => ekranCiz("ai");
    $("#tekGit").onclick = () => ekranCiz("tekrar");
  } else {
    k.innerHTML = tablo(["Zaman", "Kullanıcı", "İşlem", "Detay"],
      l.kayit.map((x) => [x.zaman, x.kullanici, x.islem, x.detay]),
      { baslik: "Denetim Kaydı (son 80 işlem)", yukseklik: "52vh" });
  }
};

/* ------------------------------------------------------------- ortak işler */
function indir(url) {
  bildir("Belge hazırlanıyor…");
  const a = document.createElement("a");
  a.href = url;
  a.download = "";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => { ekranCiz(DURUM.ekran === "cikti" ? "cikti" : DURUM.ekran); }, 1200);
}
function sil(tablo_, id, ad, sonra) {
  modalAc("Kaydı Sil", `<p><b>${KACT(ad)}</b> kaydı silinsin mi? Bu işlem geri alınamaz (yedekten dönebilirsin).</p>`, [
    { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
    { ad: "Sil", sinif: "kirmizi", tikla: async () => { await api("/api/sil", { tablo: tablo_, id }); modalKapat(); bildir("Kayıt silindi"); sonra && sonra(); } },
  ]);
}

/* ------------------------------------------------------------- olaylar */
function olaylar() {
  $$(".menuOge").forEach((b) => (b.onclick = () => ekranCiz(b.dataset.ekran)));
  $$(".temaDugme").forEach((b) => (b.onclick = () => temaAyarla(b.dataset.tema)));
  $$(".paletDugme").forEach((b) => (b.onclick = () => paletAyarla(b.dataset.palet)));
  $("#menuDugme").onclick = () => $("#yan").classList.toggle("acik");
  $("#modalKapat").onclick = modalKapat;
  $("#modal").onclick = (e) => { if (e.target.id === "modal") modalKapat(); };
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") { modalKapat(); const p = $("#canPanel"); if (p) p.remove(); } });
  $("#canDugme").onclick = (e) => { e.stopPropagation(); uyariPaneli(); };
  document.addEventListener("click", (e) => {
    const p = $("#canPanel");
    if (p && !p.contains(e.target) && e.target.id !== "canDugme") p.remove();
  });
  $("#girisForm").onsubmit = async (e) => {
    e.preventDefault();
    const r = await girisDene($("#kullaniciAdi").value, $("#sifre").value);
    if (r.tamam) { $("#girisHata").textContent = ""; kilitAc(); }
    else { $("#girisHata").textContent = r.mesaj; }
  };
  const hizli = { genel: "cari", cari: "cari", harcama: "harcama", gorusme: "gorusme", gelir: "gelir-gider",
    gider: "gelir-gider", kasa: "hesap", fatura: "fatura", stok: "stok", personel: "personel" };
  $("#hizliExcel").onclick = () => indir("/api/disa-aktar?kaynak=" + (hizli[DURUM.ekran] || "cari") + "&tur=xlsx");
  $("#hizliWord").onclick = () => indir("/api/disa-aktar?kaynak=" + (hizli[DURUM.ekran] || "cari") + "&tur=docx");
  $("#hizliPdf").onclick = () => {
    bildir("PDF hazırlanıyor — Word açılıp kapanabilir, 5-15 saniye…");
    indir("/api/pdf?kaynak=" + (hizli[DURUM.ekran] || "cari"));
  };
  $("#arama").onkeydown = (e) => { if (e.key === "Enter" && $("#arama").value.trim()) { ekranCiz("cari").then(() => { if ($("#cariAra")) { $("#cariAra").value = $("#arama").value; cariListeCiz($("#arama").value); } }); } };
  window.addEventListener("hashchange", hashUygula);
  hashUygula();
}
function hashUygula() {
  const h = (location.hash || "").replace("#", "");
  if (!h) return;
  const [t, p] = h.split("/");
  if (t && TEMALAR.some((x) => x[0] === t)) temaAyarla(t);
  if (p && PALETLER.some((x) => x[0] === p)) paletAyarla(p);
}

/* ============================================================ ÇEK & SENET */
const CEK_DURUM = { "Portföyde": "turkuaz", "Tahsil": "yesil", "Ödendi": "yesil", "Ödenecek": "altin", "Karşılıksız": "kirmizi", "İptal": "gri" };
async function cekForm(kayit) {
  const c = await api("/api/cari");
  const aln = [
    { ad: "Tür", anahtar: "tur", tur: "sec", secenekler: ["Çek", "Senet"] },
    { ad: "Yön", anahtar: "yon", tur: "sec", secenekler: ["Alınan", "Verilen"] },
    { ad: "No", anahtar: "no" },
    { ad: "Cari", anahtar: "cari_id", tur: "sec", secenekler: c.kayit.map((x) => x.id) },
    { ad: "Banka", anahtar: "banka" },
    { ad: "Tutar", anahtar: "tutar", tur: "sayi" },
    { ad: "Kesim Tarihi", anahtar: "kesim", tur: "date", varsayilan: bugunISO() },
    { ad: "Vade", anahtar: "vade", tur: "date", varsayilan: bugunISO() },
    { ad: "Durum", anahtar: "durum", tur: "sec", secenekler: Object.keys(CEK_DURUM) },
    { ad: "Açıklama", anahtar: "aciklama", genis: true },
  ];
  modalAc(kayit ? "Çek / Senet Düzenle" : "Yeni Çek / Senet", alanlar(aln, kayit || { tur: "Çek", yon: "Alınan", durum: "Portföyde" }), [
    { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
    { ad: "Kaydet", sinif: "birincil", tikla: async () => {
      const g = alanTopla();
      if (kayit) g.id = kayit.id;
      await api("/api/cek/kaydet", g);
      modalKapat(); bildir("Çek/senet kaydedildi"); rozetleriYenile(); ekranCiz("cek");
    } },
  ]);
}
EKRANLAR.cek = async () => {
  const d = await api("/api/cek");
  const gec = d.vadesi_gecen || [], yak = d.yaklasan || [];
  const damga = (x) => `<span class="damgaYeni ${CEK_DURUM[x.durum] || "gri"}">${KACT(x.durum)}</span>`;
  $("#icerik").innerHTML = `
    <div class="izgara k4" style="margin-bottom:14px">
      <div class="kart turkuaz"><div class="kartEtiket">Alınan · Portföyde</div>
        <div class="kartDeger turkuaz" data-sayac="${d.alinan_portfoy}">${para(d.alinan_portfoy)}</div>
        <div class="kartAltYazi">tahsil edilecek</div></div>
      <div class="kart pembe"><div class="kartEtiket">Verilen · Ödenecek</div>
        <div class="kartDeger pembe" data-sayac="${d.verilen_portfoy}">${para(d.verilen_portfoy)}</div>
        <div class="kartAltYazi">bizim ödeyeceğimiz</div></div>
      <div class="kart kirmizi"><div class="kartEtiket">Vadesi Geçen</div>
        <div class="kartDeger kirmizi uyariNabiz" data-sayac="${gec.reduce((t, x) => t + x.tutar, 0)}">${para(gec.reduce((t, x) => t + x.tutar, 0))}</div>
        <div class="kartAltYazi">${gec.length} adet — hemen ilgilen</div></div>
      <div class="kart altin"><div class="kartEtiket">30 Gün İçinde Vadesi Gelen</div>
        <div class="kartDeger altin" data-sayac="${yak.reduce((t, x) => t + x.tutar, 0)}">${para(yak.reduce((t, x) => t + x.tutar, 0))}</div>
        <div class="kartAltYazi">${yak.length} adet</div></div>
    </div>
    <div class="kart" style="margin-bottom:14px"><div class="kartUst"><h3>Vade Takvimi</h3>
      <span class="kartNot">kırmızı çerçeve = vadesi geçti · altın = 30 gün içinde</span></div>
      <div class="vadeSerit">${[...gec, ...yak].slice(0, 14).map((x) => {
        const gecti = x.vade < bugunISO();
        return `<div class="vadeKart ${gecti ? "gec" : "yakin"}">
          <div class="ekBilgi">${KACT(x.tur)} · ${KACT(x.yon)}</div>
          <b>${para(x.tutar)}</b>
          <div>${KACT(x.unvan || x.banka || "—")}</div>
          <div class="ekBilgi">${tarihKisa(x.vade)} ${gecti ? "· GECİKTİ" : ""}</div></div>`;
      }).join("") || '<div class="bos">Yakın vadede çek/senet yok.</div>'}</div></div>
    <div class="sagSut">
      <div>${tablo(["Tür", "Yön", "No", "Cari", "Banka", "Tutar", "Vade", "Durum", "İşlem"],
        (d.kayit || []).map((x) => [x.tur, x.yon, x.no, x.unvan || "—", x.banka || "—",
          { hucre: para(x.tutar), sinif: "para" }, tarihKisa(x.vade), { hucre: damga(x) },
          { hucre: `<div class="islemHucre"><button class="dugme kucuk" data-cek-dz="${x.id}">Düzenle</button>
            <button class="dugme kucuk kirmizi" data-cek-sl="${x.id}">Sil</button></div>` }]),
        { baslik: "Çek / Senet Listesi", yukseklik: "56vh", sagSutun: [5] })}</div>
      <div class="kart"><div class="kartUst"><h3>Hızlı İşlem</h3></div>
        <div class="kartAltYazi" style="margin-bottom:10px">Tahsil edilen çeki “Tahsil”, ödenen çeki “Ödendi” yap; durumu güncelleyince liste ve uyarılar anında değişir.</div>
        <div class="tusSatir"><button class="dugme birincil" id="cekYeni">+ Çek / Senet Ekle</button>
          <button class="dugme" id="cekWord">Word</button><button class="dugme" id="cekExcel">Excel</button>
          <button class="dugme altinDugme" id="cekPdf">PDF</button></div></div>
    </div>`;
  $("#cekYeni").onclick = () => cekForm(null);
  $$("[data-cek-dz]").forEach((b) => (b.onclick = () => cekForm(d.kayit.find((x) => x.id === Number(b.dataset.cekDz)))));
  $$("[data-cek-sl]").forEach((b) => (b.onclick = () => {
    const x = d.kayit.find((y) => y.id === Number(b.dataset.cekSl));
    sil("cek", x.id, `${x.tur} ${x.no || ""} · ${para(x.tutar)}`, () => { rozetleriYenile(); ekranCiz("cek"); });
  }));
  $("#cekWord").onclick = () => indir("/api/disa-aktar?kaynak=cek&tur=docx");
  $("#cekExcel").onclick = () => indir("/api/disa-aktar?kaynak=cek&tur=xlsx");
  $("#cekPdf").onclick = () => indir("/api/pdf?kaynak=cek");
};

/* ============================================================ BÜTÇE */
async function butceForm(kayit) {
  const aln = [
    { ad: "Kategori (TÜMÜ = hepsi)", anahtar: "kategori", varsayilan: "TÜMÜ" },
    { ad: "Defter", anahtar: "defter", tur: "sec", secenekler: ["sade", "kurumsal"] },
    { ad: "Aylık Bütçe", anahtar: "tutar", tur: "sayi" },
    { ad: "Uyarı Yüzdesi", anahtar: "uyari_yuzde", tur: "sayi", varsayilan: 80 },
    { ad: "Dönem", anahtar: "donem", tur: "sec", secenekler: ["Aylik", "Yillik"] },
    { ad: "Aktif", anahtar: "aktif", tur: "sayi", varsayilan: 1 },
  ];
  modalAc(kayit ? "Bütçe Düzenle" : "Yeni Bütçe", alanlar(aln, kayit || { kategori: "TÜMÜ", defter: "sade", donem: "Aylik", uyari_yuzde: 80, aktif: 1 }), [
    { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
    { ad: "Kaydet", sinif: "birincil", tikla: async () => {
      const g = alanTopla();
      if (kayit) g.id = kayit.id;
      await api("/api/butce/kaydet", g); modalKapat(); bildir("Bütçe kaydedildi"); ekranCiz("butce");
    } },
  ]);
}
EKRANLAR.butce = async () => {
  const d = await api("/api/butce");
  const kayit = d.kayit || [];
  $("#icerik").innerHTML = `
    <div class="izgara k3" style="margin-bottom:14px">
      <div class="kart turkuaz"><div class="kartEtiket">Toplam Bütçe (bu ay)</div>
        <div class="kartDeger turkuaz" data-sayac="${d.toplam_butce}">${para(d.toplam_butce)}</div></div>
      <div class="kart pembe"><div class="kartEtiket">Harcanan</div>
        <div class="kartDeger pembe" data-sayac="${d.toplam_harcanan}">${para(d.toplam_harcanan)}</div></div>
      <div class="kart ${d.toplam_harcanan > d.toplam_butce ? "kirmizi" : "yesil"}"><div class="kartEtiket">Kalan</div>
        <div class="kartDeger" data-sayac="${d.toplam_butce - d.toplam_harcanan}">${para(d.toplam_butce - d.toplam_harcanan)}</div></div>
    </div>
    <div class="kart"><div class="kartUst"><h3>Kategori Bütçeleri</h3>
      <span class="kartNot">çubuk yeşilden kırmızıya: harcama arttıkça renk değişir</span></div>
      <div class="izgara k3">${kayit.map((b) => `
        <div class="kart ${b.durum === "aşıldı" ? "kirmizi" : b.durum === "uyarı" ? "altin" : "yesil"}">
          <div class="kartUst"><h3>${KACT(b.kategori || "TÜMÜ")}</h3>
            <span class="damgaYeni ${b.defter === "sade" ? "turkuaz" : "mor"}">${b.defter === "sade" ? "sade defter" : "kurumsal"}</span></div>
          <div class="kartDeger" style="font-size:calc(19px * var(--olcek))">${para(b.harcanan)} / ${para(b.tutar)}</div>
          <div class="butceCubuk ${b.durum === "aşıldı" ? "asildi" : b.durum === "uyarı" ? "uyari" : ""}">
            <i style="width:${Math.min(100, b.oran)}%"></i><span>%${sayi(b.oran)}</span></div>
          <div class="kartAltYazi" style="margin-top:9px">${b.kalan >= 0 ? "Kalan: " + para(b.kalan) : "AŞIM: " + para(Math.abs(b.kalan))}${b.durum !== "normal" ? " · " + (b.durum === "aşıldı" ? "BÜTÇE AŞILDI" : "uyarı eşiği geçildi") : ""}</div>
          <div class="islemHucre" style="margin-top:10px"><button class="dugme kucuk" data-but-dz="${b.id}">Düzenle</button>
            <button class="dugme kucuk kirmizi" data-but-sl="${b.id}">Sil</button></div>
        </div>`).join("") || '<div class="bos">Bütçe tanımlı değil — “Yeni Bütçe” ile ekle.</div>'}</div>
      <div class="tusSatir"><button class="dugme birincil" id="butYeni">+ Yeni Bütçe</button>
        <button class="dugme" id="butExcel">Excel</button><button class="dugme altinDugme" id="butPdf">PDF</button></div></div>`;
  $("#butYeni").onclick = () => butceForm(null);
  $$("[data-but-dz]").forEach((b) => (b.onclick = () => butceForm(kayit.find((x) => x.id === Number(b.dataset.butDz)))));
  $$("[data-but-sl]").forEach((b) => (b.onclick = () => {
    const x = kayit.find((y) => y.id === Number(b.dataset.butSl));
    sil("butce", x.id, x.kategori || "TÜMÜ", () => ekranCiz("butce"));
  }));
  $("#butExcel").onclick = () => indir("/api/disa-aktar?kaynak=butce&tur=xlsx");
  $("#butPdf").onclick = () => indir("/api/pdf?kaynak=butce");
};

/* ============================================================ TEKRARLAYAN & ABONELİK */
async function tekrarForm(kayit) {
  const h = await api("/api/hesap");
  const aln = [
    { ad: "Ad", anahtar: "ad", genis: true },
    { ad: "Tür", anahtar: "tur", tur: "sec", secenekler: ["gider", "gelir"] },
    { ad: "Kategori", anahtar: "kategori" },
    { ad: "Tutar", anahtar: "tutar", tur: "sayi" },
    { ad: "Sıklık", anahtar: "siklik", tur: "sec", secenekler: ["Aylik", "Haftalik", "Yillik"] },
    { ad: "Ayın Günü", anahtar: "gun", tur: "sayi", varsayilan: 1 },
    { ad: "Hesap", anahtar: "hesap_id", tur: "sec", secenekler: h.kayit.map((x) => x.id) },
    { ad: "Defter", anahtar: "defter", tur: "sec", secenekler: ["kurumsal", "sade"] },
    { ad: "Abonelik mi", anahtar: "abonelik", tur: "sayi", varsayilan: 0 },
    { ad: "Başlangıç", anahtar: "baslangic", tur: "date", varsayilan: bugunISO() },
    { ad: "Aktif", anahtar: "aktif", tur: "sayi", varsayilan: 1 },
    { ad: "Açıklama", anahtar: "aciklama", genis: true },
  ];
  modalAc(kayit ? "Tekrarlayan Kaydı Düzenle" : "Yeni Tekrarlayan Kayıt",
    alanlar(aln, kayit || { tur: "gider", siklik: "Aylik", gun: 1, defter: "kurumsal", aktif: 1, baslangic: bugunISO() }),
    [{ ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
     { ad: "Kaydet", sinif: "birincil", tikla: async () => {
       const g = alanTopla();
       if (kayit) g.id = kayit.id;
       await api("/api/tekrar/kaydet", g); modalKapat(); bildir("Tekrarlayan kayıt kaydedildi"); ekranCiz("tekrar");
     } }]);
}
EKRANLAR.tekrar = async () => {
  const d = await api("/api/tekrar");
  const k = d.kayit || [];
  const abone = k.filter((x) => x.abonelik);
  const aylikG = k.filter((x) => x.tur === "gelir" && x.aktif).reduce((t, x) => t + x.tutar, 0);
  const aylikS = k.filter((x) => x.tur === "gider" && x.aktif).reduce((t, x) => t + x.tutar, 0);
  $("#icerik").innerHTML = `
    <div class="izgara k4" style="margin-bottom:14px">
      <div class="kart turkuaz"><div class="kartEtiket">Aylık Sabit Gelir</div>
        <div class="kartDeger turkuaz" data-sayac="${aylikG}">${para(aylikG)}</div></div>
      <div class="kart pembe"><div class="kartEtiket">Aylık Sabit Gider</div>
        <div class="kartDeger pembe" data-sayac="${aylikS}">${para(aylikS)}</div></div>
      <div class="kart ${aylikG - aylikS >= 0 ? "yesil" : "kirmizi"}"><div class="kartEtiket">Sabit Net</div>
        <div class="kartDeger" data-sayac="${aylikG - aylikS}">${para(aylikG - aylikS)}</div></div>
      <div class="kart altin"><div class="kartEtiket">Yıllık Abonelik Yükü</div>
        <div class="kartDeger altin" data-sayac="${d.yillik_yuk}">${para(d.yillik_yuk)}</div>
        <div class="kartAltYazi">${abone.length} abonelik</div></div>
    </div>
    <div class="kart" style="margin-bottom:14px"><div class="kartUst"><h3>Otomatik İşleme</h3>
      <span class="kartNot">Program açılışında vadesi gelenler kendiliğinden deftere düşer</span></div>
      <div class="kartAltYazi">Elle denemek için düğmeye bas: vadesi gelmiş tekrarlayan kayıtlar gelir/gider defterine ve seçili hesaba işlenir.</div>
      <div class="tusSatir"><button class="dugme birincil" id="tekUygula">Vadesi Gelenleri Şimdi İşle</button>
        <button class="dugme" id="tekYeni">+ Yeni Tekrarlayan Kayıt</button>
        <button class="dugme altinDugme" id="tekPdf">PDF</button></div></div>
    <div class="sagSut">
      <div>${tablo(["Ad", "Tür", "Kategori", "Tutar", "Sıklık", "Gün", "Defter", "Son Uygulama", "İşlem"],
        k.map((x) => [x.ad, { hucre: `<span class="damgaYeni ${x.tur === "gelir" ? "yesil" : "kirmizi"}">${x.tur}</span>` },
          x.kategori || "—", { hucre: para(x.tutar), sinif: "para" }, x.siklik, x.gun,
          { hucre: `<span class="damgaYeni ${x.defter === "sade" ? "turkuaz" : "mor"}">${x.defter}</span>` },
          x.son_uygulama ? tarihKisa(x.son_uygulama) : "—",
          { hucre: `<div class="islemHucre"><button class="dugme kucuk" data-tek-dz="${x.id}">Düzenle</button>
            <button class="dugme kucuk kirmizi" data-tek-sl="${x.id}">Sil</button></div>` }]),
        { baslik: "Tekrarlayan Kayıtlar", yukseklik: "52vh", sagSutun: [3] })}</div>
      <div class="kart"><div class="kartUst"><h3>Abonelikler</h3><span class="kartNot">${abone.length} kalem · yıllık ${para(d.yillik_yuk)}</span></div>
        ${abone.map((a) => `<div class="halkaSatir" style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--cizgi)">
          <span>${KACT(a.ad)} <span class="ekBilgi">· ${KACT(a.kategori || "")} · her ayın ${a.gun}.</span></span>
          <b>${para(a.tutar)}</b></div>`).join("") || '<div class="bos">Abonelik kaydı yok.</div>'}</div>
    </div>`;
  $("#tekYeni").onclick = () => tekrarForm(null);
  $$("[data-tek-dz]").forEach((b) => (b.onclick = () => tekrarForm(k.find((x) => x.id === Number(b.dataset.tekDz)))));
  $$("[data-tek-sl]").forEach((b) => (b.onclick = () => {
    const x = k.find((y) => y.id === Number(b.dataset.tekSl));
    sil("tekrar", x.id, x.ad, () => ekranCiz("tekrar"));
  }));
  $("#tekUygula").onclick = async () => {
    const r = await api("/api/tekrar/uygula", {});
    bildir(r.adet ? `${r.adet} kayıt deftere işlendi: ${r.yazilan.join(", ")}` : "Vadesi gelmiş kayıt yok.");
    ekranCiz("tekrar");
  };
  $("#tekPdf").onclick = () => indir("/api/pdf?kaynak=tekrar");
};

/* ============================================================ GÖREVLER */
async function gorevForm(kayit) {
  const aln = [
    { ad: "Tarih", anahtar: "tarih", tur: "date", varsayilan: bugunISO() },
    { ad: "Başlık", anahtar: "baslik", genis: true },
    { ad: "Öncelik", anahtar: "oncelik", tur: "sec", secenekler: ["Yüksek", "Normal", "Düşük"] },
    { ad: "Durum", anahtar: "durum", tur: "sec", secenekler: ["Açık", "Tamamlandı", "İptal"] },
    { ad: "Detay", anahtar: "detay", genis: true },
  ];
  modalAc(kayit ? "Görevi Düzenle" : "Yeni Görev", alanlar(aln, kayit || { tarih: bugunISO(), oncelik: "Normal", durum: "Açık" }), [
    { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
    { ad: "Kaydet", sinif: "birincil", tikla: async () => {
      const g = alanTopla();
      if (kayit) g.id = kayit.id;
      await api("/api/gorev/kaydet", g); modalKapat(); bildir("Görev kaydedildi"); rozetleriYenile(); ekranCiz("gorev");
    } },
  ]);
}
EKRANLAR.gorev = async () => {
  const d = await api("/api/gorev");
  const k = d.kayit || [];
  const acik = k.filter((x) => x.durum === "Açık");
  const gec = acik.filter((x) => x.tarih < bugunISO());
  $("#icerik").innerHTML = `
    <div class="izgara k3" style="margin-bottom:14px">
      <div class="kart turkuaz"><div class="kartEtiket">Açık Görev</div><div class="kartDeger turkuaz" data-sayac="${acik.length}">${acik.length}</div></div>
      <div class="kart kirmizi"><div class="kartEtiket">Süresi Geçen</div><div class="kartDeger kirmizi uyariNabiz" data-sayac="${gec.length}">${gec.length}</div></div>
      <div class="kart yesil"><div class="kartEtiket">Tamamlanan</div><div class="kartDeger yesil" data-sayac="${k.filter((x) => x.durum === "Tamamlandı").length}">${k.filter((x) => x.durum === "Tamamlandı").length}</div></div>
    </div>
    <div class="kart"><div class="kartUst"><h3>Görev Listesi</h3><span class="kartNot">vergi · ödeme · sayım · takip</span></div>
      ${tablo(["Tarih", "Başlık", "Detay", "Öncelik", "Durum", "İşlem"],
        k.map((x) => [tarihKisa(x.tarih), x.baslik, x.detay || "—",
          { hucre: `<span class="damgaYeni ${x.oncelik === "Yüksek" ? "kirmizi" : x.oncelik === "Düşük" ? "gri" : "altin"}">${KACT(x.oncelik)}</span>` },
          { hucre: `<span class="damgaYeni ${x.durum === "Tamamlandı" ? "yesil" : x.durum === "İptal" ? "gri" : (x.tarih < bugunISO() ? "kirmizi" : "turkuaz")}">${KACT(x.durum)}${x.durum === "Açık" && x.tarih < bugunISO() ? " · gecikti" : ""}</span>` },
          { hucre: `<div class="islemHucre">
            ${x.durum === "Açık" ? `<button class="dugme kucuk yesilDugme" data-gor2-tam="${x.id}">Tamamla</button>` : ""}
            <button class="dugme kucuk" data-gor2-dz="${x.id}">Düzenle</button>
            <button class="dugme kucuk kirmizi" data-gor2-sl="${x.id}">Sil</button></div>` }]),
        { baslik: "Görevler", yukseklik: "56vh" })}
      <div class="tusSatir"><button class="dugme birincil" id="gorevYeni">+ Yeni Görev</button>
        <button class="dugme" id="gorevExcel">Excel</button><button class="dugme altinDugme" id="gorevPdf">PDF</button></div></div>`;
  $("#gorevYeni").onclick = () => gorevForm(null);
  $$("[data-gor2-dz]").forEach((b) => (b.onclick = () => gorevForm(k.find((x) => x.id === Number(b.dataset.gor2Dz)))));
  $$("[data-gor2-tam]").forEach((b) => (b.onclick = async () => {
    const x = k.find((y) => y.id === Number(b.dataset.gor2Tam));
    await api("/api/gorev/kaydet", { id: x.id, tarih: x.tarih, baslik: x.baslik, detay: x.detay, oncelik: x.oncelik, durum: "Tamamlandı" });
    bildir("Görev tamamlandı"); rozetleriYenile(); ekranCiz("gorev");
  }));
  $$("[data-gor2-sl]").forEach((b) => (b.onclick = () => {
    const x = k.find((y) => y.id === Number(b.dataset.gor2Sl));
    sil("gorev", x.id, x.baslik, () => { rozetleriYenile(); ekranCiz("gorev"); });
  }));
  $("#gorevExcel").onclick = () => indir("/api/disa-aktar?kaynak=gorev&tur=xlsx");
  $("#gorevPdf").onclick = () => indir("/api/pdf?kaynak=gorev");
};

/* ============================================================ MUHASEBE ASİSTANI */
let SOHBET = [];
EKRANLAR.ai = async () => {
  const d = await api("/api/ai/durum");
  const hazir = d.modul && d.anahtar;
  $("#icerik").innerHTML = `
    <div class="sagSut">
      <div class="kart">
        <div class="kartUst"><h3>Muhasebe Asistanı</h3>
          <span class="damgaYeni ${hazir ? "yesil" : "kirmizi"}">${hazir ? "hazır · " + KACT(d.model) : "anahtar gerekli"}</span></div>
        <div class="sohbet" id="sohbet">${SOHBET.length ? "" : `<div class="balon o"><b>Merhaba Kenan.</b>
Defterindeki GERÇEK sayılarla cevap veriyorum — uydurmam. Şunları sorabilirsin:
• “Bu ay net durumum ne?”
• “Nerede çok harcıyorum, kısmam gereken yer neresi?”
• “Önümüzdeki ay kasam ne olur?”
• “Hangi çeklerin vadesi geçti?”
• “Giderleri nasıl azaltabilirim, somut plan ver.”</div>`}</div>
        <div class="soruSatir"><input id="aiSoru" type="text" placeholder="Sorunu yaz… (ör. bu ay en çok nereye para gitti)">
          <button class="dugme birincil" id="aiGonder">Sor</button></div>
      </div>
      <div class="kart"><div class="kartUst"><h3>Anahtar & Ayarlar</h3></div>
        <div class="kartAltYazi" style="margin-bottom:10px">Gemini API anahtarını buradan gir; anahtar yalnızca kendi bilgisayarındaki
        <b>veri/ai.json</b> dosyasında durur, hiçbir yere gönderilmez (Google'a sadece soru + defter özeti gider).</div>
        <div class="alan"><label>Gemini API Anahtarı</label><input id="aiAnahtar" type="password" placeholder="AIza…"></div>
        <div class="alan" style="margin-top:9px"><label>Model</label>
          <select id="aiModel">
            ${["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"].map((m) => `<option ${m === d.model ? "selected" : ""}>${m}</option>`).join("")}
          </select></div>
        <div class="tusSatir"><button class="dugme birincil" id="aiKaydet">Anahtarı Kaydet</button>
          <button class="dugme" id="aiTemizle">Sohbeti Temizle</button></div>
        <div class="kartAltYazi" style="margin-top:10px">Anahtar yoksa da program çalışır; asistan kapalı kalır.</div></div>
    </div>`;
  const ciz = () => {
    const s = $("#sohbet");
    s.innerHTML = SOHBET.map((m) => `<div class="balon ${m.rol === "ben" ? "ben" : "o"}">${m.rol === "ben" ? KACT(m.metin) : m.metin}</div>`).join("");
    s.scrollTop = s.scrollHeight;
  };
  if (SOHBET.length) ciz();
  const gonder = async () => {
    const soru = $("#aiSoru").value.trim();
    if (!soru) return;
    SOHBET.push({ rol: "ben", metin: soru });
    $("#aiSoru").value = "";
    ciz();
    SOHBET.push({ rol: "o", metin: "…düşünüyorum" });
    ciz();
    try {
      const r = await api("/api/ai/sor", { soru });
      SOHBET.pop();
      SOHBET.push({ rol: "o", metin: r.tamam ? KACT(r.cevap).replace(/\n/g, "<br>") : "⚠ " + KACT(r.hata || "cevap alınamadı") });
    } catch (e) {
      SOHBET.pop();
      SOHBET.push({ rol: "o", metin: "⚠ " + KACT(e.message) });
    }
    ciz();
  };
  $("#aiGonder").onclick = gonder;
  $("#aiSoru").onkeydown = (e) => { if (e.key === "Enter") gonder(); };
  $("#aiKaydet").onclick = async () => {
    const a = $("#aiAnahtar").value.trim();
    if (!a) { bildir("Anahtar boş", true); return; }
    bildir("Anahtar doğrulanıyor…");
    const r = await api("/api/ai/anahtar", { anahtar: a, model: $("#aiModel").value });
    bildir(r.tamam ? "Anahtar kaydedildi ve doğrulandı" : "Kaydedildi ama doğrulanamadı: " + (r.hata || ""), !r.tamam);
    ekranCiz("ai");
  };
  $("#aiTemizle").onclick = () => { SOHBET = []; ekranCiz("ai"); };
};

/* ============================================================ FİŞ & FATURA FOTOĞRAFI */
EKRANLAR.fis = async () => {
  const d = await api("/api/fis");
  const k = d.kayit || [];
  $("#icerik").innerHTML = `
    <div class="kart" style="margin-bottom:14px"><div class="kartUst"><h3>Fiş / Fatura Fotoğrafı Yükle</h3>
      <span class="damgaYeni ${d.ocr ? "yesil" : "altin"}">${d.ocr ? "OCR açık (Tesseract bulundu)" : "OCR kapalı — tutarı elle gir"}</span></div>
      <div class="kartAltYazi" style="margin-bottom:10px">Telefonla çektiğin fişin fotoğrafını seç; tutar ve açıklamayı yaz. Kaydettikten sonra
      “Deftere İşle” ile sade deftere gider olarak düşer. ${d.ocr ? "" : "<b>Not:</b> Bu bilgisayarda Tesseract kurulu değil, bu yüzden tutarı program okuyamıyor — sen yazıyorsun."}</div>
      <div class="izgara k3">
        <div class="alan"><label>Fotoğraf</label><input type="file" id="fisDosya" accept="image/*"></div>
        <div class="alan"><label>Tutar</label><input id="fisTutar" type="number" step="0.01" placeholder="149,90"></div>
        <div class="alan"><label>Kategori</label>
          <select id="fisKat">${["Market", "Yemek & Kafe", "Yakıt", "Kira", "Elektrik & Su", "İnternet & Telefon",
            "Kıyafet", "Sağlık", "Eğitim", "Kuaför & Bakım", "Kurumsal Alış", "Diğer"].map((x) => `<option>${x}</option>`).join("")}</select></div>
        <div class="alan" style="grid-column:span 2"><label>Açıklama</label><input id="fisAck" placeholder="ör. hırdavat fişi"></div>
        <div class="alan"><label>Tarih</label><input id="fisTarih" type="date" value="${bugunISO()}"></div>
      </div>
      <div class="tusSatir"><button class="dugme birincil" id="fisYukle">Yükle ve Kaydet</button></div></div>
    <div class="kart"><div class="kartUst"><h3>Yüklenen Fişler</h3><span class="kartNot">${k.length} kayıt</span></div>
      <div class="fisIzgara">${k.map((x) => `<div class="fisKart">
          <img src="/veri/fisler/${encodeURIComponent(x.dosya)}" alt="fiş" onerror="this.style.opacity=.25">
          <div><b>${para(x.tutar)}</b> · ${KACT(x.kategori || "—")}<br>
            <span class="ekBilgi">${tarihKisa(x.tarih)} · ${KACT(x.durum)}</span>
            <div class="islemHucre" style="margin-top:7px">
              ${x.durum !== "İşlendi" ? `<button class="dugme kucuk yesilDugme" data-fis-isle="${x.id}">Deftere İşle</button>` : ""}
              <button class="dugme kucuk kirmizi" data-fis-sl="${x.id}">Sil</button></div></div></div>`).join("")
        || '<div class="bos">Henüz fiş yüklenmedi.</div>'}</div></div>`;
  $("#fisYukle").onclick = async () => {
    const f = $("#fisDosya").files[0];
    if (!f) { bildir("Önce fotoğraf seç", true); return; }
    const okuyucu = new FileReader();
    okuyucu.onload = async () => {
      try {
        const r = await api("/api/fis/yukle", { ad: f.name, veri: okuyucu.result, tutar: $("#fisTutar").value,
          kategori: $("#fisKat").value, aciklama: $("#fisAck").value, tarih: $("#fisTarih").value });
        bildir(r.ocr ? "Yüklendi ve OCR ile okundu" : "Yüklendi — tutar elle girildi");
      } catch (e) { bildir("Yüklenemedi: " + e.message, true); }
      ekranCiz("fis");
    };
    okuyucu.readAsDataURL(f);
  };
  $$("[data-fis-isle]").forEach((b) => (b.onclick = async () => {
    await api("/api/fis/isle", { id: Number(b.dataset.fisIsle) });
    bildir("Sade deftere gider olarak işlendi"); ekranCiz("fis");
  }));
  $$("[data-fis-sl]").forEach((b) => (b.onclick = () => sil("fis", Number(b.dataset.fisSl), "fiş kaydı", () => ekranCiz("fis"))));
};

/* ============================================================ PUANTAJ (personel ekranına eklenir) */
async function puantajKarti() {
  const d = await api("/api/puantaj");
  const k = d.kayit || [];
  return `<div class="kart" style="margin-top:14px"><div class="kartUst"><h3>Puantaj · Avans / Prim / İzin</h3>
      <span class="kartNot">avans ${para(d.avans_toplam)} · prim ${para(d.prim_toplam)} · izin ${sayi(d.izin_gun)} gün</span></div>
    ${tablo(["Tarih", "Personel", "Tür", "Tutar", "Gün", "Açıklama", "İşlem"],
    k.map((x) => [tarihKisa(x.tarih), x.ad || "—",
      { hucre: `<span class="damgaYeni ${x.tur === "Avans" ? "altin" : x.tur === "Prim" ? "yesil" : x.tur === "İzin" ? "turkuaz" : "mor"}">${KACT(x.tur)}</span>` },
      { hucre: para(x.tutar), sinif: "para" }, x.gun || "—", x.aciklama || "—",
      { hucre: `<div class="islemHucre"><button class="dugme kucuk" data-pua-dz="${x.id}">Düzenle</button>
        <button class="dugme kucuk kirmizi" data-pua-sl="${x.id}">Sil</button></div>` }]),
    { baslik: "Puantaj Kayıtları", yukseklik: "32vh", sagSutun: [3] })}
    <div class="tusSatir"><button class="dugme birincil" id="puaYeni">+ Puantaj Kaydı</button>
      <button class="dugme" id="puaPdf">PDF</button></div></div>`;
}
async function puantajForm(kayit) {
  const p = await api("/api/personel");
  const aln = [
    { ad: "Personel", anahtar: "personel_id", tur: "sec", secenekler: p.kayit.map((x) => x.id) },
    { ad: "Tarih", anahtar: "tarih", tur: "date", varsayilan: bugunISO() },
    { ad: "Tür", anahtar: "tur", tur: "sec", secenekler: ["Avans", "Prim", "İzin", "Devamsızlık", "Fazla Mesai"] },
    { ad: "Tutar", anahtar: "tutar", tur: "sayi" },
    { ad: "Gün", anahtar: "gun", tur: "sayi" },
    { ad: "Açıklama", anahtar: "aciklama", genis: true },
  ];
  modalAc(kayit ? "Puantaj Düzenle" : "Yeni Puantaj Kaydı", alanlar(aln, kayit || { tarih: bugunISO(), tur: "Avans" }), [
    { ad: "Vazgeç", sinif: "cizgisiz", tikla: modalKapat },
    { ad: "Kaydet", sinif: "birincil", tikla: async () => {
      const g = alanTopla();
      if (kayit) g.id = kayit.id;
      await api("/api/puantaj/kaydet", g); modalKapat(); bildir("Puantaj kaydedildi");
      DURUM.ekran === "personel" ? ekranCiz("personel") : ekranCiz("personel");
    } },
  ]);
}
function puantajBagla() {
  const pua = (DURUM.puantaj || []);
  $("#puaYeni") && ($("#puaYeni").onclick = () => puantajForm(null));
  $$("[data-pua-dz]").forEach((b) => (b.onclick = () => puantajForm(pua.find((x) => x.id === Number(b.dataset.puaDz)))));
  $$("[data-pua-sl]").forEach((b) => (b.onclick = () => sil("puantaj", Number(b.dataset.puaSl), "puantaj kaydı", () => ekranCiz("personel"))));
  $("#puaPdf") && ($("#puaPdf").onclick = () => indir("/api/pdf?kaynak=puantaj"));
}

baslat().then(olaylar);
