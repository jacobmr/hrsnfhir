#!/bin/bash
# Azure deployment setup script using FREE tier for HRSN FHIR Processing Server

# Configuration
RESOURCE_GROUP="rg-hrsn-fhir-jmr"
APP_SERVICE_PLAN="asp-hrsn-fhir-jmr"
WEBAPP_NAME="hrsn-fhir-jmr-2024"
LOCATION="West US"
SKU="F1"  # Free tier

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Azure deployment setup (FREE TIER) for HRSN FHIR Processing Server${NC}"
echo "=================================================="

# Create App Service Plan with FREE tier
echo -e "${YELLOW}⚙️ Creating App Service Plan (FREE): $APP_SERVICE_PLAN${NC}"
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

# Generate secure keys
SECRET_KEY=$(openssl rand -base64 32)
API_KEY=$(openssl rand -base64 24)

# Configure app settings (without database for now)
echo -e "${YELLOW}⚙️ Configuring application settings...${NC}"
az webapp config appsettings set \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
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
echo "App Service: $WEBAPP_NAME (FREE TIER)"
echo "App URL: https://$WEBAPP_NAME.azurewebsites.net"
echo ""
echo -e "${YELLOW}🔧 Next Steps:${NC}"
echo "1. Add the publish profile to GitHub Secrets as 'AZUREAPPSERVICE_PUBLISHPROFILE'"
echo "2. Update the workflow file with your app name: $WEBAPP_NAME"
echo "3. Push your code to trigger the deployment"
echo "4. Access your app at: https://$WEBAPP_NAME.azurewebsites.net"
echo ""
echo -e "${YELLOW}🔑 Important Information (SAVE THIS):${NC}"
echo "API Key: $API_KEY"
echo "Secret Key: $SECRET_KEY"
echo ""
echo -e "${YELLOW}💾 Publish Profile (save this for GitHub Secrets):${NC}"
echo "$PUBLISH_PROFILE"
echo ""
echo -e "${YELLOW}📝 Note: This uses the FREE tier. To upgrade to B1 with database:${NC}"
echo "1. Request quota increase in Azure Portal"
echo "2. Run the full setup script later"
echo ""
echo -e "${GREEN}🎉 Setup complete! Your HRSN FHIR server is ready for deployment.${NC}"