pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'python2.7 setup.py sdist bdist_wheel'
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
  }
}