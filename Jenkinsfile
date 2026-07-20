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
        // 🚀 1. सबसे पहले पुराना पुराना कैश और कचरा साफ करने के लिए यह स्टेज यहाँ जोड़ें
        stage('Clean Workspace') {
            steps {
                cleanWs() 
            }
        } 
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
                            
                            // 🚀 विंडोज शेल (Cache Issue) को ठीक करने के लिए फ्रेश एनवायरनमेंट सेटिंग्स
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

        // 🚀 यहाँ सुधार किया गया है: डुप्लिकेट स्टेज को हटाकर वास्तविक EC2 डिप्लॉयमेंट कोड जोड़ा गया है
        stage('Deploy to AWS EC2 Instance') {
            steps {
                // आपके द्वारा Jenkins Credentials में बनाए गए 'ec2-ssh-key' का उपयोग
                sshagent(credentials: ['ec2-ssh-key']) {
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'aws-credentials',
                            usernameVariable: 'AWS_ACCESS_KEY_ID',
                            passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                        )
                    ]) {
                        script {
                            echo 'Deploying to AWS EC2 Instance (100.53.213.126)............'
                            
                            // SSH के जरिए विंडोज से सीधे आपके EC2 (Ubuntu) के अंदर कमांड्स रन होंगी
                            bat """
                            ssh -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "
                                # 1. EC2 के अंदर AWS क्रेडेंशियल्स एक्सपोर्ट करें ताकि ECR लॉगिन हो सके
                                export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
                                export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
                                
                                aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                                
                                # 2. अगर पुराना कंटेनर चल रहा हो तो उसे रोकें और हटाएं
                                docker stop %IMAGE_NAME% || true
                                docker rm %IMAGE_NAME% || true
                                
                                # 3. ECR से लेटेस्ट इमेज पुल (Pull) करें
                                docker pull ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/%IMAGE_NAME%:%IMAGE_TAG%
                                
                                # 4. नया कंटेनर चालू करें
                                docker run -d --name %IMAGE_NAME% -p 80:80 ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/%IMAGE_NAME%:%IMAGE_TAG%
                            "
                            """
                        }
                    }
                }
            }
        }
    }
}