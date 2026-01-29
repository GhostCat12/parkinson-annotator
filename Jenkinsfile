// Jenkinsfile
// Language: Groovy (Declarative Pipeline)
// This file defines a CI pipeline using Jenkins, for the Parkinson's Annotator project.
// This pipeline checks the repository, sets up a Conda environment, installs the package, and runs tests using pytest.
// Adapted from a sample Jenkinsfile, available at:
// https://github.com/Peter-J-Freeman/SeqKitSTP2025/blob/add_jenkins/Jenkinsfile

pipeline {
    agent any

    environment {
        CONDA_PREFIX = sh(script: 'conda info --base 2>/dev/null || echo /opt/miniconda3', returnStdout: true).trim() // Path to Conda installation
        CONDA_ENV_NAME = 'parkinsons-env'  // Name of the Conda environment to create
        PIP_DISABLE_PIP_VERSION_CHECK = '1'  // Disable pip version check warnings
        PYTHONUNBUFFERED = '1'  // Ensure real-time, unbuffered output from Python 
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm  // Get the source code from the Git repository
            }
        }
        stage('Setup Conda Environment') {
            steps {
                // Remove any existing environment with the same name, and create a new one from environment.yml
                sh '''
                . ${CONDA_PREFIX}/etc/profile.d/conda.sh
                conda env remove -n ${CONDA_ENV_NAME} || true
                conda env create -f environment.yml
                '''
            }
        }
        stage('Install Package') {
            steps {
                // Activate environment (install is handled by environment.yml)
                sh '''
                . ${CONDA_PREFIX}/etc/profile.d/conda.sh
                conda activate ${CONDA_ENV_NAME}
                '''
            }
        }
        stage('Run Tests') {
            steps {
                // Run the test suite using pytest with coverage
                sh '''
                . ${CONDA_PREFIX}/etc/profile.d/conda.sh
                conda activate ${CONDA_ENV_NAME}
                pytest --cov=parkinsons_annotator tests/
                '''
            }
        }
    }
    
    post {
        always {
            echo 'CI pipeline finished.'  // Displays this message whether the pipeline succeeds or fails
        }
    }
}
