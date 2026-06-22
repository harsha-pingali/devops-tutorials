# Oracle Database Monitoring with Grafana Alloy

This guide provides step-by-step instructions for setting up Oracle Database monitoring using Grafana Alloy's `prometheus.exporter.oracledb` component.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Custom Metrics Setup](#custom-metrics-setup)
5. [Slow Query Monitoring](#slow-query-monitoring)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Grafana Alloy
- Oracle Instant Client Basic (required for Oracle DB connectivity)
- Access to Oracle Database with appropriate permissions

### Database User Permissions
The database user must have:
- `SELECT_CATALOG_ROLE` role, OR
- `SELECT` privilege on specific system views

For complete list of required permissions, refer to the [Oracle AI Database Metrics Exporter Installation guide](https://oracle.github.io/oracle-db-appdev-monitoring/docs/getting-started/basics).

---

## Installation

### Step 1: Install Oracle Instant Client Basic

Download and install Oracle Instant Client Basic for your operating system from:
[http://www.oracle.com/technetwork/database/features/instant-client/index-097480.html](http://www.oracle.com/technetwork/database/features/instant-client/index-097480.html)

**Installation paths by OS:**
- **Linux**: `/usr/lib/oracle/<version>/client64/lib`
- **macOS (Intel)**: `/usr/local/oracle/instantclient_<version>`
- **macOS (Apple Silicon)**: `/lib/oracle/instantclient_<version>`
- **Windows**: `C:\oracle\instantclient_<version>`

### Step 2: Set Environment Variables

Configure the following environment variables based on your operating system:

#### Linux
```bash
export LD_LIBRARY_PATH=/usr/lib/oracle/19.3/client64/lib:$LD_LIBRARY_PATH
export ORACLE_HOME=/usr/lib/oracle/19.3/client64
```

#### macOS (Apple Silicon)
```bash
export DYLD_LIBRARY_PATH=/lib/oracle/instantclient_23_3:$DYLD_LIBRARY_PATH
export ORACLE_HOME=/lib/oracle/instantclient_23_3
```

#### macOS (Intel)
```bash
export DYLD_LIBRARY_PATH=/usr/local/oracle/instantclient_19_8:$DYLD_LIBRARY_PATH
export ORACLE_HOME=/usr/local/oracle/instantclient_19_8
```

#### Optional Environment Variables
```bash
export ORACLE_BASE=/opt/oracle          # Base directory for Oracle installations
export TNS_ADMIN=/path/to/wallet        # Location of Oracle wallet (for wallet authentication)
```

### Step 3: Install Grafana Alloy

Follow the [Grafana Alloy installation guide](https://grafana.com/docs/alloy/latest/get-started/install/) for your platform.

### Step 4: Verify Installation

Test the Oracle Instant Client installation:
```bash
# Linux/macOS
ldconfig -p | grep oracle    # Linux
ls -la $DYLD_LIBRARY_PATH    # macOS

# Verify Alloy installation
alloy --version
```

---

## Configuration

### Basic Configuration

Create an Alloy configuration file (e.g., `config.alloy`):

```hcl
// Basic single database configuration
prometheus.exporter.oracledb "production_db" {
  database {
    name              = "production"
    connection_string = "db-server.example.com:1521/ORCL"
    username          = "monitoring_user"
    password          = "secure_password"
  }
}

// Scrape the metrics
prometheus.scrape "oracle_metrics" {
  targets    = prometheus.exporter.oracledb.production_db.targets
  forward_to = [prometheus.remote_write.metrics_storage.receiver]
}

// Send metrics to Grafana Cloud or Prometheus
prometheus.remote_write "metrics_storage" {
  endpoint {
    url = "https://prometheus-prod-01.grafana.net/api/prom/push"
    
    basic_auth {
      username = "your_username"
      password = "your_grafana_cloud_token"
    }
  }
}
```

### Multi-Database Configuration

For monitoring multiple databases:

```hcl
prometheus.exporter.oracledb "oracle_cluster" {
  // Primary database
  database {
    name              = "primary"
    connection_string = "db-primary.example.com:1521/ORCL"
    username          = "monitor_user"
    password          = "primary_password"
    
    labels = {
      environment = "production"
      role        = "primary"
      datacenter  = "us-east-1"
    }
  }
  
  // Standby database
  database {
    name              = "standby"
    connection_string = "db-standby.example.com:1521/ORCL"
    username          = "monitor_user"
    password          = "standby_password"
    
    labels = {
      environment = "production"
      role        = "standby"
      datacenter  = "us-west-1"
    }
  }
  
  // Development database
  database {
    name              = "dev"
    connection_string = "db-dev.example.com:1521/ORCLDEV"
    username          = "monitor_user"
    password          = "dev_password"
    
    labels = {
      environment = "development"
      role        = "standalone"
    }
  }
  
  // Connection pool settings
  max_open_conns = 10
  max_idle_conns = 5
  query_timeout  = 5
}

prometheus.scrape "oracle_cluster_metrics" {
  targets    = prometheus.exporter.oracledb.oracle_cluster.targets
  forward_to = [prometheus.remote_write.metrics_storage.receiver]
}

prometheus.remote_write "metrics_storage" {
  endpoint {
    url = "https://your-prometheus-endpoint.com/api/v1/write"
    
    basic_auth {
      username = "admin"
      password = "your_password"
    }
  }
}
```

### Advanced Configuration with Custom Metrics

```hcl
prometheus.exporter.oracledb "advanced_monitoring" {
  database {
    name              = "production"
    connection_string = "db-server.example.com:1521/ORCL"
    username          = "monitor_user"
    password          = "secure_password"
  }
  
  // Path to custom metrics definitions (TOML format)
  custom_metrics = [
    "/etc/alloy/metrics/slow_queries.toml",
    "/etc/alloy/metrics/custom_app_metrics.toml",
    "/etc/alloy/metrics/tablespace_monitoring.toml"
  ]
  
  // Path to default metrics file (overrides built-in defaults)
  default_metrics = "/etc/alloy/metrics/default_oracle_metrics.toml"
  
  // Connection pool configuration
  max_open_conns = 15
  max_idle_conns = 5
  query_timeout  = 10
}

prometheus.scrape "advanced_oracle_metrics" {
  targets    = prometheus.exporter.oracledb.advanced_monitoring.targets
  forward_to = [prometheus.remote_write.metrics_storage.receiver]
}

prometheus.remote_write "metrics_storage" {
  endpoint {
    url = "https://prometheus-endpoint.example.com/api/v1/write"
    
    basic_auth {
      username = "prometheus_user"
      password = "prometheus_password"
    }
  }
}
```

---

## Custom Metrics Setup

Custom metrics are defined in TOML format files. Here are examples for various monitoring scenarios:

### Slow Query Monitoring

Create `/etc/alloy/metrics/slow_queries.toml`:

```toml
[[metric]]
context = "slow_queries"
labels = [ "sql_id", "username", "program" ]
metricsdesc = { elapsed_time = "SQL execution elapsed time in seconds", executions = "Number of executions", sql_text = "SQL query text" }
request = """
SELECT 
  sql_id,
  username,
  program,
  elapsed_time / 1000000 as elapsed_time,
  executions,
  SUBSTR(sql_text, 1, 100) as sql_text
FROM 
  v$sqlarea
WHERE 
  elapsed_time > 10000000
  AND executions > 0
ORDER BY 
  elapsed_time DESC
FETCH FIRST 20 ROWS ONLY
"""

[[metric]]
context = "long_running_queries"
labels = [ "sid", "serial#", "username", "status" ]
metricsdesc = { seconds_in_wait = "Seconds in wait state", sql_exec_start = "SQL execution start time" }
request = """
SELECT 
  s.sid,
  s.serial#,
  s.username,
  s.status,
  s.seconds_in_wait,
  TO_CHAR(s.sql_exec_start, 'YYYY-MM-DD HH24:MI:SS') as sql_exec_start
FROM 
  v$session s
WHERE 
  s.status = 'ACTIVE'
  AND s.username IS NOT NULL
  AND s.seconds_in_wait > 60
"""
```

### Tablespace Monitoring

Create `/etc/alloy/metrics/tablespace_monitoring.toml`:

```toml
[[metric]]
context = "tablespace_usage"
labels = [ "tablespace_name" ]
metricsdesc = { 
  size_mb = "Total tablespace size in MB", 
  used_mb = "Used space in MB", 
  free_mb = "Free space in MB",
  percent_used = "Percentage of space used"
}
request = """
SELECT 
  tablespace_name,
  ROUND(tablespace_size * 8192 / 1024 / 1024, 2) as size_mb,
  ROUND(used_space * 8192 / 1024 / 1024, 2) as used_mb,
  ROUND((tablespace_size - used_space) * 8192 / 1024 / 1024, 2) as free_mb,
  ROUND(used_percent, 2) as percent_used
FROM 
  dba_tablespace_usage_metrics
"""

[[metric]]
context = "tablespace_autoextend"
labels = [ "tablespace_name", "file_name" ]
metricsdesc = { 
  autoextensible = "Is file autoextensible (1=yes, 0=no)",
  bytes = "Current file size in bytes",
  maxbytes = "Maximum file size in bytes"
}
request = """
SELECT 
  tablespace_name,
  file_name,
  CASE WHEN autoextensible = 'YES' THEN 1 ELSE 0 END as autoextensible,
  bytes,
  maxbytes
FROM 
  dba_data_files
"""
```

### Session and Connection Monitoring

Create `/etc/alloy/metrics/session_monitoring.toml`:

```toml
[[metric]]
context = "active_sessions"
labels = [ "status", "machine", "program" ]
metricsdesc = { session_count = "Number of sessions by status" }
request = """
SELECT 
  status,
  machine,
  program,
  COUNT(*) as session_count
FROM 
  v$session
GROUP BY 
  status, machine, program
"""

[[metric]]
context = "blocking_sessions"
labels = [ "blocking_session", "blocked_session", "username" ]
metricsdesc = { wait_time = "Time blocked session has been waiting" }
request = """
SELECT 
  blocking_session,
  sid as blocked_session,
  username,
  seconds_in_wait as wait_time
FROM 
  v$session
WHERE 
  blocking_session IS NOT NULL
"""

[[metric]]
context = "connection_pool_usage"
labels = [ "program" ]
metricsdesc = { connections = "Number of connections by program" }
request = """
SELECT 
  program,
  COUNT(*) as connections
FROM 
  v$session
WHERE 
  type = 'USER'
GROUP BY 
  program
"""
```

### Performance Metrics

Create `/etc/alloy/metrics/performance_metrics.toml`:

```toml
[[metric]]
context = "buffer_cache_hit_ratio"
labels = []
metricsdesc = { hit_ratio = "Buffer cache hit ratio percentage" }
request = """
SELECT 
  ROUND((1 - (phy.value / (db.value + consistent.value))) * 100, 2) as hit_ratio
FROM 
  v$sysstat phy,
  v$sysstat db,
  v$sysstat consistent
WHERE 
  phy.name = 'physical reads'
  AND db.name = 'db block gets'
  AND consistent.name = 'consistent gets'
"""

[[metric]]
context = "redo_log_stats"
labels = []
metricsdesc = { 
  redo_size = "Redo size in bytes",
  redo_writes = "Number of redo writes"
}
request = """
SELECT 
  SUM(CASE WHEN name = 'redo size' THEN value ELSE 0 END) as redo_size,
  SUM(CASE WHEN name = 'redo writes' THEN value ELSE 0 END) as redo_writes
FROM 
  v$sysstat
WHERE 
  name IN ('redo size', 'redo writes')
"""

[[metric]]
context = "top_wait_events"
labels = [ "event_name" ]
metricsdesc = { 
  total_waits = "Total number of waits",
  time_waited = "Total time waited in centiseconds"
}
request = """
SELECT 
  event as event_name,
  total_waits,
  time_waited
FROM 
  v$system_event
WHERE 
  event NOT IN ('SQL*Net message from client', 'rdbms ipc message')
ORDER BY 
  time_waited DESC
FETCH FIRST 10 ROWS ONLY
"""
```

### Application-Specific Metrics

Create `/etc/alloy/metrics/custom_app_metrics.toml`:

```toml
[[metric]]
context = "order_processing_stats"
labels = [ "status" ]
metricsdesc = { order_count = "Number of orders by status" }
request = """
SELECT 
  status,
  COUNT(*) as order_count
FROM 
  orders
WHERE 
  created_date >= SYSDATE - 1
GROUP BY 
  status
"""

[[metric]]
context = "inventory_levels"
labels = [ "warehouse", "product_category" ]
metricsdesc = { 
  items_in_stock = "Number of items in stock",
  low_stock_items = "Number of items with low stock"
}
request = """
SELECT 
  warehouse,
  product_category,
  COUNT(*) as items_in_stock,
  SUM(CASE WHEN quantity < reorder_level THEN 1 ELSE 0 END) as low_stock_items
FROM 
  inventory
GROUP BY 
  warehouse, product_category
"""

[[metric]]
context = "user_activity"
labels = [ "action_type" ]
metricsdesc = { 
  action_count = "Number of user actions in last hour"
}
request = """
SELECT 
  action_type,
  COUNT(*) as action_count
FROM 
  user_activity_log
WHERE 
  action_timestamp >= SYSDATE - INTERVAL '1' HOUR
GROUP BY 
  action_type
"""
```

---

## Running Alloy

### Start Alloy with Configuration

```bash
# Linux/macOS
alloy run config.alloy

# With specific log level
alloy run --log.level=debug config.alloy

# Running in background
nohup alloy run config.alloy > alloy.log 2>&1 &

# With custom storage path
alloy run --storage.path=/var/lib/alloy config.alloy
```

### Docker Deployment

```dockerfile
FROM grafana/alloy:latest

# Install Oracle Instant Client
USER root
RUN apt-get update && \
    apt-get install -y wget unzip libaio1 && \
    wget https://download.oracle.com/otn_software/linux/instantclient/1923000/instantclient-basic-linux.x64-19.23.0.0.0dbru.zip && \
    unzip instantclient-basic-linux.x64-19.23.0.0.0dbru.zip -d /opt/oracle && \
    rm instantclient-basic-linux.x64-19.23.0.0.0dbru.zip && \
    sh -c "echo /opt/oracle/instantclient_19_23 > /etc/ld.so.conf.d/oracle-instantclient.conf" && \
    ldconfig

ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_19_23:$LD_LIBRARY_PATH
ENV ORACLE_HOME=/opt/oracle/instantclient_19_23

# Copy configuration
COPY config.alloy /etc/alloy/config.alloy
COPY metrics/ /etc/alloy/metrics/

USER alloy

CMD ["run", "/etc/alloy/config.alloy"]
```

### Kubernetes Deployment

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alloy-config
  namespace: monitoring
data:
  config.alloy: |
    prometheus.exporter.oracledb "production" {
      database {
        name              = "production"
        connection_string = "oracle-db.database.svc.cluster.local:1521/ORCL"
        username          = "monitor_user"
        password          = env("ORACLE_PASSWORD")
      }
      
      custom_metrics = [
        "/etc/alloy/metrics/slow_queries.toml",
        "/etc/alloy/metrics/tablespace_monitoring.toml"
      ]
      
      max_open_conns = 10
      max_idle_conns = 5
      query_timeout  = 10
    }
    
    prometheus.scrape "oracle_metrics" {
      targets    = prometheus.exporter.oracledb.production.targets
      forward_to = [prometheus.remote_write.grafana_cloud.receiver]
    }
    
    prometheus.remote_write "grafana_cloud" {
      endpoint {
        url = env("GRAFANA_CLOUD_URL")
        
        basic_auth {
          username = env("GRAFANA_CLOUD_USER")
          password = env("GRAFANA_CLOUD_TOKEN")
        }
      }
    }

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: oracle-custom-metrics
  namespace: monitoring
data:
  slow_queries.toml: |
    [[metric]]
    context = "slow_queries"
    labels = [ "sql_id", "username" ]
    metricsdesc = { elapsed_time = "SQL elapsed time" }
    request = "SELECT sql_id, username, elapsed_time/1000000 as elapsed_time FROM v$sqlarea WHERE elapsed_time > 10000000 ORDER BY elapsed_time DESC FETCH FIRST 20 ROWS ONLY"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: alloy-oracle-exporter
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: alloy-oracle-exporter
  template:
    metadata:
      labels:
        app: alloy-oracle-exporter
    spec:
      initContainers:
      - name: install-oracle-client
        image: oraclelinux:8
        command:
        - /bin/bash
        - -c
        - |
          yum install -y oracle-instantclient-basic
          cp -r /usr/lib/oracle/21/client64/lib/* /oracle-libs/
        volumeMounts:
        - name: oracle-libs
          mountPath: /oracle-libs
      
      containers:
      - name: alloy
        image: grafana/alloy:latest
        args:
        - run
        - /etc/alloy/config.alloy
        - --storage.path=/var/lib/alloy
        - --server.http.listen-addr=0.0.0.0:12345
        env:
        - name: LD_LIBRARY_PATH
          value: "/oracle-libs"
        - name: ORACLE_HOME
          value: "/oracle-libs"
        - name: ORACLE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: oracle-credentials
              key: password
        - name: GRAFANA_CLOUD_URL
          valueFrom:
            secretKeyRef:
              name: grafana-cloud-credentials
              key: url
        - name: GRAFANA_CLOUD_USER
          valueFrom:
            secretKeyRef:
              name: grafana-cloud-credentials
              key: username
        - name: GRAFANA_CLOUD_TOKEN
          valueFrom:
            secretKeyRef:
              name: grafana-cloud-credentials
              key: token
        volumeMounts:
        - name: alloy-config
          mountPath: /etc/alloy/config.alloy
          subPath: config.alloy
        - name: oracle-custom-metrics
          mountPath: /etc/alloy/metrics
        - name: oracle-libs
          mountPath: /oracle-libs
        ports:
        - containerPort: 12345
          name: http-metrics
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      
      volumes:
      - name: alloy-config
        configMap:
          name: alloy-config
      - name: oracle-custom-metrics
        configMap:
          name: oracle-custom-metrics
      - name: oracle-libs
        emptyDir: {}

---
apiVersion: v1
kind: Secret
metadata:
  name: oracle-credentials
  namespace: monitoring
type: Opaque
stringData:
  password: "your_oracle_password"

---
apiVersion: v1
kind: Secret
metadata:
  name: grafana-cloud-credentials
  namespace: monitoring
type: Opaque
stringData:
  url: "https://prometheus-prod-01.grafana.net/api/prom/push"
  username: "your_grafana_cloud_user"
  token: "your_grafana_cloud_token"
```

---

## Troubleshooting

### Common Issues

#### 1. Oracle Client Library Not Found

**Error:**
```
error="failed to initialize exporter: libocci.so: cannot open shared object file"
```

**Solution:**
```bash
# Verify library path
echo $LD_LIBRARY_PATH    # Linux
echo $DYLD_LIBRARY_PATH  # macOS

# Add to your shell profile
echo 'export LD_LIBRARY_PATH=/path/to/instantclient:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify libraries are found
ldd $(which alloy)  # Linux
otool -L $(which alloy)  # macOS
```

#### 2. Connection Refused

**Error:**
```
error="failed to connect to database: ORA-12541: TNS:no listener"
```

**Solution:**
- Verify database host and port
- Check firewall rules
- Test connection with sqlplus:
  ```bash
  sqlplus username/password@host:port/service_name
  ```

#### 3. Insufficient Privileges

**Error:**
```
error="ORA-00942: table or view does not exist"
```

**Solution:**
```sql
-- Grant required permissions
GRANT SELECT_CATALOG_ROLE TO monitoring_user;

-- Or grant specific permissions
GRANT SELECT ON v$session TO monitoring_user;
GRANT SELECT ON v$sqlarea TO monitoring_user;
GRANT SELECT ON v$sysstat TO monitoring_user;
GRANT SELECT ON dba_tablespace_usage_metrics TO monitoring_user;
```

#### 4. High Connection Count

**Issue:** Too many connections to database

**Solution:**
Adjust connection pool settings in config:
```hcl
prometheus.exporter.oracledb "example" {
  max_open_conns = 5   # Reduce from default 10
  max_idle_conns = 2   # Reduce from default
  query_timeout  = 5   # Timeout queries faster
  
  database {
    // ... database config
  }
}
```

#### 5. Custom Metrics Not Loading

**Check:**
```bash
# Verify TOML syntax
cat /etc/alloy/metrics/slow_queries.toml

# Check file permissions
ls -la /etc/alloy/metrics/

# Run Alloy with debug logging
alloy run --log.level=debug config.alloy
```

---

## Monitoring Best Practices

### 1. Use Connection Pooling Wisely
```hcl
// For production databases with high query volume
max_open_conns = 15
max_idle_conns = 5

// For development/low-traffic databases
max_open_conns = 5
max_idle_conns = 2
```

### 2. Set Appropriate Query Timeouts
```hcl
query_timeout = 10  // 10 seconds for complex queries
```

### 3. Use Labels for Multi-Database Environments
```hcl
database {
  name = "prod-primary"
  connection_string = "..."
  
  labels = {
    environment = "production"
    region      = "us-east-1"
    role        = "primary"
    tier        = "critical"
  }
}
```

### 4. Monitor the Exporter Itself
- Check Alloy logs regularly
- Monitor memory usage
- Set up alerts for exporter downtime

### 5. Secure Credentials
- Use environment variables or secrets management
- Never commit passwords to version control
- Rotate credentials regularly

---

## Useful Grafana Dashboard Queries

### Slow Query Alerts
```promql
# Queries taking longer than 30 seconds
oracledb_slow_queries_elapsed_time > 30

# Number of slow queries per database
count by (database) (oracledb_slow_queries_elapsed_time > 10)
```

### Tablespace Usage
```promql
# Tablespace usage percentage
oracledb_tablespace_usage_percent_used

# Alert when tablespace is over 85% full
oracledb_tablespace_usage_percent_used > 85
```

### Active Sessions
```promql
# Total active sessions
sum(oracledb_active_sessions_session_count{status="ACTIVE"})

# Sessions by program
sum by (program) (oracledb_active_sessions_session_count)
```

### Connection Pool Health
```promql
# Connection pool usage
sum by (program) (oracledb_connection_pool_usage_connections)

# Rate of new connections
rate(oracledb_connection_pool_usage_connections[5m])
```

---

## Additional Resources

- [Grafana Alloy Documentation](https://grafana.com/docs/alloy/latest/)
- [Oracle DB Exporter GitHub](https://github.com/oracle/oracle-db-appdev-monitoring)
- [Oracle Instant Client Downloads](http://www.oracle.com/technetwork/database/features/instant-client/index-097480.html)
- [Prometheus TOML Metrics Format](https://github.com/oracle/oracle-db-appdev-monitoring#custom-metrics)

---

## License and Support

This configuration is based on the official Grafana Alloy documentation and Oracle DB Exporter project. For issues and support:

- Grafana Alloy: [GitHub Issues](https://github.com/grafana/alloy/issues)
- Oracle DB Exporter: [GitHub Issues](https://github.com/oracle/oracle-db-appdev-monitoring/issues)
- Community Support: [Grafana Community](https://grafana.com/community/)
