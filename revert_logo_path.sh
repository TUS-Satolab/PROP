#!/bin/bash

# Function to revert logo path
revert_logo_path() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' 's|src="/bioinformatics/prop/assets/canal_logo.svg"|src="/assets/canal_logo.svg"|g' frontend/src/app/header/header.component.html
    else
        sed -i 's|src="/bioinformatics/prop/assets/canal_logo.svg"|src="/assets/canal_logo.svg"|g' frontend/src/app/header/header.component.html
    fi
    echo "Reverted logo path change."
}

revert_logo_path
