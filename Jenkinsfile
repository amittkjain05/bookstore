// Jenkinsfile
// ============================================================
// Jenkins CI/CD Pipeline — BookStore API Tests
// ============================================================
// Jenkins is FREE and open-source. Run it locally via Docker:
//   docker run -p 8080:8080 jenkins/jenkins:lts
//
// Place this file at the ROOT of your project as: Jenkinsfile

pipeline {

    agent any   // run on any available Jenkins agent

    environment {
        PYTHON_VERSION = '3.11'
        REPORTS_DIR    = 'reports'
    }

    // Trigger on every push (when using Jenkins + GitHub webhook)
    triggers {
        githubPush()
    }

    stages {

        // ── Stage 1: Checkout ─────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Checking out source code...'
                checkout scm
            }
        }

        // ── Stage 2: Setup Python environment ─────────────
        stage('Setup Environment') {
            steps {
                echo '🐍 Setting up Python environment...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        // ── Stage 3: Lint ─────────────────────────────────
        stage('Lint') {
            steps {
                echo '🔍 Running flake8 linter...'
                sh '''
                    . venv/bin/activate
                    flake8 app.py test_api.py --max-line-length=120
                '''
            }
        }

        // ── Stage 4: Start server + Run tests ─────────────
        stage('Run Tests') {
            steps {
                echo '🚀 Starting Flask server...'
                sh '''
                    . venv/bin/activate
                    mkdir -p ${REPORTS_DIR}
                    python app.py &
                    sleep 3
                    echo "Server started. Running tests..."
                    pytest test_api.py -v \
                        --tb=short \
                        --junitxml=${REPORTS_DIR}/results.xml \
                        --cov=app \
                        --cov-report=xml:${REPORTS_DIR}/coverage.xml \
                        --cov-report=term-missing
                '''
            }
            post {
                always {
                    // Publish JUnit test results in Jenkins UI
                    junit "${REPORTS_DIR}/results.xml"
                }
            }
        }

        // ── Stage 5: Coverage report ───────────────────────
        stage('Coverage Report') {
            steps {
                echo '📊 Publishing coverage report...'
                sh '''
                    . venv/bin/activate
                    python -m coverage report
                '''
            }
        }
    }

    // ── Post-pipeline actions ──────────────────────────────
    post {
        success {
            echo '✅ Pipeline passed! All tests green.'
        }
        failure {
            echo '❌ Pipeline failed. Check test results above.'
        }
        always {
            // Archive test reports as downloadable artifacts
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            // Clean up Flask server process
            sh 'pkill -f "python app.py" || true'
        }
    }
}
