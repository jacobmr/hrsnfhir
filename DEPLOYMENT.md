# Azure Deployment Guide - HRSN FHIR Processing Server

This guide will walk you through deploying the HRSN FHIR Processing Server to Microsoft Azure using the B1 (Basic) App Service tier.

## Prerequisites

1. **Azure CLI** - [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Azure Subscription** - Active Azure subscription with permissions to create resources
3. **GitHub Account** - For automated deployments (optional)

## 🚀 Quick Deployment (Automated)

### Option 1: One-Click Setup Script

```bash
# Clone and navigate to the repository
cd hrsn

# Run the automated setup script
./azure-setup.sh
```

This script will:
- Create all necessary Azure resources
- Set up PostgreSQL database
- Configure App Service with B1 tier
- Generate secure passwords and keys
- Provide deployment credentials for GitHub Actions

### Option 2: Manual Step-by-Step

If you prefer manual control, follow the detailed steps below.

## 📋 Manual Deployment Steps

### Step 1: Create Azure Resources

```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="rg-hrsn-fhir"
LOCATION="East US"
APP_NAME="hrsn-fhir-production"  # Must be globally unique
DB_SERVER="hrsn-postgres-server"  # Must be globally unique

# Create resource group
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Create App Service Plan (B1 tier)
az appservice plan create \
    --name "asp-hrsn-fhir" \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION" \
    --sku B1 \
    --is-linux

# Create Web App
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan "asp-hrsn-fhir" \
    --runtime "PYTHON|3.11" \
    --startup-file "startup.py"
```

### Step 2: Create Database

```bash
# Create PostgreSQL server
az postgres server create \
    --name $DB_SERVER \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION" \
    --admin-user hrsn_admin \
    --admin-password "YourSecurePassword123!" \
    --sku-name B_Gen5_1 \
    --version 13

# Create database
az postgres db create \
    --name hrsn_production \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_SERVER

# Configure firewall
az postgres server firewall-rule create \
    --name AllowAzureServices \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_SERVER \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0
```

### Step 3: Configure Application Settings

```bash
# Set environment variables
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        DATABASE_URL="postgresql://hrsn_admin@$DB_SERVER:YourSecurePassword123!@$DB_SERVER.postgres.database.azure.com:5432/hrsn_production?sslmode=require" \
        DEBUG="false" \
        LOG_LEVEL="INFO" \
        SECRET_KEY="your-generated-secret-key" \
        DEFAULT_API_KEY="your-generated-api-key" \
        PYTHONPATH="." \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE="false" \
        WEBSITES_PORT="8000"
```

### Step 4: Deploy Code

#### Option A: GitHub Actions (Recommended)

1. **Get Publish Profile:**
```bash
az webapp deployment list-publishing-profiles \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --xml
```

2. **Add to GitHub Secrets:**
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add secret: `AZUREAPPSERVICE_PUBLISHPROFILE` with the XML content

3. **Update Workflow:**
   - Edit `.github/workflows/azure-deploy.yml`
   - Change `AZURE_WEBAPP_NAME` to your app name

4. **Deploy:**
   - Push to main branch to trigger deployment

#### Option B: Direct Deployment

```bash
# Deploy from local directory
az webapp up \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan "asp-hrsn-fhir" \
    --sku B1 \
    --os-type Linux \
    --runtime "PYTHON:3.11" \
    --src-path .
```

## 🔧 Configuration

### Environment Variables

The following environment variables are automatically configured:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@server.postgres.database.azure.com:5432/db?sslmode=require` |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `SECRET_KEY` | Application secret key | `auto-generated` |
| `DEFAULT_API_KEY` | Default API key | `auto-generated` |

### Database Migration

After deployment, run database migrations:

```bash
# Access the Azure Shell or use local Azure CLI
az webapp ssh --name $APP_NAME --resource-group $RESOURCE_GROUP

# Inside the container
python -m alembic upgrade head
```

## 🔍 Monitoring & Troubleshooting

### View Logs

```bash
# Stream application logs
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP

# Download logs
az webapp log download --name $APP_NAME --resource-group $RESOURCE_GROUP
```

### Health Check

```bash
# Test health endpoint
curl https://$APP_NAME.azurewebsites.net/health
```

### Common Issues

1. **Startup Issues:**
   - Check logs for Python import errors
   - Verify `startup.py` is configured as startup file
   - Ensure `requirements-production.txt` has all dependencies

2. **Database Connection:**
   - Verify connection string format
   - Ensure SSL is enabled (`sslmode=require`)
   - Check firewall rules allow Azure services

3. **Static Files:**
   - Static files are served directly by the app
   - CSS/JS files should be in `app/static/`

## 📊 Cost Estimation (B1 Tier)

**Monthly Costs (approximate):**
- App Service B1: ~$13.14/month
- PostgreSQL Basic: ~$25/month
- **Total: ~$38/month**

## 🔒 Security

### Production Checklist:

- ✅ SSL/TLS enabled (automatic with Azure App Service)
- ✅ Environment variables secured
- ✅ Database SSL required
- ✅ API key authentication
- ✅ CORS configured
- ✅ Security headers enabled

### Generated Credentials:

The setup script generates secure:
- Database passwords
- Application secret keys
- API keys

**Store these securely** and rotate regularly.

## 🔄 Updates & Maintenance

### Updating the Application:

1. **Via GitHub Actions:**
   - Push changes to main branch
   - Deployment triggers automatically

2. **Manual Update:**
   ```bash
   az webapp up --name $APP_NAME --resource-group $RESOURCE_GROUP
   ```

### Database Backups:

```bash
# Enable automated backups
az postgres server configuration set \
    --name $DB_SERVER \
    --resource-group $RESOURCE_GROUP \
    --value on \
    --configuration-name backup_retention_days
```

## 🆘 Support

- **Azure Documentation:** [App Service Python](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python)
- **PostgreSQL on Azure:** [Azure Database for PostgreSQL](https://docs.microsoft.com/en-us/azure/postgresql/)
- **Application Logs:** Available in Azure Portal → App Service → Monitoring → Log stream

## 🎉 Success!

Your HRSN FHIR Processing Server should now be running at:
`https://YOUR-APP-NAME.azurewebsites.net`

Access the Members interface at:
`https://YOUR-APP-NAME.azurewebsites.net/members`