pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Pulls your code from GitHub
                checkout scm
            }
        }

        stage('Deploy to Pi Home') {
            steps {
                script {
                    echo "Copying mission_control.py to /home/pi/..."
                    
                    // Note: No 'sudo' is used here because Jenkins 
                    // is running inside the Docker container.
                    sh 'cp mission_control.py /home/pi/mission_control.py'
                    
                    // Make it executable just in case
                    sh 'chmod +x /home/pi/mission_control.py'
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    // This checks the timestamp of the file in the destination 
                    // to prove it was actually updated.
                    echo "Verifying file status at /home/pi/mission_control.py:"
                    sh 'ls -lh /home/pi/mission_control.py'
                }
            }
        }
    }

    post {
        success {
            echo '✅ Mission Control deployed successfully!'
        }
        failure {
            echo '❌ Deployment failed. Check the console logs above for errors.'
        }
    }
}