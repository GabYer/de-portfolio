# Technical Debt

## High Priority
### Backup / Restore
Status: ✅ DONE

Need:
- PostgreSQL dump automation
- Restore validation
- Retention policy

Risk:
Data loss on SSD failure.

Решение:
- pg_dump Airflow PostgreSQL → .sql.gz
- tar архив /data/stacks/ конфигов
- rclone sync → Google Drive (de-homelab-backups/)
- Cron: каждый день в 02:00
- Retention: 7 дней локально, всё в облаке

---

## Medium Priority

### Monitoring
Status: OPEN

Need:
- Grafana dashboards
- Airflow health monitoring
- Kafka broker monitoring

---

### Security Model
Status: OPEN

Need:
- remove broad chmod permissions
- Docker secrets
- service accounts

---

## Low Priority

### Automated Testing
Deferred due to single-developer workflow.

Planned after team expansion.