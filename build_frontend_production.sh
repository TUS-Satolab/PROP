#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the project root directory
cd "$SCRIPT_DIR"

# Function to revert logo path
revert_logo_path() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' 's|src="/bioinformatics/prop/assets/canal_logo.svg"|src="/assets/canal_logo.svg"|g' frontend/src/app/header/header.component.html
    else
        sed -i 's|src="/bioinformatics/prop/assets/canal_logo.svg"|src="/assets/canal_logo.svg"|g' frontend/src/app/header/header.component.html
    fi
    echo "Reverted logo path change."
}

# Set up trap to revert logo path on script exit
trap revert_logo_path EXIT

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found in the project root directory."
    exit 1
fi

# Read variables from .env file
source .env

# Ensure the environments directory exists
mkdir -p frontend/src/environments

# Create environment.prod.ts file
cat > frontend/src/environments/environment.prod.ts << EOL
export const environment = {
  production: true,
  apiKey: '${BACKEND_APIKEY}',
  fileSizeLimit: ${FILE_SIZE_LIMIT},
  baseUrl: '${BASE_URL}',
};
EOL

echo "environment.prod.ts file created successfully."

# Function to change logo path
change_logo_path() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' 's|src="/assets/canal_logo.svg"|src="/bioinformatics/prop/assets/canal_logo.svg"|g' frontend/src/app/header/header.component.html
    else
        sed -i 's|src="/assets/canal_logo.svg"|src="/bioinformatics/prop/assets/canal_logo.svg"|g' frontend/src/app/header/header.component.html
    fi
    echo "Changed logo path for prop build."
}

# Change logo path for prop build if the argument is provided
if [ "$1" == "prop" ]; then
    change_logo_path
fi

echo "build_frontend_production.sh completed"

cd frontend

# Run the Angular build
ng build --prod --output-path ../docs --base-href /bioinformatics/prop/

cd ..
# Note: The trap will ensure the logo path is reverted even if the build fails
