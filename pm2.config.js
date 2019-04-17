module.exports = {
  apps : [{
    name: "api",
    script: "gunicorn -c gunicorn_conf.py wsgi:app",
  }]
}
