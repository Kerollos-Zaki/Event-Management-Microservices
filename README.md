# Event Management Microservices 🎟️

A robust, scalable backend system built with a **Microservices Architecture** to manage users, events, and event registrations. The project is powered by **FastAPI** and **PostgreSQL**, fully containerized with **Docker**, and ready for orchestration using **Kubernetes**.

---

## 🌟 Key Features
* **Microservices Architecture:** Four decoupled services (User, Event, Registration, Notification) running independently.
* **Database Isolation:** Dedicated PostgreSQL databases for each service (UserDB, EventDB, RegistrationDB) to ensure data integrity and loose coupling.
* **Inter-Service Communication:** Synchronous HTTP communication via `httpx` (e.g., Registration service validating events and triggering notifications).
* **Container Orchestration:** Ready-to-use Docker Compose profiles for `dev`, `test`, and `prod` environments.
* **Kubernetes Ready:** Fully configured K8s manifests (`Deployments` and `NodePort Services`) for scalable cluster deployment.

---

## 🏗️ System Architecture

The system consists of the following microservices:
1. **User Service (Port 8001/30001):** Handles user registration and profile fetching.
2. **Event Service (Port 8002/30002):** Manages event creation, listing, and details tracking.
3. **Registration Service (Port 8003/30003):** Handles user registrations for events. Validates data with the Event Service and triggers the Notification Service upon success.
4. **Notification Service (Port 8004/30004):** Simulates sending notifications to users upon successful registration.

---

## 🛠️ Tech Stack
* **Backend Framework:** Python 3.11, FastAPI, Pydantic
* **Database & ORM:** PostgreSQL 15, SQLAlchemy, psycopg2
* **HTTP Client:** HTTPX (for service-to-service communication)
* **DevOps:** Docker, Docker Compose, Kubernetes (K8s)

