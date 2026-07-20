pipeline {
    agent any 

    environment { 
        VENV_DIR = 'venv'
        AWS_ACCOUNT_ID = '672755423000'
        AWS_REGION = 'us-east-1'
        IMAGE_NAME = 'ml_project'
        IMAGE_TAG = 'latest'
        EC2_IP = '100.53.213.126'
    } 
    
    stages {
        stage('Cloning Github repo to Jenkins') {
            steps {
                script {
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(
                        branches: [[name: '*/main']],
                        extensions: [],
                        userRemoteConfigs: [[
                            credentialsId: 'token-github',
                            url: 'https://github.com/Abhishekla311/MLOPS-COURSE-PROJECT.git'
                        ]]
                    )
                }
            }
        }

        stage('Setting up Virtual Environment and Installing dependencies') {
            steps {
                script {
                    echo 'Installing dependencies............'
                    bat """
                    python -m venv ${VENV_DIR}
                    ${VENV_DIR}\\Scripts\\python.exe -m pip install --upgrade pip
                    ${VENV_DIR}\\Scripts\\pip.exe install -e .
                    """
                }
            }
        }

        stage('Building and Pushing Docker Image to ECR') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-credentials',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {
                    withEnv(["AWS_DEFAULT_REGION=${AWS_REGION}"]) {
                        script {
                           echo 'Building and pushing Docker image............'
                            bat """
                            aws ecr get-login-password --region %AWS_DEFAULT_REGION% | docker login --username AWS --password-stdin %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_DEFAULT_REGION%.amazonaws.com
                            
                            rem ⏱️ विंडोज शेल को लॉगिन टोकन रजिस्टर करने के लिए 2 सेकंड का समय दें
                            timeout /t 2 /nobreak
                            
                            docker build -t %IMAGE_NAME%:%IMAGE_TAG% .
                            docker tag %IMAGE_NAME%:%IMAGE_TAG% %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_DEFAULT_REGION%.amazonaws.com/%IMAGE_NAME%:%IMAGE_TAG%
                            docker push %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_DEFAULT_REGION%.amazonaws.com/%IMAGE_NAME%:%IMAGE_TAG%
                            """
                        }
                    }
                }
            }
        }

        // 🚀 यहाँ बदलाव किया गया है: App Runner की जगह अब यह सीधे EC2 पर डिप्लॉय करेगा
        stage('Building and Pushing Docker Image to ECR') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-credentials',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {
                    withEnv(["AWS_DEFAULT_REGION=${AWS_REGION}"]) {
                        script {
                            echo 'Building and pushing Docker image............'
                            
                            // 🚀 यहाँ बदलाव किया गया है: विंडोज शेल में सीधे क्रेडेंशियल्स को 'set' किया गया है 
                            // ताकि AWS CLI बिल्कुल फ्रेश क्रेडेंशियल्स का उपयोग करे
                            bat """
                            set AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID%
                            set AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY%
                            set AWS_DEFAULT_REGION=%AWS_DEFAULT_REGION%
                            
                            aws ecr get-login-password --region %AWS_DEFAULT_REGION% | docker login --username AWS --password-stdin %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_DEFAULT_REGION%.amazonaws.com
                            
                            timeout /t 3 /nobreak
                            
                            docker build -t %IMAGE_NAME%:%IMAGE_TAG% .
                            docker tag %IMAGE_NAME%:%IMAGE_TAG% %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_DEFAULT_REGION%.amazonaws.com/%IMAGE_NAME%:%IMAGE_TAG%
                            docker push %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_DEFAULT_REGION%.amazonaws.com/%IMAGE_NAME%:%IMAGE_TAG%
                            """
                        }
                    }
                }
            }
        }
    }
}