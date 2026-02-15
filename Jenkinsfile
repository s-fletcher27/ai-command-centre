pipeline {
    agent any 

    stages {
        stage('Fetch from GitHub') {
            steps {
                // This pulls the latest code from your repo into the Jenkins workspace
                checkout scm
            }
        }

        stage('Deploy to Home Directory') {
            steps {
                script {
                    // Copy the file from the workspace to the target path
                    // We use 'sudo' to ensure we have permission to write to /home/pi/
                    sh 'sudo cp mission_control.py /home/pi/mission_control.py'
                    
                    // Ensure the file is executable
                    sh 'sudo chmod +x /home/pi/mission_control.py'
                }
            }
        }
    }

    post {
        success {
            echo "Successfully deployed mission_control.py to /home/pi/"
        }
    }
}