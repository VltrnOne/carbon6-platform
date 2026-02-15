# Carbon6 OiS Security Quick Reference

**Fast access to critical security commands**

---

## 🔐 Credential Management

```bash
# View current user clearance
whoami

# Change admin password
npx ts-node scripts/change-password.ts --email admin@carbon6.io

# Rotate JWT secret
NEW_JWT=$(openssl rand -base64 48)
sed -i '' "s|JWT_SECRET=.*|JWT_SECRET=\"$NEW_JWT\"|" .env
pm2 restart carbon6-api

# Generate new Ed25519 keypair
ssh-keygen -t ed25519 -C "carbon6@connector" -f ~/.ssh/carbon6_connector
```

---

## 🎖️ Clearance Management

```bash
# Assign clearance to creator
creator create --email user@example.com --clearance L3-CONFIDENTIAL

# Advance creator tier (auto-adjusts clearance)
creator advance <creator-id> --to-tier CARBON[6]  # → L3-CONFIDENTIAL
creator advance <creator-id> --to-tier [6]        # → L4-RESTRICTED

# View clearance hierarchy
agent invoke AEGIS --prompt "Show clearance hierarchy"
```

---

## 🔍 Audit & Monitoring

```bash
# View SDK installation audit logs
sdk audit <installation-id> --last 24h

# Check failed authentication attempts
psql $DATABASE_URL -c "
  SELECT COUNT(*), ip_address, user_agent
  FROM connector_audit_logs
  WHERE signature_valid = false
    AND created_at > NOW() - INTERVAL '1 hour'
  GROUP BY ip_address, user_agent
  ORDER BY COUNT(*) DESC
"

# View installation log
tail -f installation.log

# System status
pm2 status
pm2 logs carbon6-api --lines 50
```

---

## 🛡️ SDK Installation Security

```bash
# Register new SDK installation
curl -X POST http://localhost:3006/api/connector/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Partner Integration",
    "platform": "nodejs",
    "public_key": "'"$(cat ~/.ssh/carbon6_connector.pub)"'"
  }'

# List all installations
sdk list --status active

# Suspend installation (emergency)
sdk suspend <installation-id> --reason "Security review"

# Re-enable installation
sdk enable <installation-id>

# Revoke all tokens for installation
curl -X DELETE http://localhost:3006/api/connector/revoke \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## 🚨 Emergency Response

```bash
# FULL LOCKDOWN - Suspend all installations
for id in $(psql carbon6 -t -c "SELECT id FROM connector_installations WHERE enabled = 1"); do
  sdk suspend $id --reason "Security incident"
done

# Revoke all active tokens
psql carbon6 -c "
  UPDATE connector_tokens
  SET revoked_at = NOW(),
      revocation_reason = 'Security incident'
  WHERE revoked_at IS NULL
"

# Lock all admin accounts except primary
psql carbon6 -c "
  UPDATE users
  SET status = 'SUSPENDED'
  WHERE role = 'ADMIN' AND id != 1
"

# Invoke AEGIS for incident response
agent invoke AEGIS --prompt "Security incident: [describe]"

# Emergency Oracle validation
oracle emergency --severity critical
```

---

## 🔑 Database Security

```bash
# Create read-only analytics user
psql carbon6 << EOF
CREATE USER analytics_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE carbon6 TO analytics_readonly;
GRANT USAGE ON SCHEMA public TO analytics_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_readonly;
EOF

# Backup database (encrypted)
./scripts/backup-database.sh

# Check database connections
psql carbon6 -c "SELECT * FROM pg_stat_activity WHERE datname = 'carbon6'"
```

---

## 🔐 Encryption Operations

```bash
# Encrypt sensitive file
openssl enc -aes-256-gcm -salt -in secret.txt -out secret.txt.enc \
  -pass env:ENCRYPTION_KEY

# Decrypt file
openssl enc -d -aes-256-gcm -in secret.txt.enc -out secret.txt \
  -pass env:ENCRYPTION_KEY

# Verify TLS version
curl -v https://localhost:3006/api/health 2>&1 | grep "TLS"
```

---

## 📊 Security Health Checks

```bash
# Verify all security gates
curl http://localhost:3006/api/health/security \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Check rate limits
sdk limits <installation-id>

# Oracle signature verification
oracle verify <decision-id>

# Run security audit
agent invoke AEGIS --prompt "Run full security audit"
```

---

## 📋 Pre-Launch Verification

```bash
# Run VERIFICUS adversarial audit
agent invoke VERIFICUS --prompt "Pre-launch security verification"

# Check critical security gates
agent invoke AEGIS-PENETRATOR --prompt "Penetration test for production readiness"

# Verify encryption at rest
psql carbon6 -c "
  SELECT table_name, column_name, data_type
  FROM information_schema.columns
  WHERE column_name LIKE '%encrypted%' OR column_name LIKE '%hash%'
"
```

---

## 🎯 Common Security Tasks

### Change Creator Clearance
```bash
psql carbon6 -c "
  UPDATE creators
  SET clearance = 'L4-RESTRICTED'
  WHERE id = <creator-id>
"
```

### Force Password Reset
```bash
psql carbon6 -c "
  UPDATE users
  SET password_reset_required = true
  WHERE id = <user-id>
"
```

### Enable 2FA for User
```bash
npx ts-node scripts/enable-2fa.ts --user-id <user-id>
```

### IP Whitelist for SDK
```bash
psql carbon6 -c "
  UPDATE connector_installations
  SET metadata = jsonb_set(
    COALESCE(metadata, '{}'::jsonb),
    '{allowed_ips}',
    '[\"192.168.1.0/24\"]'::jsonb
  )
  WHERE id = 'inst_xyz123'
"
```

---

## 🔔 Security Alerts Setup

```bash
# Monitor failed authentications (every 15 min)
cat > ~/monitor-security.sh << 'EOF'
#!/bin/bash
FAILED=$(psql $DATABASE_URL -t -c "
  SELECT COUNT(*) FROM connector_audit_logs
  WHERE signature_valid = false
  AND created_at > NOW() - INTERVAL '1 hour'
")
[ "$FAILED" -gt 10 ] && echo "ALERT: $FAILED failed auth attempts"
EOF

chmod +x ~/monitor-security.sh
(crontab -l; echo "*/15 * * * * ~/monitor-security.sh") | crontab -
```

---

## 📞 Security Contacts

**Via Web Terminal:**
```bash
# Security incident
@AEGIS Security incident: [describe]

# Compliance issue
@TRUST_DIRECTOR Compliance concern: [describe]

# Forensic analysis
@LOGOS Audit trail request: [timeframe]

# Emergency consensus
oracle emergency --issue "[describe]" --severity critical
```

---

**Keep this reference handy for quick security operations!**

```
Document ID: L5-SEC-QR-2026-001
Classification: L5-BLACK
```
