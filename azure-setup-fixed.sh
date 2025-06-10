#!/bin/bash
# Fixed Azure deployment setup script for HRSN FHIR Processing Server

# Configuration
RESOURCE_GROUP="rg-hrsn-fhir-jmr"
APP_SERVICE_PLAN="asp-hrsn-fhir-jmr"
WEBAPP_NAME="hrsn-fhir-jmr-2024"
DB_SERVER_NAME="hrsn-postgres-jmr-2024"
DB_NAME="hrsn_production"
LOCATION="East US"
SKU="B1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Azure deployment setup for HRSN FHIR Processing Server${NC}"
echo "=================================================="

# Create App Service Plan
echo -e "${YELLOW}⚙️ Creating App Service Plan: $APP_SERVICE_PLAN${NC}"
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION" \
    --sku $SKU \
    --is-linux

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ App Service Plan created successfully${NC}"
else
    echo -e "${RED}❌ Failed to create App Service Plan${NC}"
    exit 1
fi

# Create Web App
echo -e "${YELLOW}🌐 Creating Web App: $WEBAPP_NAME${NC}"
az webapp create \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --runtime "PYTHON|3.11" \
    --startup-file "startup.py"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Web App created successfully${NC}"
else
    echo -e "${RED}❌ Failed to create Web App${NC}"
    exit 1
fi

# Prompt for database password
echo -e "${YELLOW}🔐 Please enter a strong admin password for the database:${NC}"
read -s DB_ADMIN_PASSWORD
echo

# Create PostgreSQL Flexible Server (newer version)
echo -e "${YELLOW}🗄️ Creating PostgreSQL Flexible Server: $DB_SERVER_NAME${NC}"
az postgres flexible-server create \
    --name $DB_SERVER_NAME \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION" \
    --admin-user hrsn_admin \
    --admin-password "$DB_ADMIN_PASSWORD" \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --version 13 \
    --storage-size 32

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PostgreSQL server created successfully${NC}"
else
    echo -e "${RED}❌ Failed to create PostgreSQL server${NC}"
    exit 1
fi

# Create database
echo -e "${YELLOW}📊 Creating database: $DB_NAME${NC}"
az postgres flexible-server db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_SERVER_NAME \
    --database-name $DB_NAME

# Configure firewall rules for PostgreSQL
echo -e "${YELLOW}🔥 Configuring firewall rules...${NC}"
az postgres flexible-server firewall-rule create \
    --name AllowAzureServices \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_SERVER_NAME \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# Get database connection string
DB_CONNECTION_STRING="postgresql://hrsn_admin:$DB_ADMIN_PASSWORD@$DB_SERVER_NAME.postgres.database.azure.com:5432/$DB_NAME?sslmode=require"

# Generate secure keys
SECRET_KEY=$(openssl rand -base64 32)
API_KEY=$(openssl rand -base64 24)

# Configure app settings
echo -e "${YELLOW}⚙️ Configuring application settings...${NC}"
az webapp config appsettings set \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        DATABASE_URL="$DB_CONNECTION_STRING" \
        DEBUG="false" \
        LOG_LEVEL="INFO" \
        SECRET_KEY="$SECRET_KEY" \
        DEFAULT_API_KEY="$API_KEY" \
        PYTHONPATH="." \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE="false" \
        WEBSITES_PORT="8000"

# Enable logging
echo -e "${YELLOW}📝 Enabling application logging...${NC}"
az webapp log config \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --application-logging filesystem \
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
echo -e "${YELLOW}🔑 Important Information (SAVE THIS):${NC}"
echo "Database Admin Password: $DB_ADMIN_PASSWORD"
echo "API Key: $API_KEY"
echo "Secret Key: $SECRET_KEY"
echo ""
echo -e "${YELLOW}💾 Publish Profile (save this for GitHub Secrets):${NC}"
echo "$PUBLISH_PROFILE"
echo ""
echo -e "${GREEN}🎉 Setup complete! Your HRSN FHIR server is ready for deployment.${NC}"