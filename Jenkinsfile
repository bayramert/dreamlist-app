pipeline {
    agent any

    environment {
        DOCKER_IMAGE_NAME = "10.77.3.24:80/library/dreamlist-app"
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

        stage('Login to Harbor') {
            steps {
                withCredentials([string(credentialsId: 'harbor-password', variable: 'DOCKER_PASSWORD')]) {
                    sh "docker login 10.77.3.24:80 -u admin -p${DOCKER_PASSWORD}"
                }
            }
        }

        stage('Push Image') {
            steps {
                sh "docker push ${DOCKER_IMAGE_NAME}:latest"
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    sh "kubectl set image deployment/dreamlist-app-deployment flask-app=${DOCKER_IMAGE_NAME}:latest -n default"
                }
            }
        }
    }
}
