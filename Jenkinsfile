pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'python3 setup.py sdist bdist_wheel'
      }
    }
    stage('Test') {
      steps {
        sh '''#!/bin/bash
source ~/vault.sh
packer build docker.json'''
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
        stage("Publish to Github") {
          steps {
            sh '''
            source ~/vault.sh
            github_data=$(python3 scripts/github_token.py)
            GITHUB_TOKEN=$(echo ${github_data | jq .data.personal_access_token})
            GITHUB_USER=$(echo ${github_data | jq .data.username})
            VERSION=$(cat version.txt) 
            ghr -t ${GITHUB_TOKEN} -u ${GITHUB_USER} -r ${GITHUB_REPO_NAME} -c ${GIT_COMMIT} -delete ${VERSION} .
            '''
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
  environment {
    GITHUB_REPO_NAME = 'PyTFE-Code'
  }
}