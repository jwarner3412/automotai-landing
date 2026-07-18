# automotAI — Privacy Policy

**Last updated:** July 14, 2026

## 1. Introduction

AutomotAI LLC ("Company," "we," "us," or "our") operates the automotAI platform, including the web application at app.automotai.com, the AI phone receptionist, customer portal, and all related services (collectively, the "Service").

This Privacy Policy explains what information we collect, how we use it, who we share it with, and what rights you have regarding your data. We take your privacy seriously and are committed to protecting the personal information entrusted to us.

By using the Service, you agree to the collection and use of information in accordance with this policy.

## 2. Information We Collect

### 2.1 Information You Provide

**Account Information:**
- Shop owner name, email address, and password (hashed)
- Shop name, address, phone number, and business details
- Team member names and email addresses

**Customer Data (entered by you or your customers):**
- Customer names, phone numbers, email addresses, and mailing addresses
- Vehicle information (make, model, year, VIN, license plate)
- Service history, estimates, and invoices
- Digital Vehicle Inspection (DVI) photos and findings

**Payment Information:**
- Payment card details are processed directly by Stripe. We do not store full credit card numbers on our servers. We may retain the last four digits, card brand, and expiration date for reference.

### 2.2 Information Collected Automatically

**Call Recordings & Transcripts:**
When the AI phone receptionist handles calls, we record and transcribe the conversation. These recordings and transcripts are stored in your Supabase database instance.

**Usage Data:**
- Pages visited, features used, and actions taken within the Service
- Browser type, device type, operating system
- IP address, approximate location (derived from IP)
- Referring URL and exit pages
- Timestamps of activity

**Cookies & Similar Technologies:**
We use cookies and similar technologies for:
- **Authentication** — keeping you logged in (session cookies)
- **Security** — preventing fraud and abuse
- **Preferences** — remembering your settings
- **Analytics** — understanding how the Service is used

You can control cookies through your browser settings. Disabling cookies may affect Service functionality.

### 2.3 Information from Third Parties

- **Stripe** — payment status and transaction metadata
- **Twilio** — call metadata (caller ID, duration, status)
- **Google** — if you sign in with Google OAuth, we receive your name and email address

## 3. How We Use Your Information

We use the information we collect to:

- **Provide the Service** — operate, maintain, and improve the automotAI platform
- **Process AI Interactions** — power the AI phone receptionist, generate estimates, and respond to customer inquiries
- **Authentication & Security** — verify your identity, protect against unauthorized access, detect and prevent fraud
- **Communication** — send service-related emails (password resets, billing notifications, feature updates), respond to support requests
- **Billing** — process subscription payments and manage your account
- **Analytics & Improvement** — understand usage patterns, identify bugs, and improve the Service
- **Legal Compliance** — comply with applicable laws, regulations, and legal processes

### 3.1 AI Model Processing

When you use AI features (phone receptionist, estimate generation, etc.), relevant data is sent to OpenRouter for AI model inference. OpenRouter routes requests to third-party AI model providers. We have configured these services to not retain or train on your data. See Section 5 for details.

## 4. How We Share Your Information

We do not sell your personal information or your customers' personal information. Period.

We share information only in the following circumstances:

### 4.1 Service Providers
We engage third-party services to operate the platform. These providers only access data necessary to perform their functions and are contractually bound to protect your information:

| Provider | Purpose | Data Accessed |
|----------|---------|---------------|
| **Supabase** | Database hosting, authentication | All Service data |
| **Twilio** | Phone call handling, SMS | Call recordings, transcripts, phone numbers |
| **Cloudflare** | Content delivery, DDoS protection | Web traffic, IP addresses |
| **Resend** | Email delivery | Email addresses, email content |
| **OpenRouter** | AI model inference | Call transcripts, estimate data, customer context |
| **Stripe** | Payment processing | Payment details, billing information |

### 4.2 Legal Requirements
We may disclose information if required to do so by law or in response to valid legal requests (subpoenas, court orders, warrants). We will notify you of such requests when legally permitted.

### 4.3 Business Transfers
If AutomotAI LLC is involved in a merger, acquisition, or sale of assets, your information may be transferred as part of that transaction. We will notify you before your information is transferred and becomes subject to a different privacy policy.

### 4.4 With Your Consent
We may share information for other purposes with your explicit consent.

## 5. Data Storage & Security

