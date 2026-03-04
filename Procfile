web: cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
ui: streamlit run ui/app.py --server.port=$PORT --server.address=0.0.0.0
