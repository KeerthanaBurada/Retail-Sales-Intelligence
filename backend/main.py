from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import auth, datasets, analytics, forecast, reports

app = FastAPI(
    title='Retail Sales Intelligence Platform',
    description='Analytics and ML-powered retail sales intelligence',
    version='1.0.0'
)

# Allow frontend dev servers

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://retail-sales-intelligence.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all route handlers
app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(analytics.router)
app.include_router(forecast.router)
app.include_router(reports.router)


@app.on_event('startup')
def startup():
    """Create database tables on first run."""
    Base.metadata.create_all(bind=engine)
    print('Database tables created successfully')


@app.get('/')
def root():
    return {
        'message': 'Retail Sales Intelligence Platform API',
        'version': '1.0.0',
        'docs': '/docs'
    }


@app.get('/health')
def health_check():
    return {'status': 'healthy'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
