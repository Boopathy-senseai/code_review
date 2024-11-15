from django.test import TestCase

# Create your tests here.
import requests

x = requests.get('https://sonarcloud.io/project/key?id=Boopathy-senseai_codeguru_development')

print(x.status_code)
name: SonarCloud Analysis

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  sonarcloud:
    runs-on: ubuntu-latest
    steps:
      # Step 1: Checkout code
      - name: Checkout code
        uses: actions/checkout@v3

      # Step 2: Set up JDK 17
      - name: Set up JDK 17
        uses: actions/setup-java@v2
        with:
          java-version: '17'
          distribution: 'temurin'

      # Step 3: SonarCloud Scan using SonarSource Action
      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@v1
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        with:
          args: |
            -Dsonar.projectKey=Boopathy-senseai_codeguru_development
            -Dsonar.organization=boopathy-senseai
            -Dsonar.host.url=https://sonarcloud.io
            -Dsonar.sources=.
