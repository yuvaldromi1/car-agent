# סוכן רכב משפחתי — קריית טבעון (MVP)

אפליקציית חיפוש רכבים משפחתיים יד שנייה בעברית RTL, עם ארכיטקטורת source adapters חוקית (ללא scraping אגרסיבי), דירוג מודעות, סינון רדיוס סביב קריית טבעון, והשוואת רכבים.

## מה קיים ב-MVP

- Backend ב-`FastAPI + SQLModel + SQLite`
- Frontend ב-`React + TypeScript + Vite + Tailwind`
- ממשק RTL בעברית
- מנוע חיפוש מודולרי לפי מקורות חוקיים:
  - `google_cse` (API חוקי)
  - `yad2_search_url` (קישור חיפוש ידני)
  - `carwiz_search_url` (קישור ידני)
  - `manual_url` (קישורים שהמשתמש שומר)
  - `dealership_manual` (אתרי סוכנויות שנשמרו)
- נרמול תוצאות → סינון רדיוס (Haversine) → דירוג והסבר בעברית → דה-דופליקציה

## מגבלות חוקיות (חשוב)

- אין עקיפת CAPTCHA / anti-bot
- אין scraping אגרסיבי של אתרים שאינם מאפשרים
- במקורות לא-אוטומטיים נשמרים קישורי חיפוש/מקור לבדיקה ידנית

## דרישות

- Python 3.11+ (נבדק גם על 3.14)
- Node.js 20+

## הגדרת סביבה

צור קובץ `.env` בשורש הפרויקט:

```env
DATABASE_URL=sqlite:///./car_agent.db
GOOGLE_CSE_ID=
GOOGLE_API_KEY=
NOMINATIM_USER_AGENT=CarAgentKiryatTivon/1.0 (contact: local-dev)
GEOCODING_ENABLED=false
```

> `GOOGLE_CSE_ID` ו-`GOOGLE_API_KEY` נדרשים להפעלת מקור Google.
> אם הם לא מוגדרים, המערכת מפעילה fallback חוקי (קישורי חיפוש/מקורות ידניים), אך נפח התוצאות האוטומטיות יהיה נמוך יותר.

לקוח ה-frontend תומך גם במשתני סביבה:

```env
VITE_API_BASE=
VITE_USE_MOCK=false
```

- השארת `VITE_API_BASE` ריק משתמשת ב-proxy של Vite ל-`http://127.0.0.1:8000`.
- `VITE_USE_MOCK=true` מפעיל מצב דמה (ללא קריאות שרת לרוב המסכים).

## הרצה מקומית

### 1) Backend

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

השרת יעלה ב-`http://127.0.0.1:8000`.

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

האפליקציה תעלה ב-`http://localhost:5173`.

## נקודות קצה מרכזיות

- Search:
  - `GET /search/profile`
  - `PUT /search/profile`
  - `POST /search/run`
  - `GET /search/runs`
  - `GET /search/runs/{id}`
- Listings:
  - `GET /listings`
  - `GET /listings/{id}`
  - `POST /listings`
  - `PUT /listings/{id}`
  - `DELETE /listings/{id}`
  - `POST /listings/import-csv`
  - `POST /listings/{id}/evaluate`
  - `POST /listings/deduplicate`
- Sources:
  - `GET /sources`
  - `POST /sources`
  - `PUT /sources/{id}`
  - `POST /sources/{id}/test`
- Dealerships:
  - `GET /dealerships`
  - `POST /dealerships`
  - `PUT /dealerships/{id}`
  - `DELETE /dealerships/{id}`

## CSV import

נתמכים שמות עמודות באנגלית/עברית (למשל `title`/`כותרת`, `price`/`מחיר`, `year`/`שנה`, `mileage`/`קילומטראז`, `source_url`/`url`/`קישור`).

## בדיקות בסיס שבוצעו

- `python -m compileall backend -q`
- `cd frontend && npm run build`

שני השלבים עברו בהצלחה.

