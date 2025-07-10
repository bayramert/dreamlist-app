pipeline {
    agent any

    environment {
        DOCKER_IMAGE_NAME = "10.77.3.24/library/dreamlist-app"
        DOCKER_REGISTRY = "10.77.3.24"
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
                    sh 'docker build -t $DOCKER_IMAGE_NAME:latest .'
                }
            }
        }

        stage('Push to Harbor') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'harbor-creds', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')
                ]) {
                    sh 'docker login $DOCKER_REGISTRY -u $DOCKER_USERNAME -p $DOCKER_PASSWORD'
                    sh 'docker push $DOCKER_IMAGE_NAME:latest'
                }
            }
        }
    }
}
