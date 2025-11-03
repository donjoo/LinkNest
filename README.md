# 🚀 URL Shortener — Hackathon Project

A **namespaced URL shortening platform** built with **Django (Backend)** and **React (Frontend)** within **24 hours** for a hackathon challenge.

---

## 🧩 Problem Statement

Build a **URL Shortener** with organizational privileges, secure access control, and namespace-based URL management.

Each user has their own organization(s), where they can manage namespaces and assign roles such as **Admin**, **Editor**, and **Viewer**.

---

## ⚙️ Tech Stack

- **Frontend:** React.js  
- **Backend:** Django + Django REST Framework  
- **Database:** PostgreSQL  
- **Storage:** Amazon S3 (for file uploads)  
- **Authentication:** JWT-based (role-based access control)  

---

## 🔑 Core Features

### 👤 User & Organization Management
- When a user signs up, a new **organization** is automatically created.  
- The user becomes the **Admin** of that organization.  
- An Admin can **invite** other users with different roles:
  - **Admin:** Create namespaces, invite users, manage URLs.
  - **Editor:** Create/edit/delete shortened URLs.
  - **Viewer:** View shortened URLs.

### 🏢 Namespace Management
- Each **organization** can have multiple **namespaces**.
- **Global uniqueness** — no two organizations share the same namespace.
- **Custom namespace creation** available to Admins.

### 🔗 URL Shortening
- Users can **create short URLs** under a specific namespace.
- **Custom shortcodes** supported (or generated randomly).
- Shortcode uniqueness is **enforced per namespace**.
- Example:
domain.com/myspace/cv → https://drive.google.com/abc123/mycv


### 📁 Bulk Shortening
- Upload an Excel file with a list of URLs.
- The system returns an Excel file with corresponding shortened URLs.
- Uses **Amazon S3** for secure file storage.

### ⚙️ URL Management
- Create, update, and delete short URLs within an organization’s namespace.


- 🕒 **Expiring URLs:** Shortened links automatically expire after a defined duration.  
- 📬 **Email Invites:** Admins can send organization invitations via email.
- 
---

## ⏳ Optional / Not Implemented (Due to Time Constraint)
The following features were **planned but not completed** within the 24-hour build window:

- 📊 **Analytics Dashboard** (click count, creator, timestamps)
- 🧾 **Tags or Categories** for URLs
- 🧩 **QR Code Generation**
- ⚙️ **Rate Limiting / Usage Stats**
- 🔒 **Private URLs** (access via JWT token only)

---

## 🧠 URL Routing Example

domain.com/<namespace>/<shortcode>/ → Redirects to actual URL


**Example:**
domain.com/my/cv → https://drive.google.com/file/d/abc123/view


---

## 🕐 Hackathon Details

- 🏁 **Duration:** 24 hours  
- 🧑‍💻 **Built With:** Django + React  
- 🎯 **Goal:** Implement maximum core functionality under strict time constraint  

---

## 💬 Future Improvements

- Add analytics and QR generation  
- Integrate Google sign-in  
- Add category/tag filters and usage statistics  

---

## 👨‍💻 Author

**Don Jo Rois**  
Python Django + React Developer  
*(Hackathon Build - 24 hours)*

---
