# Technical Debt

## High Priority

### Backup / Restore
Status: OPEN

Need:
- PostgreSQL dump automation
- Restore validation
- Retention policy

Risk:
Data loss on SSD failure.

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