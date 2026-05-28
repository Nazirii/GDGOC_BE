# API Contract - Analys Product Flow

Dokumen ini dipakai sebagai acuan request/response untuk mock server dan frontend.

Catatan:
- Field `description` pada request create analysis tetap berupa teks singkat.
- Hasil analisis yang kompleks disimpan di `report.content` sebagai JSON.
- Endpoint detail analysis mengembalikan `report` + `design_references`.

Swagger docs:
- `/docs` (Swagger UI)
- `/redoc` (ReDoc)

## 0) Auth - Login

### Endpoint
`POST /api/auth/login`

### Request
```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

### Response 200
```json
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "bearer"
}
```

### Response 401
```json
{
  "detail": "Email atau password salah"
}
```

---

## 0) Auth - Register

### Endpoint
`POST /api/auth/register`

### Request
```json
{
  "email": "user@example.com",
  "password": "secret123",
  "full_name": "Alya Putri",
  "phone": "08123456789",
  "company_name": "Rajut Nusantara"
}
```

### Response 200
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Alya Putri",
  "phone": "08123456789",
  "company_name": "Rajut Nusantara",
  "created_at": "2026-05-27T12:49:43.994311",
  "updated_at": "2026-05-27T12:49:43.994311"
}
```

---

## 0) Auth - Logout

### Endpoint
`POST /api/auth/logout`

### Request
```json
{
  "refresh_token": "jwt_refresh_token"
}
```

### Response 200
```json
{
  "message": "Logout berhasil"
}
```

---

## 1) Create Analysis Product

### Endpoint
`POST /api/analys_products`

### Request
```json
{
  "category": "pakaian",
  "product_name": "Baju Rajut Wanita",
  "description": "Baju rajut wanita dengan gaya casual-premium, cocok untuk pasar Jepang dan Eropa. Fokus pada kenyamanan, tekstur halus, dan warna netral yang mudah dipadukan."
}
```

### Response 201
```json
{
  "id": 12,
  "user_id": 1,
  "category": "pakaian",
  "product_name": "Baju Rajut Wanita",
  "description": "Baju rajut wanita dengan gaya casual-premium, cocok untuk pasar Jepang dan Eropa. Fokus pada kenyamanan, tekstur halus, dan warna netral yang mudah dipadukan.",
  "image_url": null,
  "status": "pending",
  "created_at": "2026-05-27T12:49:43.994311",
  "updated_at": "2026-05-27T12:49:43.994311",
  "message": "Analisis sedang diproses, silakan cek kembali nanti"
}
```

### Response 404 / 401
```json
{
  "detail": "Produk tidak ditemukan"
}
```

---

## 2) Get Analysis Detail

### Endpoint
`GET /api/analys_products/{analys_product_id}`

