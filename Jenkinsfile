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
    
    // 🚀 यहाँ से मुख्य STAGES ब्लॉक शुरू होता है (पूरी स्क्रिप्ट में केवल यही एक रहेगा)
    stages {
        
        // Stage 1: सबसे पहले पुराना कचरा और कैश साफ़ होगा
        stage('Clean Workspace') {
            steps {
                cleanWs() 
            }
        } 

        // Stage 2: गिटहब से नया कोड क्लोन होगा
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

        // Stage 3: वर्चुअल एनवायरनमेंट सेटअप और डिपेंडेंसी इंस्टॉल होगी
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

        // Stage 4: डॉकर इमेज बिल्ड होगी और एडब्ल्यूएस ECR पर पुश होगी
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
                            
                            // विंडोज कैश को बायपास करने के लिए क्रेडेंशियल्स को जबरन सेट किया गया है
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

        // Stage 5: SSH Agent के द्वारा कोड सीधे आपके EC2 इंस्टेंस पर लाइव होगा
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
                            
                            // SSH के जरिए विंडोज होस्ट से सीधे आपके Ubuntu EC2 के अंदर कमांड्स निष्पादित होंगी
                            bat """
                            ssh -o StrictHostKeyChecking=no ubuntu@%EC2_IP% "
                                # 1. EC2 के भीतर AWS क्रेडेंशियल्स एक्सपोर्ट करें ताकि इमेज पुल की जा सके
                                export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
                                export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
                                
                                aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                                
                                # 2. पोर्ट क्लैश से बचने के लिए पुराने कंटेनर को रोकें और हटाएं
                                docker stop %IMAGE_NAME% || true
                                docker rm %IMAGE_NAME% || true
                                
                                # 3. ECR से एकदम ताज़ा इमेज डाउनलोड करें
                                docker pull ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/%IMAGE_NAME%:%IMAGE_TAG%
                                
                                # 4. नया कंटेनर पोर्ट 80 पर बैकग्राउंड में चलाएं
                                docker run -d --name %IMAGE_NAME% -p 80:80 ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/%IMAGE_NAME%:%IMAGE_TAG%
                            "
                            """
                        }
                    }
                }
            }
        }
    } // 🚀 यहाँ मुख्य STAGES ब्लॉक सही ढंग से बंद होता है
}