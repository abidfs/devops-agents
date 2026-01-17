# Production-Ready Remediation Plan: PostgreSQL Authentication Failure (`FATAL: password authentication failed for user "app_user"`)

---

## 1. Executive Summary

The production application is failing to start due to repeated PostgreSQL authentication failures for user `app_user`. The root cause is a mismatch or invalidation of the credentials used by the application to connect to the database. This plan provides step-by-step remediation, verification, and prevention strategies to resolve and avoid recurrence of this issue.

---

## 2. Step-by-Step Remediation Plan

### **Step 1: Identify and Validate Current Credentials**

#### **A. Locate Credential Source**

- **Check if credentials are stored in:**
  - Environment variables
  - Secret manager (e.g., AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
  - Configuration file (e.g., `/app/config/production.yaml`)

#### **B. Extract Current Application Credential**

- **Example (YAML):**
    ```yaml
    database:
      username: app_user
      password: <CURRENT_PASSWORD>
      host: <db_host>
      name: <db_name>
    ```
- **Example (Environment Variable):**
    ```bash
    echo $DB_PASSWORD
    ```

#### **C. Retrieve Actual Database Password**

- **Connect to PostgreSQL as an admin:**
    ```bash
    psql -h <db_host> -U <admin_user> -d <db_name>
    ```
- **Check user details:**
    ```sql
    \du app_user
    ```
- **(Optional) Reset password if unknown:**
    ```sql
    ALTER USER app_user WITH PASSWORD '<NEW_SECURE_PASSWORD>';
    ```

> **Reference:**  
> [PostgreSQL: ALTER USER](https://www.postgresql.org/docs/current/sql-alteruser.html)

---

### **Step 2: Update Application Configuration with Correct Credentials**

#### **A. Update Secret Manager or Config File**

- **If using a secret manager (recommended):**
    - Update the secret value for `app_user`'s password.
    - Example (AWS CLI):
        ```bash
        aws secretsmanager update-secret --secret-id <secret_name> --secret-string '{"username":"app_user","password":"<NEW_SECURE_PASSWORD>"}'
        ```
- **If using environment variables:**
    - Update the deployment manifest or environment variable store.
    - Example (Kubernetes Secret YAML):
        ```yaml
        apiVersion: v1
        kind: Secret
        metadata:
          name: db-credentials
        type: Opaque
        data:
          username: YXBwX3VzZXI=   # base64 for 'app_user'
          password: <base64_of_NEW_SECURE_PASSWORD>
        ```
- **If using a config file:**
    - Edit `/app/config/production.yaml` and update the password field.

#### **B. Ensure Only One Source of Truth**

- Remove outdated credentials from all other locations to avoid config drift.

---

### **Step 3: Redeploy Application**

- **Trigger a redeploy to ensure the application picks up the new credentials.**
    - **Docker Compose:**
        ```bash
        docker-compose down && docker-compose up -d
        ```
    - **Kubernetes:**
        ```bash
        kubectl rollout restart deployment <app_deployment>
        ```
    - **Other orchestrators:** Use the appropriate redeploy/restart command.

---

### **Step 4: Validate Database User Status**

- **Check that `app_user` is not locked, expired, or disabled:**
    ```sql
    SELECT usename, valuntil, passwd FROM pg_shadow WHERE usename = 'app_user';
    ```
    - Ensure `valuntil` is NULL or a future date.
    - Ensure `passwd` is not NULL.

- **Check for role attributes:**
    ```sql
    \du app_user
    ```
    - Confirm `app_user` has `LOGIN` privilege.

---

### **Step 5: Test Direct Database Connection**

- **From the application host or a bastion:**
    ```bash
    PGPASSWORD='<NEW_SECURE_PASSWORD>' psql -h <db_host> -U app_user -d <db_name>
    ```
    - **Success:** You should see the `psql` prompt.
    - **Failure:** Double-check password, user status, and host-based authentication (`pg_hba.conf`).

---

### **Step 6: Audit PostgreSQL Logs**

- **Check for failed login attempts or security anomalies:**
    ```bash
    # Example: tail the PostgreSQL log
    tail -f /var/log/postgresql/postgresql-*.log
    ```
    - Look for repeated `FATAL: password authentication failed for user "app_user"` entries.

---

## 3. Verification

### **A. Application Health**

- **Check application logs for successful DB connection:**
    ```bash
    kubectl logs <app_pod>
    # or
    docker logs <app_container>
    ```
    - Look for messages indicating successful DB pool initialization.

- **Check health endpoint:**
    ```bash
    curl -f http://<app_host>:<health_port>/health
    # Should return 200 OK
    ```

- **Check load balancer status:**  
    - Instance should be marked healthy.

### **B. Database Authentication**

- **Monitor PostgreSQL logs:**  
    - Ensure no further authentication failures for `app_user`.

---

## 4. Prevention & Best Practices

### **A. Centralize and Automate Secret Management**

- Use a secret manager (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault).
- Ensure applications retrieve secrets at startup and support dynamic reload if possible.

### **B. Implement Automated Secret Rotation**

- Use secret manager rotation features.
- Automate application redeploys or rolling restarts upon secret rotation.

### **C. Monitoring and Alerting**

- Set up alerts for:
    - Repeated authentication failures in PostgreSQL logs.
    - Application health check failures.
    - Secret rotation events.

- **Example (Prometheus Alertmanager Rule):**
    ```yaml
    - alert: PostgresAuthFailures
      expr: increase(postgresql_log_auth_failures_total[5m]) > 5
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High rate of PostgreSQL authentication failures"
    ```

### **D. Configuration Hygiene**

- Ensure only one authoritative source for credentials.
- Remove hardcoded secrets from code and config files.
- Use environment variables or secret injection at runtime.

### **E. Documentation and Change Management**

- Document credential rotation procedures.
- Track all changes to database users and application secrets.

---

## 5. References

- [Microsoft Learn: Troubleshoot password authentication failed for user](https://learn.microsoft.com/en-us/azure/postgresql/troubleshoot/troubleshoot-password-authentication-failed-for-user)
- [PostgreSQL: ALTER USER](https://www.postgresql.org/docs/current/sql-alteruser.html)
- [PostgreSQL: Managing Roles and Privileges](https://www.postgresql.org/docs/current/user-manag.html)
- [AWS Secrets Manager: Rotating Secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [Kubernetes: Managing Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)

---

## 6. Summary Table

| Step                        | Action/Command/Config Example                                                                 | Reference/Notes                                      |
|-----------------------------|----------------------------------------------------------------------------------------------|------------------------------------------------------|
| Identify credentials        | Check `/app/config/production.yaml`, env vars, or secret manager                            |                                                      |
| Validate DB password        | `ALTER USER app_user WITH PASSWORD '<NEW_SECURE_PASSWORD>';`                                | [PostgreSQL ALTER USER](https://www.postgresql.org/docs/current/sql-alteruser.html) |
| Update secret/config        | Update secret manager, env var, or config file                                               |                                                      |
| Redeploy application        | `kubectl rollout restart deployment <app_deployment>` or equivalent                         |                                                      |
| Test direct connection      | `psql -h <db_host> -U app_user -d <db_name>`                                                |                                                      |
| Audit logs                  | `tail -f /var/log/postgresql/postgresql-*.log`                                              |                                                      |
| Verify health               | `curl -f http://<app_host>:<health_port>/health`                                            |                                                      |
| Monitor & alert             | Prometheus, CloudWatch, or equivalent                                                       |                                                      |

---

## 7. Conclusion

By following this remediation plan, you will resolve the immediate authentication failure, restore application availability, and implement best practices to prevent similar incidents in the future. Ensure all credential changes are tracked, secrets are managed centrally, and monitoring is in place for early detection of authentication issues.

---

**If you require further assistance or a tailored automation script for your environment, please specify your stack and secret management tooling.**