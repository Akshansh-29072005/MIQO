# 🤖 MIQO  
## Modular Intelligent Campus Assistant Robot  
**Backend Engineering • AI Systems • Edge Computing • Robotics**

![Platform](https://img.shields.io/badge/Platform-Jetson%20Nano-green?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-Computer%20Vision%20%7C%20RL-blue?style=for-the-badge)
![CUDA](https://img.shields.io/badge/CUDA-cuDNN%20Accelerated-red?style=for-the-badge)
![Language](https://img.shields.io/badge/Language-Python%20%7C%20Embedded%20C%2B%2B-orange?style=for-the-badge)
![Domain](https://img.shields.io/badge/Domain-Backend%20%2B%20AI%20Systems-purple?style=for-the-badge)

---

## 🚀 One-Line Pitch (For Recruiters)

**MIQO is a real-world AI system that combines computer vision, backend-style orchestration, and embedded control to deliver an autonomous indoor delivery robot running on edge hardware.**

---

## 👀 Why This Project Stands Out

Most student projects focus on:
- isolated ML models, or  
- basic CRUD backends, or  
- simulation-only robotics  

**MIQO integrates all three layers of a real product system:**

- 🧠 **AI inference at the edge**
- 🧩 **Backend-like orchestration & state management**
- ⚙️ **Low-level embedded control**

This project demonstrates how **AI models interact with real systems**, not just datasets.

---

## 🎯 Problem Statement

Educational campuses still rely on **manual human effort** for short-distance logistics:
- Carrying files and documents
- Transporting academic materials
- Repetitive department-to-department tasks

These tasks are:
- Time-consuming
- Costly over time
- Ideal candidates for automation

**MIQO automates these workflows using AI-driven perception and control.**

---

## 🧠 What I Built (High-Level Summary)

- Designed a **semi-autonomous indoor robot** for real environments
- Built a **vision-driven decision pipeline** on Jetson Nano
- Implemented **path learning & replay** as a stateful system
- Created **low-latency communication** between AI layer and motor controller
- Engineered a **modular architecture** suitable for future scaling

This mirrors how **backend + AI systems** are designed in production.

---

## 🛠️ Tech Stack & Skills Demonstrated

### **AI & Computer Vision**
- OpenCV 4.5.0 (compiled from source with CUDA & cuDNN)
- Real-time image preprocessing (ROI, blur, thresholding)
- Contour detection & centroid-based navigation
- Reinforcement-learning-ready architecture (DQN integration planned)

### **Backend-Style System Design**
- State-based decision logic
- Command deduplication (send only on state change)
- Timestamped event logging (CSV as lightweight datastore)
- Deterministic replay using temporal data
- Mode-driven execution (Learn / Replay / Autonomous)

### **Edge & Systems Engineering**
- NVIDIA Jetson Nano (GPU inference at the edge)
- CSI camera pipeline via GStreamer
- Serial (UART) communication design
- Hardware–software co-design
- Power-aware system architecture

### **Embedded Systems**
- ESP32 for real-time control
- PWM motor control
- MPU6050 IMU integration
- Ultrasonic sensor for collision prevention
- High-current BTS7960 motor drivers

---

## 🏗️ System Architecture (Conceptual)

**Jetson Nano (AI + Control Plane)**  
- Vision inference  
- Path learning & replay logic  
- Decision making  

⬇ UART (low latency)

**ESP32 (Execution Plane)**  
- Motor PWM control  
- Sensor handling  
- Safety logic  

⬇ PWM Generation 

**Motor Drivers → DC Motors**

This separation closely resembles **backend control plane vs execution plane** architecture.

---

## 🔁 Operating Modes

1. **Learn Mode**
   - Robot follows line
   - Commands logged with timestamps
   - Path persisted for reuse

2. **Replay Mode**
   - Replays stored commands
   - Preserves original timing & behavior

3. **Autonomous Follow**
   - Vision-only navigation
   - No data recording

---

## 👁️ Real-Time Vision Pipeline

1. CSI camera frame capture  
2. Region of Interest (ROI) extraction  
3. Grayscale conversion  
4. Gaussian blur  
5. Binary thresholding  
6. Contour detection  
7. Centroid computation  
8. Action selection (`F / L / R / S`)  

⚡ Commands are transmitted **only on state change**, reducing latency and jitter.

---

## 📊 Performance Metrics

| Metric | Result |
|------|--------|
| Line-following accuracy | ~100% |
| Path replay accuracy | ~90% |
| Load capacity | Up to 5 kg |
| Human effort reduction | ~95% |
| Motion stability | Smooth, indoor-safe |

---

## 💰 Cost & Impact

- Manual support staff ≈ ₹15,000/month
- MIQO = one-time hardware cost
- Scales without proportional cost increase

Demonstrates **cost-aware system design**, not just technical novelty.

---

## 🧠 What I Learned (Key Section)

### **Backend + AI Perspective**

- How to treat AI inference as a **service**, not a script
- Designing **stateful systems** instead of one-off computations
- Handling **real-time constraints** and unreliable inputs
- Separating **decision logic** from **execution logic**
- Why deterministic replay is critical for debugging AI systems

### **Systems & Engineering Insights**

- GPU acceleration matters only when the **pipeline is designed correctly**
- Latency reduction is often about **architecture**, not hardware
- Embedded systems force you to write **defensive, predictable code**
- Real environments expose edge cases no dataset ever shows

### **AI Reality Check**

- Vision models must be **robust, not perfect**
- Classical CV still matters alongside ML
- Reinforcement learning requires **clean state/action definitions**
- Data collection and system stability are as important as models

---

## 🔮 Future Enhancements (Production-Oriented)

- SLAM + LiDAR for full autonomy
- Deep Q-Reinforcement Learning integration
- Web dashboard (backend + frontend)
- Voice interaction
- Multi-robot coordination
- Cloud-assisted monitoring

---

## 🎓 Project Context

- **Type:** Minor Project  
- **Branch:** Computer Science & Engineering (AI)  
- **Team Size:** 3  
- **Target Role:** Backend + AI / Systems Engineer  

---

## 📌 For Recruiters

This project demonstrates:
- Backend-style system thinking
- AI deployed beyond notebooks
- Comfort with low-level systems
- End-to-end ownership mindset
- Ability to design, debug, and scale real systems

---

## 📜 License

Academic & educational use only.

---

⭐ If this project aligns with your work, feel free to star the repository or reach out.
