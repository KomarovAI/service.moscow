# Service Moscow - K3s Optimized Static Website

🚀 **Production-ready static website deployment on K3s cluster with automatic SSL, zero-downtime updates, and Docker Hub CI/CD**

## Overview

This project deploys a static restaurant equipment repair website to K3s cluster with:
- ✅ **Automatic SSL** via Traefik ACME Let's Encrypt
- ✅ **Zero-downtime deployments** with rolling updates
- ✅ **CI/CD pipeline** GitHub Actions → Docker Hub → K3s
- ✅ **Production optimizations** gzip, caching, security headers
- ✅ **Network-aware scheduling** for hybrid cloud setup

## Architecture

```
GitHub Push → GitHub Actions → Docker Hub → K3s Cluster
                                              ↓
                                          Traefik Ingress
                                          (SSL + Headers)
                                              ↓
                                          Service (ClusterIP)
                                              ↓
                                          Deployment (2 replicas)
                                              ↓
                                          Nginx Alpine Pods
```

## Quick Start

### 1. Setup GitHub Secrets

Go to repository Settings → Secrets and variables → Actions:

```
DOCKERHUB_USERNAME    # Your Docker Hub username
DOCKERHUB_TOKEN       # Docker Hub access token  
KUBECONFIG_BASE64     # Base64 encoded kubeconfig
```

### 2. Configure Traefik SSL (one-time setup on K3s server)

```bash
# On K3s master node
sudo nano /var/lib/rancher/k3s/server/manifests/traefik-config.yaml
```

Add this content:
```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    additionalArguments:
      - "--certificatesresolvers.letsencrypt.acme.email=artur.komarovv@gmail.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/data/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      web:
        exposedPort: 80
      websecure:
        exposedPort: 443
```

### 3. Point Domain to K3s

```bash
# Get K3s external IP
kubectl get nodes -o wide

# Update DNS: artur789298.work.gd → K3s_IP
```

### 4. Deploy

```bash
# Push to main branch triggers automatic deployment
git push origin main
```

## Project Structure

```
├── src/                    # Static website files
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── images/
├── k8s/                    # Kubernetes manifests
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── middleware.yaml
│   └── pdb.yaml
├── .github/workflows/
│   └── deploy.yml          # CI/CD pipeline
├── Dockerfile              # Simple nginx:alpine container
└── README.md
```

## Secrets Setup

### Docker Hub Token

1. Go to Docker Hub → Account Settings → Security
2. Create "New Access Token" 
3. Copy token to GitHub secret `DOCKERHUB_TOKEN`

### Kubeconfig

```bash
# On K3s server, get kubeconfig in base64
cat /etc/rancher/k3s/k3s.yaml | base64 -w 0

# Or if you have local kubectl configured
kubectl config view --raw | base64 -w 0
```

Copy output to GitHub secret `KUBECONFIG_BASE64`

## Monitoring & Management

### Check Deployment Status

```bash
# Pod status
kubectl -n service-moscow get pods

# Ingress and SSL certificate
kubectl -n service-moscow get ingress
kubectl -n service-moscow describe ingress service-moscow

# Application logs
kubectl -n service-moscow logs -l app=service-moscow -f
```

### Manual Operations

```bash
# Manual rollout restart
kubectl -n service-moscow rollout restart deploy/service-moscow

# Scale replicas
kubectl -n service-moscow scale deploy/service-moscow --replicas=3

# Delete deployment
kubectl delete namespace service-moscow
```

## Network-Aware Scheduling

For hybrid clusters (VPS + home PCs via Tailscale), web pods are automatically scheduled on public nodes with best internet connectivity:

```yaml
# In deployment.yaml
nodeSelector:
  node-role.kubernetes.io/public: "true"
```

## Performance Features

- **Gzip compression** via Traefik middleware
- **Static file caching** browser cache headers
- **HTTP/2** enabled by default
- **Security headers** HSTS, CSP, XSS protection
- **CDN ready** cache-friendly headers

## Troubleshooting

### SSL Issues
```bash
# Check certificate status
kubectl -n service-moscow describe ingress service-moscow

# Traefik logs
kubectl -n kube-system logs -l app.kubernetes.io/name=traefik -f
```

### Deployment Issues
```bash
# Check rollout status
kubectl -n service-moscow rollout status deploy/service-moscow

# Pod events
kubectl -n service-moscow describe pods
```

### DNS Issues
```bash
# Test DNS resolution
dig artur789298.work.gd

# Test from inside cluster
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup service-moscow.service-moscow.svc.cluster.local
```

## Production Optimizations

### Zero-Downtime Updates
- 2+ replicas with rolling update strategy
- PodDisruptionBudget ensures availability
- Readiness probes prevent traffic to unhealthy pods

### Resource Limits
```yaml
resources:
  requests:
    cpu: "25m"
    memory: "32Mi"
  limits:
    cpu: "100m" 
    memory: "64Mi"
```

### Security
- Non-root container execution
- Security headers via Traefik middleware
- Network policies (optional)

## License

MIT License - see LICENSE file

## Contact

- **Author**: KomarovAI
- **Email**: artur.komarovv@gmail.com
- **Website**: https://artur789298.work.gd

---

**🚀 Production-ready K3s deployment with automatic SSL and zero-downtime updates!**