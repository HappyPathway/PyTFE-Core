pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'python3 setup.py sdist bdist_wheel'
      }
    }
    stage('Publish') {
      parallel {
        stage('Publish') {
          steps {
            archiveArtifacts(artifacts: 'dist/*.tar.gz', onlyIfSuccessful: true)
          }
        }
        stage('PyPi Publish') {
          steps {
            sh 'twine upload dist/* || echo'
          }
        }
      }
    }
    stage('CleanUp') {
      steps {
        cleanWs(cleanWhenAborted: true, cleanWhenFailure: true, cleanWhenNotBuilt: true, cleanWhenSuccess: true, cleanWhenUnstable: true, cleanupMatrixParent: true, deleteDirs: true)
      }
    }
  }
}