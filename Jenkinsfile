pipeline {
    agent any
    // options { cleanWs() } satırını burdan SİLDİK
    environment {
        DOCKER_IMAGE_NAME = 'bayramert/dreamlist-app'
        K8S_DEPLOYMENT_NAME = 'dreamlist-app-deployment'
        KUBECONFIG_PATH = '/home/ubuntu/.kube/config'
    }
    stages {
        stage('Checkout') {
            steps {
                script {
                    // Çalışma dizinini manuel olarak temizle
                    sh 'rm -rf *' // Bu satırı ekleyin

                    // Jenkins'in Git deposunu klonlaması için SSH anahtarını kullan
                    withCredentials([sshUserPrivateKey(credentialsId: 'github-jenkins-ssh-key', keyFileVariable: 'SSH_KEY_FILE')]) {
                        sh 'git config --global core.sshCommand "ssh -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=no"'
                        sh "git clone git@github.com:bayramert/dreamlist-app.git ."
                    }
                }
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ."
                    sh "docker tag ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }
        stage('Push Docker Image') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh "echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin"
                        sh "docker push ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                        sh "docker push ${DOCKER_IMAGE_NAME}:latest"
                    }
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    sh "kubectl --kubeconfig ${KUBECONFIG_PATH} set image deployment/${K8S_DEPLOYMENT_NAME} flask-app=${DOCKER_IMAGE_NAME}:latest"
                    sh "kubectl --kubeconfig ${KUBECONFIG_PATH} rollout status deployment/${K8S_DEPLOYMENT_NAME}"
                }
            }
        }
    }
}