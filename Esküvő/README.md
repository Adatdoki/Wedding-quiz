# Esküvői Kvíz - Vidám Csapatverseny

## 🎉 Áttekintés

Ez egy QR kódos esküvői kvíz webalkalmazás, amely párválasztással, számszavazásos játékmenettel és kvízkérdésekkel szórakoztatja a vendégeket. A játék célja, hogy az emberek interakcióba lépjenek egymással és vidám hangulatot teremtsen az esküvői ünnepségen.

## 🚀 Éles Alkalmazás

**Frontend URL:** https://vabxqdck.manus.space
**Backend API URL:** https://mzhyi8cdpkv0.manus.space

## 🎮 Játékszabályok

### 1. Regisztráció
- A vendégek QR kód beszkennelésével vagy közvetlenül a weboldalon regisztrálnak
- Minden játékos automatikusan kap egy vicces esküvői becenevet (pl. "Koszorúslány", "Virágszóró")

### 2. Párválasztás
- A játékosok egymásra kattintva választanak partnert
- Aki előbb kattint, annak lesz társa (1 század pontossággal)
- Páratlan számú játékos esetén egy játékos pár nélkül marad

### 3. Számszavazás
- Minden csapat szavaz egy 0-nál nagyobb egész számra
- Az nyer, aki a legkisebbet választotta, amire más nem szavazott
- Döntetlen esetén senki sem nyer, de mindenki iszik 🍻

### 4. Csapat Rablás
- A nyertes csapat kvízkérdést kap az ifjú párról
- Helyes válasz esetén rabolhatnak egy játékost más csapatból
- A csapat bővülés örömére a tagok isznak egy italt

### 5. Kiesés és Győzelem
- Az egyedül maradt csapat kiesik
- A játék addig folytatódik, míg csak egy csapat marad
- A győztes csapat 2-t iszik a győzelem örömére! 🎉

## 🛠️ Technikai Részletek

### Frontend
- **Technológia:** React + Vite
- **Styling:** Tailwind CSS + Shadcn/UI
- **Ikonok:** Lucide React
- **Responsive design:** Mobil és desktop támogatás

### Backend
- **Technológia:** Flask + SQLAlchemy
- **Adatbázis:** SQLite
- **API:** RESTful endpoints
- **CORS:** Engedélyezett minden origin számára

### Főbb Funkciók
- ✅ Játékos regisztráció automatikus becenév generálással
- ✅ Párválasztás valós idejű szinkronizációval
- ✅ Számszavazás és kiértékelés
- ✅ Kvízkérdések az ifjú párról
- ✅ Csapat rablás mechanika
- ✅ Automatikus kiesés és győzelem kezelés
- ✅ Responsive UI mobil és desktop eszközökön

## 📱 Használat

1. **QR kód generálás:** Készíts QR kódot a frontend URL-hez
2. **Vendégek regisztrációja:** A vendégek beszkennelhetik a QR kódot vagy közvetlenül megnyithatják a linket
3. **Játék indítása:** Amikor elegendő játékos regisztrált, kezdődhet a párválasztás
4. **Játékmenet:** Kövesd a képernyőn megjelenő utasításokat

## 🎨 Vicces Elemek

### Automatikus Becenevek
- Koszorúslány, Virágszóró, Gyűrű-hordó
- Násznép, Mátka, Legény
- Anyós, Após, Keresztapa

### Csapatnevek (Tervezett)
- Tüllkommandó
- Csokornyakkendő-maffia
- Lakodalmas Lámák
- Menyasszonyi Maffia
- Vőlegény Bandája

### Kvízkérdések Példák
- "Hol volt az első randijuk?"
- "Ki mondta ki először: 'Szeretlek'?"
- "Mi a pár közös kedvenc sorozata?"
- "Hány gyereket terveznek?"

## 🔧 Fejlesztői Információk

### Projekt Struktúra
```
wedding-quiz-app/
├── frontend/          # React alkalmazás
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.jsx
│   └── dist/          # Build output
└── backend/           # Flask API
    ├── src/
    │   ├── models/
    │   ├── routes/
    │   └── main.py
    └── populate_db.py  # Adatbázis feltöltő script
```

### API Végpontok
- `POST /api/register` - Játékos regisztráció
- `GET /api/players` - Aktív játékosok listája
- `GET /api/game/state` - Játék állapot
- `POST /api/pair` - Pár létrehozása
- `POST /api/vote` - Szavazat leadása
- `POST /api/quiz/question` - Kvízkérdés lekérése
- `POST /api/steal-player` - Játékos rablása

### Lokális Fejlesztés
```bash
# Backend indítása
cd backend
source venv/bin/activate
python src/main.py

# Frontend indítása
cd frontend
pnpm install
pnpm run dev
```

## 🎯 Jövőbeli Fejlesztési Lehetőségek

1. **"Dupla vagy semmi" Power-up:** Nyerés esetén két embert is rabolhatnak
2. **Egyedi kvízkérdések:** Testreszabható kérdések az ifjú párról
3. **Hangeffektek:** Vidám hangok a különböző eseményekhez
4. **Statisztikák:** Játék végén részletes eredmények
5. **Többnyelvű támogatás:** Angol, német, stb.
6. **Admin panel:** Játékmester felület a játék irányításához

## 📞 Támogatás

Ha bármilyen kérdésed van vagy problémába ütközöl, nyugodtan keress!

---

**Készítette:** Manus AI Agent
**Verzió:** 1.0.0
**Utolsó frissítés:** 2025. augusztus 19.

Jó szórakozást az esküvői kvízzel! 🎊💒

