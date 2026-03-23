search_engine_project/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   │
│   ├── models/              # Database models
│   │   ├── user_model.py
│   │   ├── document_model.py
│   │
│   ├── routes/              # Flask routes (controllers)
│   │   ├── auth_routes.py
│   │   ├── search_routes.py
│   │   ├── upload_routes.py
│   │   ├── admin_routes.py
│   │
│   ├── services/            # Business logic
│   │   ├── search_service.py
│   │   ├── indexing_service.py
│   │   ├── spellcheck_service.py
│   │   ├── file_service.py
│   │
│   ├── utils/               # Helper functions
│   │   ├── tokenizer.py
│   │   ├── validators.py
│   │   ├── security.py
│   │
│   ├── templates/           # HTML files
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── upload.html
│   │   ├── results.html
│   │   ├── admin.html
│   │
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
|   | 
|   |-- __init__.py
│   
├── data/
│   ├── uploads/             # Stored documents
│   ├── index/               # Whoosh index
│
├── database/
│   ├── app.db               # SQLite DB
│
├── logs/
│   ├── app.log
│
├── tests/                   # Unit testing
│
├── requirements.txt
├── run.py
└── README.md