### Response 200
```json
{
  "id": 12,
  "user_id": 1,
  "category": "pakaian",
  "product_name": "Baju Rajut Wanita",
  "description": "Baju rajut wanita dengan gaya casual-premium, cocok untuk pasar Jepang dan Eropa. Fokus pada kenyamanan, tekstur halus, dan warna netral yang mudah dipadukan.",
  "image_url": null,
  "status": "done",
  "created_at": "2026-05-27T12:49:43.994311",
  "updated_at": "2026-05-27T12:50:10.123456",
  "report": {
    "meta": {
      "version": "1.0",
      "generated_at": "2026-05-27T12:50:10Z",
      "analysis_status": "ready",
      "analys_product_id": 12,
      "product_count": 3
    },
    "summary": {
      "title": "Baju Rajut Wanita",
      "subtitle": "Analisis tren konsumen dan peluang ekspor untuk knitwear casual-premium",
      "recommended_market": {
        "primary": "Jepang",
        "alternatives": ["Korea Selatan", "Eropa"]
      },
      "export_readiness": {
        "score": 84,
        "label": "siap",
        "note": "Produk memiliki potensi tinggi karena kombinasi tekstur, warna netral, dan kenyamanan yang cocok untuk pasar urban."
      }
    },
    "sections": [
      {
        "type": "brainstorm",
        "title": "Saran BrainS",
        "items": [
          {
            "id": "brainstorm-1",
            "title": "Baju rajut Anda kuat di sisi kenyamanan",
            "content": "Pasar merespons positif pada knitwear yang ringan, hangat, dan punya siluet simpel."
          }
        ]
      },
      {
        "type": "sentiment_breakdown",
        "title": "Analisis Sentimen",
        "items": [
          { "aspect": "Tekstur", "value": 0.91 },
          { "aspect": "Kenyamanan", "value": 0.88 },
          { "aspect": "Warna", "value": 0.76 }
        ]
      },
      {
        "type": "seasonality",
        "title": "Musim Permintaan",
        "series": [
          { "month": "Jan", "value": 18 },
          { "month": "Feb", "value": 20 },
          { "month": "Mar", "value": 26 },
          { "month": "Apr", "value": 35 },
          { "month": "Mei", "value": 42 },
          { "month": "Jun", "value": 30 }
        ],
        "note": "Permintaan meningkat saat transisi musim dan cuaca dingin."
      },
      {
        "type": "favorite_colors",
        "title": "Warna Favorit",
        "items": [
          { "name": "Cream", "value": 0.41 },
          { "name": "Beige", "value": 0.34 },
          { "name": "Olive", "value": 0.25 }
        ]
      },
      {
        "type": "popular_comments",
        "title": "Komentar Populer",
        "items": ["hangat", "lembut", "simple", "mudah dipadukan"]
      },
      {
        "type": "pricing_reference",
        "title": "Referensi Harga",
        "items": [
          { "tier": "Eksklusif", "price_range": "Rp350rb - Rp520rb" },
          { "tier": "Umum", "price_range": "Rp180rb - Rp280rb" }
        ],
        "note": "Segmen premium cocok untuk knitwear dengan finishing rapi dan warna netral."
      },
      {
        "type": "opportunities",
        "title": "Celah Peluang",
        "items": [
          {
            "id": "opp-1",
            "title": "Knitwear warna netral",
            "content": "Fokus pada warna cream dan beige untuk memperkuat kesan premium dan mudah dipadu."
          },
          {
            "id": "opp-2",
            "title": "Versi layering",
            "content": "Buat varian yang cocok dipakai layering untuk memperluas segmentasi pasar urban."
          }
        ]
      }
    ],
    "sources": {
      "products": [
        { "product_id": 101, "name": "Baju Rajut A" },
        { "product_id": 102, "name": "Baju Rajut B" },
        { "product_id": 103, "name": "Baju Rajut C" }
      ],
      "insight_version": "2026-05-27"
    }
  },
  "design_references": [
    {
      "id": 1,
      "analys_product_id": 12,
      "title": "Soft Minimal Knit",
      "description": "Gaya rajut lembut dengan warna cream, cocok untuk tampilan minimalis modern.",
      "image_url": "https://example.com/images/soft-minimal-knit.jpg",
      "tags": ["cream", "minimal", "soft texture"],
      "sort_order": 0,
      "created_at": "2026-05-27T12:50:10.123456",
      "updated_at": "2026-05-27T12:50:10.123456"
    },
    {
      "id": 2,
      "analys_product_id": 12,
      "title": "Urban Cozy Layer",
      "description": "Inspirasi knitwear untuk layering style urban dengan warna beige dan olive.",
      "image_url": "https://example.com/images/urban-cozy-layer.jpg",
      "tags": ["beige", "layering", "urban"],
      "sort_order": 1,
      "created_at": "2026-05-27T12:50:10.123456",
      "updated_at": "2026-05-27T12:50:10.123456"
    }
  ],
  "message": null
}
```

