#!/bin/bash
# Azure deployment setup script for HRSN FHIR Processing Server

# Configuration - Update these values for your deployment
RESOURCE_GROUP="rg-hrsn-fhir"
APP_SERVICE_PLAN="asp-hrsn-fhir"
WEBAPP_NAME="hrsn-fhir-production"
DB_SERVER_NAME="hrsn-postgres-server"
DB_NAME="hrsn_production"
LOCATION="East US"
SKU="B1"  # Basic B1 tier as requested

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Azure deployment setup for HRSN FHIR Processing Server${NC}"
echo "=================================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure
echo -e "${YELLOW}🔐 Logging into Azure...${NC}"
az login

# Create resource group
echo -e "${YELLOW}📦 Creating resource group: $RESOURCE_GROUP${NC}"
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Create App Service Plan (B1 tier)
echo -e "${YELLOW}⚙️ Creating App Service Plan: $APP_SERVICE_PLAN${NC}"
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION" \
    --sku $SKU \
    --is-linux

# Create Web App
echo -e "${YELLOW}🌐 Creating Web App: $WEBAPP_NAME${NC}"
az webapp create \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --runtime "PYTHON|3.11" \
    --startup-file "startup.py"

# Create PostgreSQL server
echo -e "${YELLOW}🗄️ Creating PostgreSQL server: $DB_SERVER_NAME${NC}"
echo "Please enter a strong admin password for the database:"
read -s DB_ADMIN_PASSWORD

az postgres server create \
    --name $DB_SERVER_NAME \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION" \
    --admin-user hrsn_admin \
    --admin-password $DB_ADMIN_PASSWORD \
    --sku-name B_Gen5_1 \
    --version 13

# Create database
echo -e "${YELLOW}📊 Creating database: $DB_NAME${NC}"
az postgres db create \
    --name $DB_NAME \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_SERVER_NAME

# Configure firewall rules for PostgreSQL
echo -e "${YELLOW}🔥 Configuring firewall rules...${NC}"
az postgres server firewall-rule create \
    --name AllowAzureServices \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_SERVER_NAME \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# Get database connection string
DB_CONNECTION_STRING="postgresql://hrsn_admin@$DB_SERVER_NAME:$DB_ADMIN_PASSWORD@$DB_SERVER_NAME.postgres.database.azure.com:5432/$DB_NAME?sslmode=require"

# Configure app settings
echo -e "${YELLOW}⚙️ Configuring application settings...${NC}"
az webapp config appsettings set \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        DATABASE_URL="$DB_CONNECTION_STRING" \
        DEBUG="false" \
        LOG_LEVEL="INFO" \
        SECRET_KEY="$(openssl rand -base64 32)" \
        DEFAULT_API_KEY="$(openssl rand -base64 24)" \
        PYTHONPATH="." \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE="false" \
        WEBSITES_PORT="8000"

# Enable logging
echo -e "${YELLOW}📝 Enabling application logging...${NC}"
az webapp log config \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --application-logging true \
    --level information \
    --web-server-logging filesystem

# Get deployment credentials
echo -e "${YELLOW}🔑 Getting deployment credentials...${NC}"
PUBLISH_PROFILE=$(az webapp deployment list-publishing-profiles \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --xml)

echo -e "${GREEN}✅ Azure resources created successfully!${NC}"
echo "=================================================="
echo -e "${YELLOW}📋 Deployment Information:${NC}"
echo "Resource Group: $RESOURCE_GROUP"
echo "App Service: $WEBAPP_NAME"
echo "Database Server: $DB_SERVER_NAME"
echo "Database: $DB_NAME"
echo "App URL: https://$WEBAPP_NAME.azurewebsites.net"
echo ""
echo -e "${YELLOW}🔧 Next Steps:${NC}"
echo "1. Add the publish profile to GitHub Secrets as 'AZUREAPPSERVICE_PUBLISHPROFILE'"
echo "2. Update the workflow file with your app name: $WEBAPP_NAME"
echo "3. Push your code to trigger the deployment"
echo "4. Access your app at: https://$WEBAPP_NAME.azurewebsites.net"
echo ""
echo -e "${YELLOW}💾 Publish Profile (save this for GitHub Secrets):${NC}"
echo "$PUBLISH_PROFILE"
echo ""
echo -e "${GREEN}🎉 Setup complete! Your HRSN FHIR server is ready for deployment.${NC}"