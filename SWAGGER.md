<img src="/static/images/logo.png" alt="Logo" class="img-fluid" style="height: 50px;" />

# 📡 SMARTX CONNECTOR
[**HOME**](/) | [**LOGS**](/logs) | [**API DOCS**](/docs)

**SMARTX CONNECTOR** is a modern **RFID reader management solution** offering **high performance**, **scalability**, and **real-time monitoring** with comprehensive system integration capabilities.

---

## ⚙️ How It Works

The SMARTX CONNECTOR acts as a **middleware solution** between physical RFID readers and your management systems, providing:

### 🔌 **Universal Connectivity**
- Support for multiple protocols: **TCP/IP**, **Serial**, **USB**
- Simultaneous connections with multiple devices
- Auto-reconnection and device health monitoring

### 📊 **Smart Processing**
- **Automatic filtering** of duplicate tags
- **Real-time validation** of EPC/TID data
- **Antenna control** and power configuration
- **RSSI monitoring** for proximity analysis

### 🔄 **Flexible Integration**
- **Database Support**: SQLite, MySQL, PostgreSQL
- **Webhook Integration** with retry mechanisms
- **MQTT Connectivity** for IoT platforms
- **RESTful API** with comprehensive endpoints
- **Real-time Monitoring** and structured logging

---

### 🧪 **Testing & Simulation**

**Perfect for:**
- ✅ **Integration testing** without physical hardware
- ✅ **Application development** and debugging
- ✅ **Data flow validation** across systems
- ✅ **Team training** and demonstration
- ✅ **Load testing** with multiple tag simulations

---

## 🔄 **Operating Flow**

1. **Configuration**: Define devices and system settings
2. **Connection**: Automatically connect to RFID readers
3. **Processing**: Tags are captured and processed in real-time
4. **Storage**: Data persisted to configured database
5. **Integration**: Send data to external systems
6. **Monitoring**: Real-time logs and system status

---

## 📊 **API Features**

### **Device Management**
- List and configure RFID devices
- Monitor device status and health
- Get device examples and templates

### **RFID Operations**
- Retrieve detected tags and statistics
- Clear tag memory and reset counters
- Access EPC and GTIN data

### **Integration**
- Receive data from external systems
- Process webhook and MQTT messages

### **Testing Tools**
- Simulate tag events for development
- Generate test data for validation

---

## 🖥️ **Web Interface**

### **Dashboard**
- Real-time device monitoring
- Tag statistics and activity
- System health indicators

### **Log Viewer**
- Live log streaming with auto-refresh
- Search and filter capabilities
- Color-coded log levels

### **API Documentation**
- Interactive testing interface
- Complete endpoint documentation
- Request and response examples

---

## 🛠️ **Technology**

**Backend**: FastAPI with SQLAlchemy  
**Frontend**: Modern web interface with real-time updates  
**Integration**: Webhook, MQTT, and database support  
**Deployment**: Standalone executable or server installation

---