### Response saat masih diproses
```json
{
  "id": 12,
  "user_id": 1,
  "category": "pakaian",
  "product_name": "Baju Rajut Wanita",
  "description": "Baju rajut wanita dengan gaya casual-premium, cocok untuk pasar Jepang dan Eropa.",
  "image_url": null,
  "status": "processing",
  "created_at": "2026-05-27T12:49:43.994311",
  "updated_at": "2026-05-27T12:50:00.000000",
  "report": null,
  "design_references": [],
  "message": "Analisis sedang diproses, silakan cek kembali nanti"
}
```

---

## 3) Create Design Reference

### Endpoint
`POST /api/analys_products/{analys_product_id}/design-references`

### Request
```json
{
  "title": "Soft Minimal Knit",
  "description": "Gaya rajut lembut dengan warna cream, cocok untuk tampilan minimalis modern.",
  "image_url": "https://example.com/images/soft-minimal-knit.jpg",
  "tags": ["cream", "minimal", "soft texture"],
  "sort_order": 0
}
```

### Response 200
```json
{
  "id": 1,
  "analys_product_id": 12,
  "title": "Soft Minimal Knit",
  "description": "Gaya rajut lembut dengan warna cream, cocok untuk tampilan minimalis modern.",
  "image_url": "https://example.com/images/soft-minimal-knit.jpg",
  "tags": ["cream", "minimal", "soft texture"],
  "sort_order": 0,
  "created_at": "2026-05-27T12:50:10.123456",
  "updated_at": "2026-05-27T12:50:10.123456"
}
```

---

## 4) Chat Send

### Endpoint
`POST /api/chat/sessions/{session_id}/send`

### Request
```json
{
  "message": "Bisa bantu kasih saran style yang lebih premium untuk baju rajut ini?",
  "analys_product_id": 12,
  "design_reference_id": 1
}
```

### Response 200
```json
{
  "reply": "Kamu bisa arahkan ke warna cream atau beige dengan tekstur rajut yang lebih rapi untuk memberi kesan premium.",
  "image_url": "https://example.com/generated/baju-rajut-01.png"
}
```

### Response jika tidak ada gambar
```json
{
  "reply": "Untuk pasar Jepang, fokuskan pada warna netral, siluet clean, dan material yang terlihat lembut.",
  "image_url": null
}
```

---

## 5) Chat Sessions - Create

### Endpoint
`POST /api/chat/sessions`

### Request
```json
{
  "title": "Diskusi Baju Rajut",
  "product_id": null
}
```

### Response 200
```json
{
  "id": 99,
  "title": "Diskusi Baju Rajut"
}
```

---

## 6) Chat Sessions - List

### Endpoint
`GET /api/chat/sessions`

### Response 200
```json
[
  {
    "id": 99,
    "user_id": 1,
    "product_id": null,
    "title": "Diskusi Baju Rajut",
    "created_at": "2026-05-27T12:50:10.123456",
    "updated_at": "2026-05-27T12:50:10.123456"
  }
]
```

---

## 7) Chat Messages - List

### Endpoint
`GET /api/chat/sessions/{session_id}/messages`

### Response 200
```json
[
  {
    "id": 1,
    "session_id": 99,
    "role": "user",
    "content": "Bisa bantu kasih saran style yang lebih premium?",
    "token_count": null,
    "created_at": "2026-05-27T12:50:15.000000"
  },
  {
    "id": 2,
    "session_id": 99,
    "role": "assistant",
    "content": "Fokus ke warna netral dan tekstur halus untuk kesan premium.",
    "token_count": null,
    "created_at": "2026-05-27T12:50:16.000000"
  }
]
```

---

## 8) Notes for Mockoon

- Gunakan response JSON di atas sebagai contoh response per endpoint.
- Kalau pakai Mockoon, kamu bisa set response statis per route.
- Untuk `GET /api/analys_products/{id}`, siapkan dua variasi response:
  - `processing`
  - `done`
- Untuk chat, cukup simpan response sederhana dulu, nanti bisa diganti sesuai prompt Gemini.
