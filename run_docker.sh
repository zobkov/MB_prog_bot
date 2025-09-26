# Запустить Postgres
docker run -d \
  --name mb_prog_bot \
  -e POSTGRES_USER=mb_prog_bot_user \
  -e POSTGRES_PASSWORD=mb_prog_bot_pass \
  -e POSTGRES_DB=mb_prog_bot_db \
  -p 5434:5432 \
  postgres:latest

# Запустить Redis
docker run -d \
  --name mb_prog_bot_redis \
  -p 6381:6379 \
  redis:latest