<p align="center">
  <img src="./assets/header.svg" width="100%" alt="Build. Ship. Operate. — Backend engineering, cloud infrastructure and reliable delivery." />
</p>

<div align="center">

# Phan Trinh Tien Dat

**Backend & DevOps Engineer** · Da Nang, Vietnam

Building resilient services. Automating the path from code to cloud.

<p>
  <a href="mailto:tiendat.xpbp@gmail.com"><img src="https://img.shields.io/badge/Email-0F172A?style=for-the-badge&logo=gmail&logoColor=67E8F9" alt="Email Dat" /></a>
  <a href="#technical-stack"><img src="https://img.shields.io/badge/Explore_the_stack-0F172A?style=for-the-badge&logo=stackshare&logoColor=67E8F9" alt="Explore the technical stack" /></a>
  <a href="#certification-goals"><img src="https://img.shields.io/badge/Certification_goals-0F172A?style=for-the-badge&logo=bookstack&logoColor=67E8F9" alt="View certification goals" /></a>
</p>

[About](#about) &nbsp; / &nbsp; [Stack](#technical-stack) &nbsp; / &nbsp; [DevOps roadmap](#devops-learning-roadmap) &nbsp; / &nbsp; [Certifications](#certification-goals)

</div>

---

## About

I'm Dat, a backend and DevOps engineer interested in the full journey of a service: **how it is designed, delivered, and operated**.

My focus is on **Java and Spring microservices**, **event-driven systems**, and **cloud infrastructure automation**. I enjoy connecting application architecture with the infrastructure that keeps it running.

- **Backend engineering** — Spring Boot, Spring Cloud, domain-driven design, Kafka, RabbitMQ, and Redis.
- **Cloud & delivery** — AWS, Docker, Kubernetes/EKS, Terraform, Ansible, and CI/CD pipelines.
- **Engineering growth** — distributed systems, GitOps, platform security, and service reliability.

## Technical Stack

<p>
  <img src="https://img.shields.io/badge/Java-0F172A?style=for-the-badge&logo=openjdk&logoColor=FBBF24" alt="Java" />
  <img src="https://img.shields.io/badge/Spring_Boot-0F172A?style=for-the-badge&logo=springboot&logoColor=86EFAC" alt="Spring Boot" />
  <img src="https://img.shields.io/badge/AWS-0F172A?style=for-the-badge&logo=amazonwebservices&logoColor=FBBF24" alt="AWS" />
  <img src="https://img.shields.io/badge/Docker-0F172A?style=for-the-badge&logo=docker&logoColor=67E8F9" alt="Docker" />
  <img src="https://img.shields.io/badge/Kubernetes-0F172A?style=for-the-badge&logo=kubernetes&logoColor=93C5FD" alt="Kubernetes" />
  <img src="https://img.shields.io/badge/Terraform-0F172A?style=for-the-badge&logo=terraform&logoColor=C4B5FD" alt="Terraform" />
</p>

### Cloud, infrastructure & delivery

| Area | Technologies |
| :--- | :--- |
| **Cloud & containers** | AWS · Amazon EKS · Docker · Kubernetes · Helm |
| **Infrastructure as Code** | Terraform · Ansible |
| **CI/CD & source control** | GitHub Actions · GitLab CI/CD · Jenkins · Git |
| **Systems & automation** | Linux · Bash / Shell · Python · YAML |
| **Observability** | Prometheus · Grafana · OpenTelemetry · Elasticsearch · Logstash · Kibana · Zipkin |

### Backend & data

| Area | Technologies |
| :--- | :--- |
| **Languages** | Java · SQL · Python · TypeScript |
| **Services & persistence** | Spring Boot · Spring Cloud · Hibernate / JPA |
| **Identity & APIs** | Keycloak · Swagger / OpenAPI · Postman |
| **Databases & caching** | PostgreSQL · MySQL · Redis · Elasticsearch |
| **Messaging & streaming** | Apache Kafka · RabbitMQ |
| **Web tooling** | Next.js |

## DevOps Learning Roadmap

The next tools and practices I want to develop through focused labs and projects.

<p>
  <img src="https://img.shields.io/badge/GitOps-Argo_CD-0F172A?style=flat-square&logo=argo&logoColor=67E8F9&labelColor=164E63" alt="GitOps learning goal: Argo CD" />
  <img src="https://img.shields.io/badge/Security-Trivy-0F172A?style=flat-square&logo=trivy&logoColor=67E8F9&labelColor=164E63" alt="Security learning goal: Trivy" />
  <img src="https://img.shields.io/badge/Secrets-Vault-0F172A?style=flat-square&logo=vault&logoColor=67E8F9&labelColor=164E63" alt="Secrets learning goal: Vault" />
  <img src="https://img.shields.io/badge/Logs-Loki-0F172A?style=flat-square&logo=grafana&logoColor=67E8F9&labelColor=164E63" alt="Logging learning goal: Loki" />
</p>

| Track | Tools & concepts to explore | Practice goal |
| :--- | :--- | :--- |
| **GitOps & releases** | Argo CD · Kustomize · Helm · Amazon ECR | Version deployment configuration, detect drift, and practice rollback. |
| **AWS foundations** | IAM · VPC · EC2 · S3 · RDS · Route 53 · CloudWatch | Build a networked application environment with scoped access and useful telemetry. |
| **Kubernetes operations** | RBAC · NetworkPolicy · HPA · probes · resource limits · storage · Gateway API | Deploy, scale, and troubleshoot workloads; practice cluster backup and recovery. |
| **Networking & Linux** | TCP/IP · DNS · HTTP/TLS · NGINX · systemd | Trace connectivity problems from process to endpoint. |
| **DevSecOps** | Trivy · SonarQube · Gitleaks · SBOMs | Add image, code, and secret checks to a delivery pipeline. |
| **Secrets & identity** | HashiCorp Vault · External Secrets Operator · cert-manager · OIDC | Explore secret delivery, certificate automation, and short-lived CI credentials. |
| **Observability & SRE** | Grafana Loki · Tempo · Alertmanager · SLIs/SLOs · error budgets | Correlate logs, metrics, and traces; write actionable alerts and incident runbooks. |
| **Infrastructure quality** | Terraform modules · remote state · state locking · environment isolation | Make infrastructure changes reviewable, repeatable, and easier to recover. |

<details>
<summary><strong>Learning blueprint · from commit to observable service</strong></summary>

This is a target lab architecture for practicing the roadmap above.

```mermaid
flowchart TD
    A[Source commit] --> B[CI: test and security checks]
    B --> C[Build and scan container image]
    C --> D[Publish image to Amazon ECR]
    D --> E[Review image digest update in GitOps repo]
    E --> F[Argo CD reconciles Helm manifests]
    F --> G[Application on Amazon EKS]
    T[Terraform: AWS infrastructure] --> G
    G --> H[OpenTelemetry instrumentation]
    H --> I[Metrics, logs and traces]
    I --> J[Grafana dashboards and alerts]
    J --> K[Investigate and improve]

    classDef core fill:#0f172a,stroke:#38bdf8,color:#f1f5f9;
    classDef support fill:#132c35,stroke:#5eead4,color:#f1f5f9;
    class A,B,C,D,E,F,G core;
    class T,H,I,J,K support;
```

**Backend architecture interests:** domain-driven design, event-driven communication, SAGA workflows, circuit breakers, bulkheads, caching, and distributed tracing.

</details>

## Certification Goals

**All certifications below are future goals; none have been earned yet.**

<p>
  <img src="https://img.shields.io/badge/CKA-GOAL-0F172A?style=for-the-badge&logo=kubernetes&logoColor=white&labelColor=1D4ED8" alt="CKA — goal, not yet earned" />
  <img src="https://img.shields.io/badge/AWS_SAA-GOAL-0F172A?style=for-the-badge&labelColor=92400E" alt="AWS Solutions Architect Associate — goal, not yet earned" />
  <img src="https://img.shields.io/badge/Terraform-GOAL-0F172A?style=for-the-badge&logo=terraform&logoColor=white&labelColor=6D28D9" alt="Terraform Associate — goal, not yet earned" />
</p>

### Foundation & core goals

| Certification | Learning focus | Status |
| :--- | :--- | :--- |
| [**AWS Certified Solutions Architect – Associate**](https://aws.amazon.com/certification/certified-solutions-architect-associate/) | Resilient, secure, and cost-aware AWS architectures | Planned |
| [**Certified Kubernetes Administrator (CKA)**](https://www.cncf.io/training/certification/cka/) | Cluster administration, networking, storage, and troubleshooting | Planned |
| [**HashiCorp Certified: Terraform Associate**](https://docs.hashicorp.com/certifications/terraform-associate) | IaC fundamentals, configuration, state, and core workflows | Planned |

### Further specialization

| Certification | Learning focus | Status |
| :--- | :--- | :--- |
| [**Certified Kubernetes Application Developer (CKAD)**](https://www.cncf.io/training/certification/ckad/) | Application configuration and workloads on Kubernetes | Future goal |
| [**Certified Kubernetes Security Specialist (CKS)**](https://www.cncf.io/training/certification/cks/) | Cluster hardening, supply chain, and runtime security | After passing CKA |
| [**AWS Certified DevOps Engineer – Professional**](https://aws.amazon.com/certification/certified-devops-engineer-professional/) | Delivery automation, monitoring, resilience, and operations on AWS | Long-term goal |

<sub>Certification names link to official programs. CKS requires passing CKA before attempting the exam.</sub>

---

<div align="center">

**Let's talk backend systems, cloud infrastructure, and developer workflows.**

[Email](mailto:tiendat.xpbp@gmail.com) &nbsp; · &nbsp; [Facebook](https://www.facebook.com/tien.at.563335) &nbsp; · &nbsp; [Instagram](https://www.instagram.com/johnleynguci/)

<sub>Phan Trinh Tien Dat · Da Nang, Vietnam</sub>

</div>
