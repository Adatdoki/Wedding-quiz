# Esküvői Kvíz - Változásnapló

## v2.0.0 - Kibővített Funkciók (2025-08-19)

### 🎯 **ÚJ SZAVAZÁSI RENDSZER**
- **30 másodperces nyílt szavazás** - bárhányszor változtatható
- **Egyhangúság elve**: Ha minden csapattag ugyanarra szavaz → az érvényesül
- **Legkisebb szám szabály**: Különben a legkisebb szám a csapat végső száma
- **Valós idejű visszajelzés**: "Egyhangúság kész: 7" / "Legkisebb jelenleg: 5"
- **Grace period**: 300ms késleltetés a késői kattintásokra

### 🎪 **SZURKOLÓI TOKEN RENDSZER**
- **Kiesett játékosok tippelhetnek** a nyerő csapat számára
- **Helyes tipp esetén**: visszatérés a legkisebb csapatba
- **Automatikus balansz**: megakadályozza a "snowball" effektust
- **Token követés**: minden token használat naplózva

### 🛡️ **MODERÁTOR PANEL**
- **Titkos kód**: `MODERATOR2025`
- **Játék vezérlés**: kör indítás, szünet, újraindítás
- **Ital szünet koordináció**: üzenet küldés és időzítés
- **Manuális csapatváltás**: játékosok áthelyezése
- **Valós idejű statisztikák**: játékosok, csapatok, tokenek
- **Moderátor akciók naplózása**

### ⚖️ **CSAPAT BALANSZ ALGORITMUS**
- **Legkisebb csapat szabály**: új játékosok automatikusan ide kerülnek
- **Snowball effect megelőzés**: túl erős csapatok korlátozása
- **Automatikus kiegyensúlyozás**: nagy különbségek csökkentése
- **Csapat egyensúly ellenőrzés**: API végpont a balansz monitorozásához

### 🔧 **TECHNIKAI FEJLESZTÉSEK**
- **Új Vote model**: egyéni szavazatok player_id-val
- **Round model bővítés**: voting_start_time, voting_duration_seconds
- **Új API végpontok**: `/api/vote/*`, `/api/balance/*`, `/api/moderator/*`
- **Valós idejű szavazás követés**: csapat státusz és időzítés
- **Grace period kezelés**: késői szavazatok kezelése

## v1.0.0 - Alapverzió (2025-08-19)

### ✅ **ALAPFUNKCIÓK**
- QR kódos regisztráció automatikus becenevekkel
- Párválasztás kattintás-alapú rendszerrel
- Számszavazás legkisebb egyedi szám algoritmussal
- Kvízkérdések az ifjú párról
- Csapat rablás nyertes csapatok számára
- Automatikus kiesés egyedül maradt csapatoknál
- Responsive design mobil és desktop támogatással

### 🎮 **JÁTÉKLOGIKA**
- Vicces esküvői becenevek generálása
- Csapatnevek: "Tüllkommandó", "Csokornyakkendő-maffia", stb.
- 15 előre elkészített kvízkérdés
- Ital jutalmak: rablás → 1 ital, győzelem → 2 ital

### 🚀 **DEPLOYMENT**
- Backend: Flask + SQLAlchemy + SQLite
- Frontend: React + Tailwind CSS + Shadcn/UI
- Éles URL-ek: Manus Cloud platformon

---

## 🎊 **Összesen implementált funkciók:**

### Backend API végpontok:
- `/api/register` - Játékos regisztráció
- `/api/game/state` - Játék állapot lekérése
- `/api/vote/submit` - Szavazat leadása/módosítása
- `/api/vote/team-status/<team_id>` - Csapat szavazási állapot
- `/api/vote/round-status` - Teljes kör állapot
- `/api/vote/finalize` - Szavazás lezárása
- `/api/supporter/*` - Szurkolói token rendszer
- `/api/moderator/*` - Moderátor funkciók
- `/api/balance/*` - Csapat balansz algoritmusok

### Frontend komponensek:
- Regisztrációs képernyő
- Párválasztó felület
- Szavazási képernyő (ÚJ logikával)
- Kvíz képernyő
- Szurkolói képernyő
- Moderátor panel
- Valós idejű állapot frissítés

### Adatbázis modellek:
- Player (játékosok)
- Team (csapatok)
- Game (játékok)
- Round (körök)
- Vote (szavazatok - ÚJ struktúra)
- QuizQuestion (kvízkérdések)
- SupporterToken (szurkolói tokenek)
- ModeratorAction (moderátor akciók)

---

**Fejlesztő megjegyzés**: Az új szavazási rendszer a felhasználó ötlete alapján készült, amely sokkal elegánsabb és praktikusabb megoldás, mint a korábbi kapitány-alapú rendszer. 🎯

