pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
        AWS_ACCOUNT_ID = "672755423000"
        AWS_REGION = "us-east-1"
        IMAGE_NAME = "ml_project"
        IMAGE_TAG = "latest"

        ECR_REPOSITORY = "ml_project"

        EC2_HOST = "54.160.240.123"
        EC2_USER = "ubuntu"
    }

    stages {

        stage('Clone GitHub Repository') {
            steps {
                checkout scmGit(
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        credentialsId: 'token-github',
                        url: 'https://github.com/Abhishekla311/MLOPS-COURSE-PROJECT.git'
                    ]]
                )
            }
        }

        stage('Install Python Dependencies') {
            steps {
                bat """
                python -m venv %VENV_DIR%
                %VENV_DIR%\\Scripts\\python.exe -m pip install --upgrade pip
                %VENV_DIR%\\Scripts\\pip.exe install -e .
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                bat """
                docker build -t %IMAGE_NAME%:%IMAGE_TAG% .
                """
            }
        }

        stage('Push Docker Image To ECR') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-credentials',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {

                    bat """
                    set AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID%
                    set AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY%
                    set AWS_DEFAULT_REGION=%AWS_REGION%

                    aws ecr get-login-password --region %AWS_REGION% | docker login --username AWS --password-stdin %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com

                    docker tag %IMAGE_NAME%:%IMAGE_TAG% %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com/%ECR_REPOSITORY%:%IMAGE_TAG%

                    docker push %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com/%ECR_REPOSITORY%:%IMAGE_TAG%
                    """
                }
            }
        }

        stage('Deploy To EC2') {

            steps {

                sshagent(credentials: ['ec2-key']) {

                    bat """
                    ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% ^
                    "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 672755423000.dkr.ecr.us-east-1.amazonaws.com && \
                    docker pull 672755423000.dkr.ecr.us-east-1.amazonaws.com/ml_project:latest && \
                    docker stop ml_project || true && \
                    docker rm ml_project || true && \
                    docker run -d --restart always --name ml_project -p 5000:5000 672755423000.dkr.ecr.us-east-1.amazonaws.com/ml_project:latest"
                    """

                }

            }

        }

    }

}