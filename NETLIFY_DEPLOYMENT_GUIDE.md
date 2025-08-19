# 🎯 Esküvői Kvíz - Netlify Deployment Útmutató

## 📦 Csomag Tartalma

Ez a csomag tartalmazza a teljes Esküvői Kvíz alkalmazást:
- ✅ **Frontend**: React alkalmazás (már buildelt)
- ✅ **Backend**: Flask API szerver
- ✅ **Gyorsítási beállítások**: 20mp szavazás, sprint mód, védettség ki/be
- ✅ **Szurkolói token rendszer**: Kiesett játékosok visszatérése
- ✅ **Moderátor panel**: Játék vezérlés

## 🚀 Netlify Deployment Lépések

### 1. Frontend Deployment (Netlify)

1. **Lépj be a Netlify-ba**: https://netlify.com
2. **"Add new site" → "Deploy manually"**
3. **Húzd be a `frontend/dist` mappát** (nem az egész frontend mappát!)
4. **Site settings → Change site name** (opcionális)
5. **Deployment complete!** ✅

### 2. Backend Deployment Opciók

#### Opció A: Heroku (Ajánlott)
1. **Heroku account** létrehozása
2. **Heroku CLI** telepítése
3. **Backend mappa** feltöltése:
   ```bash
   cd backend
   git init
   heroku create your-app-name
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

#### Opció B: Railway
1. **Railway.app** regisztráció
2. **"Deploy from GitHub"** vagy **"Deploy from local"**
3. **Backend mappa** kiválasztása
4. **Automatic deployment** ✅

#### Opció C: Render
1. **Render.com** regisztráció
2. **"New Web Service"**
3. **Backend mappa** feltöltése
4. **Python environment** automatikus felismerés

### 3. API URL Frissítése

A backend deployment után:

1. **Másold a backend URL-t** (pl. `https://your-app.herokuapp.com`)
2. **Szerkeszd a `frontend/src/services/api.js` fájlt**:
   ```javascript
   const API_BASE_URL = 'https://your-backend-url.herokuapp.com/api'
   ```
3. **Build újra a frontend-et**:
   ```bash
   cd frontend
   npm run build
   ```
4. **Húzd be újra a `dist` mappát** Netlify-ra

## ⚙️ Környezeti Változók (Backend)

Ha szükséges, állítsd be ezeket:
```
FLASK_ENV=production
DATABASE_URL=sqlite:///app.db
SECRET_KEY=your-secret-key-here
```

## 🎮 Játék Beállítások

### Moderátor Kód
```
MODERATOR2025
```

### Gyorsítási Presets
- **Normal**: 20mp, védettség be, 1-20 számok
- **Sprint**: 15mp, védettség ki, 1-25 számok  
- **Fast**: 20mp, védettség ki, 1-25 számok

### API Végpontok (Teszteléshez)
```
GET  /api/game/state           - Játék állapot
POST /api/register             - Regisztráció
POST /api/vote/submit          - Szavazás
GET  /api/settings/get         - Beállítások
POST /api/settings/update      - Beállítások módosítása
```

## 🔧 Hibaelhárítás

### Frontend nem töltődik be
- Ellenőrizd, hogy a `dist` mappát töltötted-e fel
- Netlify build settings: **Build command**: `npm run build`, **Publish directory**: `dist`

### Backend nem elérhető
- Ellenőrizd a backend URL-t
- Nézd meg a backend logs-okat
- CORS beállítások ellenőrzése

### API hívások sikertelenek
- Frissítsd az API_BASE_URL-t a frontend kódban
- Ellenőrizd, hogy a backend fut-e
- Network tab a böngésző dev tools-ban

## 📱 QR Kód Generálás

A játékhoz QR kódot generálhatsz:
1. **Frontend URL** (pl. `https://your-site.netlify.app`)
2. **QR generátor**: https://qr-code-generator.com
3. **Nyomtatás** és kihelyezés az esküvőn

## 🎊 Játék Indítása

1. **QR kód** kiosztása a vendégeknek
2. **Moderátor panel** megnyitása (titkos kód: `MODERATOR2025`)
3. **Beállítások** kiválasztása (Normal/Sprint/Fast)
4. **Játék indítása** és élvezet! 🍻

## 📞 Támogatás

Ha bármi probléma van:
- Ellenőrizd a browser console-t (F12)
- Nézd meg a backend logs-okat
- API végpontokat teszteld Postman-nel

**Jó szórakozást az esküvői kvízzel!** 💒🎉

