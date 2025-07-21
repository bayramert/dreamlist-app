pipeline {
    agent any

    environment {
        DOCKER_IMAGE_NAME = "bayramert/dreamlist-app"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:latest ."
                }
            }
        }

        // Harbor login ve push kaldırıldı

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    sh "kubectl set image deployment/dreamlist-app-deployment flask-app=${DOCKER_IMAGE_NAME}:latest -n default"
                }
            }
        }
    }
}
