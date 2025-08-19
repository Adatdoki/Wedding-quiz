# 🎊 Esküvői Kvíz - Vidám Csapatverseny v2.0

Egy interaktív, QR kódos esküvői játék szurkolói token rendszerrel, moderátor panellel és fejlett csapat balansz algoritmusokkal.

## 🎯 **ÚJ v2.0 FUNKCIÓK**

### 🗳️ **Forradalmi Szavazási Rendszer**
- **30 másodperces nyílt szavazás** - bárhányszor változtatható a szám
- **Egyhangúság elve**: Ha minden csapattag ugyanarra szavaz → az érvényesül  
- **Legkisebb szám szabály**: Különben a legkisebb szám a csapat végső száma
- **Valós idejű visszajelzés**: 
  - "Egyhangúság kész: 7" ✅
  - "Legkisebb jelenleg: 5" 📊
- **Grace period**: 300ms késleltetés a késői kattintásokra

### 🎪 **Szurkolói Token Rendszer**
- Kiesett játékosok **tippelhetnek** a nyerő csapat számára
- Helyes tipp esetén **visszatérés a legkisebb csapatba**
- Automatikus **balansz** - megakadályozza a "snowball" effektust
- **Comeback lehetőség** az underdog csapatoknak

### 🛡️ **Moderátor Panel** (Titkos kód: `MODERATOR2025`)
- **Játék vezérlés**: kör indítás, szünet, újraindítás
- **Ital szünet koordináció**: üzenet küldés és időzítés 🍻
- **Manuális csapatváltás**: játékosok áthelyezése
- **Valós idejű statisztikák**: játékosok, csapatok, tokenek
- **Moderátor akciók naplózása**

### ⚖️ **Intelligens Csapat Balansz**
- **Legkisebb csapat szabály**: új játékosok automatikusan ide kerülnek
- **Snowball effect megelőzés**: túl erős csapatok korlátozása
- **Automatikus kiegyensúlyozás**: nagy különbségek csökkentése

## 🎮 **Játékszabályok**

### 1️⃣ **Regisztráció**
- QR kód beszkennelése vagy közvetlen link
- Automatikus vicces becenév generálás (Koszorúslány, Vőfély, stb.)

### 2️⃣ **Párválasztás** 
- Kattintás másik játékosra → csapatképzés
- Aki előbb kattint, annak lesz társa
- Páratlan esetén egy játékos egyedül marad

### 3️⃣ **Szavazási Kör** (ÚJ!)
```
⏰ 30 másodperc nyílt szavazás
📱 Bárhányszor változtatható a szám (1-20)
👥 Egyhangú szavazat → az érvényesül
🔢 Különben → legkisebb szám
📊 Valós idejű "Egyhangúság" és "Legkisebb" jelzés
```

### 4️⃣ **Nyertes Meghatározás**
- **Legkisebb egyedi szám** nyer (amire más nem szavazott)
- Döntetlen esetén → **mindenki iszik!** 🍻

### 5️⃣ **Kvízkérdés**
- Nyertes csapat kvízkérdést kap az ifjú párról
- Helyes válasz → **játékos rablás** másik csapatból
- **Ital jutalom**: rablás → 1 ital 🍺

### 6️⃣ **Szurkolói Mód** 
- Kiesett játékosok **tippelhetnek** a következő nyertesre
- Helyes tipp → **visszatérés** a legkisebb csapatba
- **Balansz**: megakadályozza a túl erős csapatok dominanciáját

### 7️⃣ **Győzelem**
- Utolsó megmaradt csapat → **2 ital!** 🎉
- Új forduló indítható

## 🚀 **Éles Alkalmazás**

**🌐 Frontend URL:** https://vabxqdck.manus.space  
**🔧 Backend API URL:** https://mzhyi8cdpkv0.manus.space

**📱 QR Kód generálás:** Bármely QR generátorral a frontend URL-hez

## 🛠️ **Technikai Részletek**

### Backend API végpontok:
```
POST /api/register              - Játékos regisztráció
GET  /api/game/state           - Játék állapot lekérése
POST /api/vote/submit          - Szavazat leadása/módosítása
GET  /api/vote/team-status/<id> - Csapat szavazási állapot
GET  /api/vote/round-status    - Teljes kör állapot
POST /api/vote/finalize        - Szavazás lezárása
GET  /api/supporter/tokens     - Szurkolói tokenek
POST /api/supporter/predict    - Tipp leadása
POST /api/supporter/rejoin     - Visszatérés tokennel
POST /api/moderator/authenticate - Moderátor belépés
GET  /api/moderator/stats      - Játék statisztikák
POST /api/moderator/start-round - Új kör indítása
POST /api/moderator/pause-game - Játék szünet
POST /api/moderator/drink-break - Ital szünet
GET  /api/balance/check        - Csapat balansz ellenőrzés
```

### Adatbázis modellek:
- **Player**: játékosok egyedi session ID-val
- **Team**: csapatok tagszám követéssel  
- **Game**: játékok állapot kezeléssel
- **Round**: körök időzítéssel és szavazási logikával
- **Vote**: egyéni szavazatok player_id + updated_at mezőkkel
- **SupporterToken**: szurkolói tokenek tippelési adatokkal
- **ModeratorAction**: moderátor akciók naplózása

### Frontend komponensek:
- **Regisztrációs képernyő**
- **Párválasztó felület**  
- **Szavazási képernyő** (ÚJ 30mp logikával)
- **Kvíz képernyő**
- **Szurkolói képernyő** (ÚJ)
- **Moderátor panel** (ÚJ)
- **Valós idejű állapot frissítés**

## 🎊 **Használati Útmutató**

### Játékosoknak:
1. **QR kód** beszkennelése vagy link megnyitása
2. **Regisztráció** → automatikus becenév
3. **Párválasztás** → kattintás másik játékosra
4. **Szavazás** → 30 mp alatt bárhányszor változtatható
5. **Kvíz** → nyertes csapat válaszol
6. **Szurkolás** → kiesés után tippelés

### Moderátornak:
1. **Titkos kód**: `MODERATOR2025`
2. **Kör indítás** → új szavazási kör
3. **Ital szünet** → koordinált szünet üzenettel
4. **Manuális beavatkozás** → játékos áthelyezés
5. **Statisztikák** → valós idejű követés

## 🍻 **Ital Szabályok**

- **Rablás után**: 1 ital a nyertes csapatnak
- **Döntetlen**: mindenki iszik
- **Győzelem**: 2 ital az utolsó csapatnak
- **Szurkolói visszatérés**: ünneplés → 1 ital

## 🎯 **Miért jó ez a szavazási rendszer?**

✅ **Egyszerű**: Nincs kapitány, nincs bonyolult szabály  
⚡ **Gyors**: 30 mp alatt mindenki szavaz  
🤝 **Kooperatív**: Egyhangúság → azonnali siker  
🎲 **Determinisztikus**: Legkisebb szám → mindig egyértelmű  
📱 **Mobil-barát**: Valós idejű visszajelzés  
🎪 **Szórakoztató**: Nyílt szavazás → kevesebb vita

---

**🎊 Jó szórakozást az esküvői kvízzel!**

*Fejlesztő: Az új szavazási rendszer a felhasználó zseniális ötlete alapján készült!* 🧠✨

