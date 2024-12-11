#!/bin/bash
set -eo pipefail

Help() {
  echo "Script to deploy image tags to flux"
  echo 
  echo "Syntax: ./.github/scripts/deploy_image_tag.sh [-e|s|t|l|u|p|h]"
  echo "options:"
  echo "c      Commit directly to the flux repo"
  echo "e      Environment of service to deploy"
  echo "s      Service to deploy"
  echo "t      Image tag for service"
  echo "u      Github Username"
  echo "p      Github Personal Access Token"
  echo "l      Local directory for modifying flux locally"
  echo "h      Print this help"
}

pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

while getopts ":c:e:s:t:u:p:l:h:" flag;
do
  case $flag in
    c) COMMIT_DIRECTLY=${OPTARG};;
    e) ENVIRONMENT=${OPTARG};;
    s) SERVICE=${OPTARG};;
    t) TAG=${OPTARG};;
    u) GITHUB_USERNAME=${OPTARG};; 
    p) GITHUB_PERSONAL_ACCESS_TOKEN=${OPTARG};;
    l) LOCAL_DIR=${OPTARG};;
    h) 
      Help
      exit;;
  esac
done

if [ -z "$ENVIRONMENT" ]; then
  echo "environment must be set"
  exit 1
fi

if [ -z "$SERVICE" ]; then 
  echo "service must be set"
  exit 1
fi

if [ -z "$TAG" ]; then 
  echo "tag must be set"
  exit 1
fi

TESTAPP_COMMIT_EMAIL=$(git log -1 --pretty=format:'%ae' $TAG)
TESTAPP_COMMIT_NAME=$(git log -1 --pretty=format:'%an' $TAG)
TESTAPP_COMMIT_MESSAGE=$(git log -n 1 --pretty=format:'%s' $TAG)

# NOTE: using testapp commit infor for this commit email as well
COMMIT_EMAIL=$(git log -1 --pretty=format:'%ae' $TAG)
COMMIT_NAME="test-bot"
COMMIT_MESSAGE=$(cat <<-END
($ENVIRONMENT, $SERVICE) $TESTAPP_COMMIT_MESSAGE

Commit authored by: $TESTAPP_COMMIT_NAME ($TESTAPP_COMMIT_EMAIL)
END
)

UpdateFluxTag() {
  pushd .
  cd apps/$ENVIRONMENT/$SERVICE/
  sed -i.bak "s/local tag = .*/local tag = '$TAG';/" values.jsonnet
  rm values.jsonnet.bak
  popd
  render render.yaml -s service-base
}

GitWorkflowCommitDirectly() {
  # NOTE: commits directly to flux repo
  git config user.name "$COMMIT_NAME"
  git config user.email "$COMMIT_EMAIL"
  
  # Review changes
  git --no-pager diff

  # Add and commit changes
  git add .
  git commit -m "$COMMIT_MESSAGE"

  # Push changes
  git push
  # don't want PAT lingering on the disk after we use it
  echo > .git/config
}

GitWorkflowMakePullRequest() {
  # NOTE: creates PR to flux repo

  # Configure git credentials
  git config user.name "$COMMIT_NAME"
  git config user.email "$COMMIT_EMAIL"
  
  # Create a new branch for the changes
  BRANCH_NAME="deploy-$TAG-$(date +%Y%m%d%H%M%S)"  # Creating a unique branch name using current timestamp
  git checkout -b "$BRANCH_NAME"

  # Review changes
  git --no-pager diff

  # Add and commit changes
  git add .
  git commit -m "$COMMIT_MESSAGE"

  # Push changes
  git push -u origin "$BRANCH_NAME"

  # Create pull request
  gh pr create --title "Deploying $TAG to ($ENVIRONMENT, $SERVICE)" --body "$TESTAPP_COMMIT_MESSAGE" --base main --head "$BRANCH_NAME"

  # don't want PAT lingering on the disk after we use it
  echo > .git/config
}

pushd .

if [ -z "$LOCAL_DIR" ]; then 
  if [ -z "$GITHUB_USERNAME" ]; then
    echo "github username must be set"
    exit 1
  fi

  if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
    echo "github personal access token must be set"
    exit 1
  fi

  ENCODED_GITHUB_USERNAME=$(echo -n $GITHUB_USERNAME | jq -sRr @uri)
  ENCODED_GITHUB_PERSONAL_ACCESS_TOKEN=$(echo -n $GITHUB_PERSONAL_ACCESS_TOKEN | jq -sRr @uri)
  FLUX_REPO_LINK=https://$ENCODED_GITHUB_USERNAME:$ENCODED_GITHUB_PERSONAL_ACCESS_TOKEN@github.com/danmurphy1217/flux-gitops.git

  WORKDIR=$(mktemp -d)
  pushd .
  echo $WORKDIR
  cd $WORKDIR
  git clone $FLUX_REPO_LINK
  cd flux-gitops
  UpdateFluxTag
  if [ "$COMMIT_DIRECTLY" = "true" ]; then
    GitWorkflowCommitDirectly
  else
    GitWorkflowMakePullRequest
  fi
  popd
else
  pushd .
  cd $LOCAL_DIR
  UpdateFluxTag
  popd
fi

popd