### 5.1 Where Data is Stored
Your Shop Data is stored in a Supabase database instance hosted in the United States. Call recordings and transcripts are stored by Twilio and in your Supabase instance. Backups are stored in Supabase's backup infrastructure.

### 5.2 Security Measures
We implement commercially reasonable security measures to protect your information:
- Encryption in transit (TLS/HTTPS) for all data transmission
- Encryption at rest for stored data (Supabase, Twilio)
- Password hashing using bcrypt (via Supabase Auth)
- Regular security reviews and dependency updates
- Access controls limiting employee access to production data

### 5.3 No Guarantee
No method of electronic storage or transmission is 100% secure. While we strive to protect your data, we cannot guarantee absolute security.

### 5.4 Data Retention
- **Account Data** — retained while your account is active
- **Customer Data** — retained while your account is active
- **Call Recordings & Transcripts** — retained while your account is active
- **Usage Data** — retained for up to 24 months
- **Backups** — retained for up to 90 days per our backup rotation

Upon account termination, your data is deleted within 30 days (see our Terms of Service, Section 6.5).

## 6. Your Rights & Choices

### 6.1 Access & Portability
You may request a copy of your Shop Data in a standard format (CSV or JSON). We will provide this within 14 business days. Contact us at hello@automotai.com.

### 6.2 Correction
You can update your account information through your account settings. For corrections to other data, contact us.

### 6.3 Deletion
You may request deletion of your account and all associated data at any time. We will complete the deletion within 30 days, subject to backup retention (up to 90 days).

### 6.4 Call Recording
You control whether the AI phone agent records calls. You can configure recording settings in your shop settings. You are responsible for complying with call recording consent laws in your jurisdiction.

### 6.5 Marketing Communications
We do not currently send marketing emails. If we begin doing so, you will have the option to opt out. Service-related communications (billing, security alerts, feature announcements) are not optional while your account is active.

### 6.6 Cookies
You can manage cookie preferences through your browser settings. Essential cookies (authentication, security) cannot be disabled without affecting Service functionality.

## 7. Your Customers' Privacy

As an auto repair shop using automotAI, you collect personal information from your customers. You are the data controller for your customers' information; we are the data processor.

### 7.1 Your Responsibilities
- Obtain appropriate consent from your customers for data collection and use
- Comply with applicable privacy laws in your jurisdiction
- Notify your customers about how their data is used (including AI processing and call recording)
- Honor your customers' data rights requests (access, correction, deletion)

### 7.2 Our Commitments
- We process your customers' data only to provide the Service to you
- We do not sell or use your customers' data for our own purposes
- We do not contact your customers directly except as part of the Service (e.g., sending estimates, invoices, or appointment reminders on your behalf)
- We will assist you in responding to customer data requests where possible

### 7.3 Customer Portal
When your customers access the customer portal to view estimates, approve repairs, or pay invoices, they interact directly with the Service. The portal collects minimal data necessary for its function (session cookies, authentication tokens). Portal sessions expire automatically.

## 8. Children's Privacy

The Service is not intended for individuals under the age of 18. We do not knowingly collect personal information from children. If we learn that we have collected personal information from a child, we will delete it promptly.

## 9. International Users

The Service is hosted in the United States. If you access the Service from outside the United States, your information may be transferred to, stored, and processed in the United States. By using the Service, you consent to this transfer.

## 10. California Privacy Rights

If you are a California resident, you may have additional rights under the California Consumer Privacy Act (CCPA):

- **Right to Know** — request disclosure of categories and specific pieces of personal information collected
- **Right to Delete** — request deletion of personal information
- **Right to Opt-Out** — we do not sell personal information, so this right is not applicable
- **Right to Non-Discrimination** — we will not discriminate against you for exercising your CCPA rights

To exercise these rights, contact us at hello@automotai.com. We will verify your identity before processing your request.

## 11. Changes to This Policy

We may update this Privacy Policy from time to time. We will notify you of material changes via email or through the Service at least 14 days before they take effect. Your continued use of the Service after the effective date constitutes acceptance of the updated policy.

## 12. Contact Us

If you have questions, concerns, or requests regarding this Privacy Policy or your data, contact us:

**AutomotAI LLC**
Email: hello@automotai.com
For privacy-specific inquiries: James@automotai.com

---

**Effective Date:** July 14, 2026
