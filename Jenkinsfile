pipeline {
    agent any 

    environment { 
        VENV_DIR = 'venv'
        AWS_ACCOUNT_ID = '672755423000'
        AWS_REGION = 'us-east-1'
        IMAGE_NAME = 'ml_project'
        IMAGE_TAG = 'latest'
        EC2_IP = '100.53.213.126'
        
        // 🚀 अगर आपकी मशीन पर Python का वर्ज़न अलग है, तो यहाँ पाथ बदल लें (Double Slash \\ लगाना ज़रूरी है)
       PYTHON_EXE = 'C:\\Users\\Abhishek\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'
    } 
    
    stages {
        // Stage 1: पुराना बिल्ड कैश और कचरा साफ़ करना
        stage('Clean Workspace') {
            steps {
                cleanWs() 
            }
        } 

        // Stage 2: गिटहब से फ्रेश कोड क्लोन करना
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

        // Stage 3: वर्चुअल एनवायरनमेंट बनाना और डिपेंडेंसी इंस्टॉल करना
        stage('Setting up Virtual Environment and Installing dependencies') {
            steps {
                script {
                    echo 'Installing dependencies............'
                    bat """
                    "${PYTHON_EXE}" -m venv ${VENV_DIR}
                    ${VENV_DIR}\\Scripts\\python.exe -m pip install --upgrade pip
                    ${VENV_DIR}\\Scripts\\pip.exe install -e .
                    """
                }
            }
        }

        // Stage 4: डॉकर इमेज बिल्ड करना और AWS ECR पर पुश करना
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
                            
                            // विंडोज एनवायरनमेंट वेरिएबल्स के कैश को बायपास करने के लिए
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

        // Stage 5: SSH Agent के ज़रिए इमेज को सीधे EC2 इंस्टेंस पर रन करना
        stage('Deploy to AWS EC2 Instance') {
            steps {
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
                            
                            // SSH कनेक्शन के ज़रिए विंडोज होस्ट से Ubuntu EC2 सर्वर के अंदर कमांड्स एक्जीक्यूट होंगी
                            bat """
                            ssh -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "
                                # 1. EC2 के अंदर क्रेडेंशियल्स सेट करें ताकि वो ECR से इमेज डाउनलोड कर सके
                                export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
                                export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
                                
                                aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                                
                                # 2. अगर पुराना पुराना कंटेनर चल रहा है तो उसे रोकें और डिलीट करें
                                docker stop %IMAGE_NAME% || true
                                docker rm %IMAGE_NAME% || true
                                
                                # 3. ECR से ताज़ा इमेज पुल (Pull) करें
                                docker pull ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/%IMAGE_NAME%:%IMAGE_TAG%
                                
                                # 4. नया कंटेनर पोर्ट 80 पर लाइव करें
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